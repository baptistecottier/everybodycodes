import requests
import binascii
from sys import argv
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class EverybodyCodesClient:
    def __init__(self, session_cookie: str):
        # Step 1: Prepare an HTTP Client
        self.session = requests.Session()
        # Set the 'everybody-codes' cookie matching what you see in your Profile
        self.session.cookies.set('everybody-codes', session_cookie, domain='everybody.codes')
        self.session.cookies.set('everybody-codes', session_cookie, domain='api.everybody.codes')
        self.seed = None

    def get_seed(self) -> int:
        """Step 2: Retrieve Your Seed Parameter"""
        url = "https://api.everybody.codes/user/me"
        response = self.session.get(url)
        response.raise_for_status()
        
        self.seed = response.json().get('seed')
        print(f"[*] Retrieved seed: {self.seed}")
        return self.seed

    def fetch_inputs(self, event: str, quest: str, part: str) -> dict:
        """Step 3: Fetch Your Input Notes"""
        if not self.seed:
            self.get_seed()
        if event.startswith("30"):
            url = f"https://everybody.codes/assets/{event}/{quest}/input.json"
        else:
            url = f"https://everybody.codes/assets/{event}/{quest}/input/{self.seed}.json"
        response = self.session.get(url)
        response.raise_for_status()
        print(response.json())
        print(f"[*] Fetched encrypted inputs for Event {event}, Quest {quest}")
        # Returns encoded input notes { "1": "...", "2": "...", "3": "..." }
        return response.json()

    def get_keys(self, event: str, quest: str, part: str) -> dict:
        """Step 4: Retrieve AES Keys"""
        url = f"https://api.everybody.codes/event/{event}/quest/{quest}"
        response = self.session.get(url)
        response.raise_for_status()
        
        print(f"[*] Fetched keys for Event {event}, Quest {quest}")
        # The structure of this response depends on the API, but it contains the keys
        return response.json()

    @staticmethod
    def decrypt(key: str, encrypted_hex: str) -> str:
        """Step 5: Decode the Input Note (Ported from Java/JS samples)"""
        try:
            # Prepare decryption components
            encrypted_bytes = binascii.unhexlify(encrypted_hex)
            key_bytes = key.encode('utf-8')
            iv_bytes = key[:16].encode('utf-8')  # IV is the first 16 bytes of the key
            
            # Setup AES Cipher (AES/CBC/PKCS5Padding)
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            
            # Perform decryption and unpad
            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"[!] Decryption failed: {e}")
            return None

    def submit_answer(self, event: str, quest: str, part: str, answer: str) -> dict:
        """Step 6: Send Your Answer"""
        url = f"https://api.everybody.codes/event/{event}/quest/{quest}/part/{part}/answer"
        payload = { "answer": str(answer) }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        print(f"[*] Submitted answer for Part {part}: {answer}")
        return response.json()

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # 1. Grab your session cookie from your browser dev tools
    SESSION_COOKIE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjA1Mywic2VlZCI6NDEsImJhZGdlcyI6IiwxLDIsMywyMDI0LDIwMjUsMjAyNiwzMDAxLCIsInR5cGUiOiIwIiwiaWF0IjoxNzgwNTAyMjk3LCJleHAiOjE3ODExMDcwOTd9.X7fza5I2yffQ9GCtzboc8Te4Do72BIRt-iIzuc_YGTs"
    EVENT_YEAR = argv[1]
    QUEST_NUM = argv[2]
    PART = argv[3]
    
    # Initialize Client
    client = EverybodyCodesClient(SESSION_COOKIE)
    
    try:
        # Fetch inputs
        encrypted_inputs = client.fetch_inputs(EVENT_YEAR, QUEST_NUM, PART)
        
        # Fetch keys for the parts you have access to
        quest_data = client.get_keys(EVENT_YEAR, QUEST_NUM, PART)
        
        # Assuming quest_data gives you a key for Part 1 (adjust based on actual API response)
        # Note: You'll need to parse the specific key location from quest_data JSON
        key = quest_data[f"key{PART}"] 
        
        if "1" in encrypted_inputs:
            # Decrypt Part 1 input
            decrypted_text = client.decrypt(key, encrypted_inputs[PART])
            print(f"Decrypted Input for Part 1:\n{decrypted_text}\n")
            
            # ... Write your logic to solve the puzzle here ...
            my_solution = "42" 
            
            # Submit Answer
            # result = client.submit_answer(EVENT_YEAR, QUEST_NUM, PART, "1", my_solution)
            # print(result)
            
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")