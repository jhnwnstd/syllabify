#!/usr/bin/env python3

import sys
import random
import nltk
from pathlib import Path
import importlib.util
from typing import List

# Constants
DEFAULT_WORD_COUNT = 10

def import_module(module_name: str, module_path: Path):
    """
    Dynamically imports a module given its name and file path.

    Args:
        module_name (str): The name to assign to the module.
        module_path (Path): The file path to the module.

    Returns:
        module: The imported module object.
    """
    if not module_path.is_file():
        print(f"Error: {module_name}.py not found in the current directory.")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        print(f"Error: Could not load specification for {module_name}.")
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        sys.exit(1)

    return module

def get_random_words(cmu_dict: dict, count: int = DEFAULT_WORD_COUNT) -> List[str]:
    """
    Selects a random set of unique words from the CMU Pronouncing Dictionary.

    Args:
        cmu_dict (dict): The CMU Pronouncing Dictionary.
        count (int): Number of unique words to select.

    Returns:
        List[str]: A list of randomly selected words.
    """
    words = list(cmu_dict.keys())
    if count > len(words):
        raise ValueError("Requested number of words exceeds the total available in the dictionary.")
    return random.sample(words, count)

def test_syllabify(syllabify_module, wcm_module, word_list: List[str]):
    """
    Tests the syllabification and computes the Word Complexity Measure (WCM) for each word.

    Args:
        syllabify_module (module): The imported syllabify module.
        wcm_module (module): The imported wcm module.
        word_list (List[str]): List of words to test syllabification.
    """
    for word in word_list:
        lower_word = word.lower()
        if lower_word in cmu_dict:
            # Get the ARPABET pronunciation(s) for the word
            pronunciations = cmu_dict[lower_word]
            for pron in pronunciations:
                print(f"Word: {word}")
                print(f"Pronunciation: {pron}")

                try:
                    # Syllabify the pronunciation using the syllabify function
                    syllables = syllabify_module.syllabify(pron)

                    # Pretty-print the syllabified output
                    syllabified_str = syllabify_module.pretty_print(syllables)
                    print("Syllabification:")
                    print(syllabified_str)

                    # Compute the Word Complexity Measure using wcm function
                    complexity_score = wcm_module.wcm(pron)
                    print(f"Word Complexity Measure (WCM): {complexity_score}")

                except ValueError as ve:
                    print(f"Error: {ve}")

                print("-" * 40)
        else:
            print(f"Word: {word} not found in CMU dictionary.")
            print("-" * 40)

def main():
    # Define paths for syllabify.py and wcm.py
    syllabify_path = Path('./syllabify.py')
    wcm_path = Path('./wcm.py')

    # Import the syllabify and wcm modules
    syllabify_module = import_module("syllabify", syllabify_path)
    wcm_module = import_module("wcm", wcm_path)

    # Download the CMU Pronouncing Dictionary from NLTK if it's not already downloaded
    nltk.download('cmudict', quiet=True)

    # Load the CMU Pronouncing Dictionary
    global cmu_dict
    cmu_dict = nltk.corpus.cmudict.dict()

    try:
        # Select ten random unique words from the CMU dictionary
        words_to_test = get_random_words(cmu_dict, DEFAULT_WORD_COUNT)
    except ValueError as ve:
        print(f"Error selecting words: {ve}")
        sys.exit(1)

    # Test the syllabification and compute WCM for the selected words
    test_syllabify(syllabify_module, wcm_module, words_to_test)

if __name__ == '__main__':
    main()