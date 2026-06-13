# Everybody Codes - Puzzle Solutions for GridOS challenges

The tables shows best stats _individually_, not for a single set of rules.
<br>Each part `i` of quest `j` contains four files; one optimizing each ranking criterion.
- number of read heads: `qjpi_heads.rules`
- total number of states encountered: `qjpi_states.rules`
- total number of rules used: `qjpi_rules.rules`
- total number of steps required: `qjpi_steps.rules`.

By default, the `steps` criterion is used by the runner, but you can specify the one to use with the `-c` parameter. For example, to run the `2`nd part of the `3`rd quest of the `1` st GridOS event using the `heads` optimised rules:
```
uv run ec.py 3001 3 2 -c heads
```

### GridOS Tournament [No. 1] 🏰

| Quest                         | Part                  | _#Heads_      | _#States_              | _#Rules_               | _#Steps_                |
|-                              |------:                |:-----------:|:--------------------:|:--------------------:|:---------------------:|
|1. The Battle for the Farmlands| I ✅<br>II ✅<br>III ✅| 1<br>1<br>2 | 200<br>200<br>592    | 484<br>668<br>2824   | 2620<br>2717<br>35730 |
|2. The Runes of Power          | I ✅<br>II ✅<br>III ✅| 2<br>2<br>4 | 200<br>200<br>200    | 578<br>834<br>1351   | 2527<br>11409<br>11318|
|3. Mining Maestro              | I ✅<br>II ✅<br>III ✅| 2<br>7<br>8 | 200<br>200<br>789    | 879<br>852<br>3549   | 4681<br>4568<br>54390 |
|4. Royal Smith's Puzzle        | I ✅<br>II ✅<br>III ✅| 3<br>2<br>3 | 400<br>798<br>1086    | 441<br>1699<br>2691   | 1000<br>39974<br>40978 |
|5. Pseudo-Random Clap Dance    | I ✅<br>II ✅<br>III ✅| 4<br>4<br>4 | 200<br>900<br>1900    | 700<br>2095<br>4431   | 2685<br>5474<br>7278 |