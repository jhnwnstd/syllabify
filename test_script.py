import sys
import random
import nltk
from pathlib import Path
import importlib.util
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Constants
DEFAULT_WORD_COUNT = 10
SYLLABIFY_MODULE_NAME = "syllabify"
WCM_MODULE_NAME = "wcm"
SYLLABIFY_FILE = "syllabify.py"
WCM_FILE = "wcm.py"

# List of unsyllabifiable words still found in the CMU Pronouncing Dictionary
UNSYLLABIFIABLE_WORDS = {'fs', 'mmmm', 'shh', 'ths'}


def import_module(module_name: str, module_path: Path):
    """
    Dynamically imports a module given its name and file path.

    Args:
        module_name (str): The name to assign to the module.
        module_path (Path): The file path to the module.

    Returns:
        module: The imported module object.

    Raises:
        SystemExit: If the module file is not found or cannot be imported.
    """
    if not module_path.is_file():
        logging.error(f"{module_name}.py not found in the current directory ({module_path}).")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        logging.error(f"Could not load specification for {module_name}.")
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore
        logging.info(f"Successfully imported module: {module_name}")
    except Exception as e:
        logging.error(f"Error importing {module_name}: {e}")
        sys.exit(1)

    return module


def get_random_words(cmu_dict: dict, count: int = DEFAULT_WORD_COUNT) -> List[str]:
    """
    Selects a random set of unique words from the CMU Pronouncing Dictionary,
    excluding unsyllabifiable words.

    Args:
        cmu_dict (dict): The CMU Pronouncing Dictionary.
        count (int): Number of unique words to select.

    Returns:
        List[str]: A list of randomly selected words.

    Raises:
        ValueError: If the requested number of words exceeds the dictionary size.
    """
    # Get all words from the CMU dictionary and exclude unsyllabifiable words
    words = [word for word in cmu_dict.keys() if word.lower() not in UNSYLLABIFIABLE_WORDS]
    
    if count > len(words):
        raise ValueError("Requested number of words exceeds the total available in the dictionary.")
    
    selected_words = random.sample(words, count)
    logging.debug(f"Selected random words: {selected_words}")
    return selected_words


def test_syllabify(syllabify_module, wcm_module, word_list: List[str], cmu_dict: dict):
    """
    Tests the syllabification and computes the Word Complexity Measure (WCM) for each word.

    Args:
        syllabify_module (module): The imported syllabify module.
        wcm_module (module): The imported wcm module.
        word_list (List[str]): List of words to test syllabification.
        cmu_dict (dict): The CMU Pronouncing Dictionary.
    """
    for word in word_list:
        lower_word = word.lower()
        if lower_word in cmu_dict:
            pronunciations = cmu_dict[lower_word]
            for pron in pronunciations:
                print(f"\nWord: {word}")
                print(f"Pronunciation: {pron}")

                try:
                    syllables = syllabify_module.syllabify(pron)
                    syllabified_str = syllabify_module.pretty_print(syllables)
                    num_syllables = len(syllables)
                    complexity_score = wcm_module.wcm(pron)

                    print(f"Number of Syllables: {num_syllables}")
                    print(f"Syllabification: {syllabified_str}")
                    print(f"Word Complexity Measure (WCM): {complexity_score}")
                except ValueError as ve:
                    print(f"Error: {ve}")
        else:
            print(f"\nWord: {word} not found in CMU dictionary.")

        print("-" * 40)


def prompt_user_choice() -> Optional[str]:
    """
    Presents an interactive menu to the user and captures their choice.

    Returns:
        Optional[str]: The user's choice ('1', '2', or '3'), or None if invalid.
    """
    print("\n=== Syllabify and Compute WCM ===")
    print("1. Test random words")
    print("2. Test a specific word")
    print("3. Exit")
    choice = input("Enter your choice (1/2/3): ").strip()
    return choice


def prompt_word_count(default: int = DEFAULT_WORD_COUNT) -> int:
    """
    Prompts the user to enter the number of random words to test.

    Args:
        default (int): The default number of words if the user provides no input.

    Returns:
        int: The number of words to test.
    """
    count_input = input(f"Enter the number of random words to test (default {default}): ").strip()
    if not count_input:
        logging.debug(f"No input provided. Using default count: {default}")
        return default
    try:
        count = int(count_input)
        if count <= 0:
            raise ValueError
        logging.debug(f"User selected word count: {count}")
        return count
    except ValueError:
        logging.warning("Invalid input for word count. Using default count.")
        return default


def prompt_specific_word() -> Optional[str]:
    """
    Prompts the user to enter a specific word to syllabify.

    Returns:
        Optional[str]: The word entered by the user, or None if no input.
    """
    word = input("Enter the word to syllabify: ").strip()
    if word.isalpha():
        logging.debug(f"User entered specific word: {word}")
        return word
    else:
        logging.warning("Invalid word entered. Please enter alphabetic characters only.")
        return None


def main():
    # Define paths for syllabify.py and wcm.py
    syllabify_path = Path(SYLLABIFY_FILE)
    wcm_path = Path(WCM_FILE)

    # Import the syllabify and wcm modules
    syllabify_module = import_module(SYLLABIFY_MODULE_NAME, syllabify_path)
    wcm_module = import_module(WCM_MODULE_NAME, wcm_path)

    # Download the CMU Pronouncing Dictionary from NLTK if it's not already downloaded
    try:
        nltk.data.find('corpora/cmudict')
        logging.info("CMU Pronouncing Dictionary already downloaded.")
    except LookupError:
        logging.info("Downloading CMU Pronouncing Dictionary...")
        nltk.download('cmudict')

    # Load the CMU Pronouncing Dictionary
    cmu_dict = nltk.corpus.cmudict.dict()
    logging.info(f"Loaded CMU Pronouncing Dictionary with {len(cmu_dict)} entries.")

    while True:
        choice = prompt_user_choice()

        if choice == '1':
            count = prompt_word_count()
            try:
                words_to_test = get_random_words(cmu_dict, count)
                test_syllabify(syllabify_module, wcm_module, words_to_test, cmu_dict)
            except ValueError as ve:
                logging.error(ve)
        elif choice == '2':
            word = prompt_specific_word()
            if word:
                test_syllabify(syllabify_module, wcm_module, [word], cmu_dict)
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            sys.exit(0)
        else:
            logging.warning("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == '__main__':
    main()