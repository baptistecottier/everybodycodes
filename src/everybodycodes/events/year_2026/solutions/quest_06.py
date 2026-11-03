"""
Event: Lord of the Wings
Quest: The Nullspiracy
"""

import re
from typing import Iterator


def preprocessing(puzzle_inputs: dict[int, str]) -> list[dict[str, set[str]]]:
    """
    Parse each input into its recipes, mapping a product to its ingredients.
    """
    return [
        {product: set(ingredients.split(','))
         for (product, ingredients) in re.findall(r'(\w+):(.+)', part_input)
         } for part_input in puzzle_inputs.values()]


def solver(recipes: list[dict[str, set[str]]]) -> Iterator[int]:
    """
    Yield the number of ingredients used to make NULL in the first notes,
    then the number of products made with at least one, and at least two,
    ingredients starting with NULL in the second and third notes.
    """
    yield len(used_ingredients(recipes[0])['NULL'])
    for part in (1, 2):
        yield sum(
            sum(ingredient.startswith('NULL') for ingredient in ingredients)
            >= part
            for ingredients in used_ingredients(recipes[part]).values()
        )


def used_ingredients(note: dict[str, set[str]]) -> dict[str, set[str]]:
    """
    Map each product of note to every ingredient used, directly or not, to
    make it.
    """
    products = set(note.keys())
    all_ingredients: dict[str, set[str]] = {}
    for product in products:
        ingredients: set[str] = set()
        add_ingredients(note, product, ingredients)
        all_ingredients[product] = ingredients
    return all_ingredients


def add_ingredients(
        recipes: dict[str, set[str]], product: str, used: set[str]
) -> None:
    """
    Add to used every ingredient used, directly or not, to make product.
    """
    if product not in recipes.keys() or recipes[product] < used:
        return

    used |= recipes[product]
    for ingredient in recipes[product]:
        add_ingredients(recipes, ingredient, used)
