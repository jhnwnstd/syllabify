# Syllabify Project

Welcome to the **Syllabify Project**! This project offers tools to syllabify words using the CMU Pronouncing Dictionary and compute their **Word Complexity Measure (WCM)**. It comprises three main Python scripts:

1. [`syllabify.py`](#syllabifypy)
2. [`wcm.py`](#wcmpy)
3. [`test_script.py`](#test_scriptpy)

Additionally, a comprehensive guide is available in [`manual.pdf`](manual.pdf).

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
  - [`syllabify.py`](#syllabifypy)
  - [`wcm.py`](#wcmpy)
  - [`test_script.py`](#test_scriptpy)
- [Usage](#usage)
  - [Syllabify a Word](#syllabify-a-word)
  - [Compute Word Complexity Measure (WCM)](#compute-word-complexity-measure-wcm)
  - [Testing the Scripts](#testing-the-scripts)
- [Example](#example)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

The **Syllabify Project** is designed to:

1. **Syllabify Words:** Break down words into their constituent syllables based on phonetic pronunciations.
2. **Compute Word Complexity Measure (WCM):** Evaluate the complexity of words using a defined metric.
3. **Test Functionality:** Validate syllabification and WCM computations using random words from the CMU Pronouncing Dictionary.

These functionalities are encapsulated within three Python scripts that work together seamlessly to provide comprehensive syllabification and complexity analysis.

---

## Prerequisites

Ensure you have the following installed:

- **Python 3.6 or higher**
- **pip** (Python package installer)
- **Virtual Environment (optional but recommended):** To manage project dependencies without affecting system-wide packages.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/jhnwnstd/syllabify.git
   cd syllabify
   ```

2. **Set Up a Virtual Environment (Optional):**

   It's good practice to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Packages:**

   ```bash
   pip install -r requirements.txt
   ```

   *If `requirements.txt` is not provided, install the necessary packages manually:*

   ```bash
   pip install nltk
   ```

4. **Download NLTK Data:**

   The scripts utilize the CMU Pronouncing Dictionary from NLTK. Download it using the following command:

   ```bash
   python -c "import nltk; nltk.download('cmudict')"
   ```

---

## Project Structure

```
syllabify/
├── __init__.py
├── __pycache__/
├── manual.pdf
├── README.md
├── syllabify.py
├── test_script.py
└── wcm.py
```

### `syllabify.py`

#### Description

Responsible for breaking down words into syllables based on their phonetic pronunciations. It employs syllabification rules, including the Alaska rule, to accurately assign phonemes to syllable onsets and codas.

#### Key Components

- **`Syllable` Dataclass:** Represents a syllable with its onset, nucleus, and coda.
- **`identify_nuclei_and_onsets` Function:** Identifies the nuclei (vowels) and onsets (initial consonant clusters) in a pronunciation.
- **`resolve_onsets_and_codas` Function:** Adjusts onsets and computes codas based on syllabification rules.
- **`syllabify` Function:** Integrates the identification and resolution steps to produce a syllabified representation of a word.
- **`pretty_print` Function:** Formats the syllabified output into a human-readable string.
- **`destress` Function:** Removes stress markers from the syllabified output for simplified analysis.

#### Dependencies

- `dataclasses` (Python 3.7+)
- `itertools`
- `typing`
- `copy`

### `wcm.py`

#### Description

Computes the **Word Complexity Measure (WCM)** for a given word based on its pronunciation. The WCM is a metric designed to evaluate the complexity of words, useful in linguistic studies, readability assessments, or language learning applications.

#### Key Components

- **`wcm` Function:** Calculates the complexity score based on syllabification and phoneme patterns.

  *Note: The specific implementation details of the WCM function are provided within this script.*

#### Dependencies

- `typing`

### `test_script.py`

#### Description

Serves as a testing utility that:

1. Randomly selects a predefined number of words from the CMU Pronouncing Dictionary.
2. Syllabifies each selected word using `syllabify.py`.
3. Computes the WCM for each word using `wcm.py`.
4. Displays the results in a structured and readable format, including the number of syllables.

#### Key Components

- **`import_module` Function:** Dynamically imports `syllabify.py` and `wcm.py` as modules.
- **`get_random_words` Function:** Selects a specified number of random words from the CMU Pronouncing Dictionary.
- **`test_syllabify` Function:** Processes each word by syllabifying and computing its WCM, then displays the results.
- **`main` Function:** Orchestrates the workflow by importing modules, selecting words, and invoking the test function.

#### Dependencies

- `sys`
- `random`
- `nltk`
- `pathlib`
- `importlib.util`
- `typing`

---

## Usage

### Syllabify a Word

Use the `syllabify` function to break down a word's pronunciation into syllables.

```python
from syllabify import syllabify, pretty_print

# Example pronunciation
pronunciation = ['K', 'R', 'IH1', 'S', 'K', 'R', 'AO2', 'S', 'IH0', 'NG']

# Syllabify the pronunciation
syllables = syllabify(pronunciation)

# Pretty-print the syllabification
syllabified_str = pretty_print(syllables)
print(syllabified_str)
```

**Output:**

```
K-R-IH1.S-K-R-AO2.S-IH0-NG
```

### Compute Word Complexity Measure (WCM)

Use the `wcm` function to compute the WCM of a word's pronunciation.

```python
from wcm import wcm

# Example pronunciation
pronunciation = ['K', 'R', 'IH1', 'S', 'K', 'R', 'AO2', 'S', 'IH0', 'NG']

# Compute WCM
complexity_score = wcm(pronunciation)
print(f"Word Complexity Measure (WCM): {complexity_score}")
```

**Output:**

```
Word Complexity Measure (WCM): 5
```

*Note: The actual WCM value depends on the implementation within `wcm.py`.*

### Testing the Scripts

Run `test_script.py` to syllabify and compute WCM for random words.

```bash
python test_script.py
```

**Sample Output:**

```
Word: crisscrossing
Pronunciation: ['K', 'R', 'IH1', 'S', 'K', 'R', 'AO2', 'S', 'IH0', 'NG']
Number of Syllables: 4
Syllabification: K-R-IH1.S-K-R-AO2.S-IH0-NG
Word Complexity Measure (WCM): 5
----------------------------------------
Word: example
Pronunciation: ['IH0', 'G', 'Z', 'AE1', 'M', 'P', 'AH0', 'L']
Number of Syllables: 3
Syllabification: IH0-G-Z-AE1.M-P-AH0.L
Word Complexity Measure (WCM): 3
----------------------------------------
...
```

Each execution selects ten random words by default, syllabifies them, computes their WCM, and displays the results.

---

## Example

Processing the word `crisscrossing`:

1. **Pronunciation:** `['K', 'R', 'IH1', 'S', 'K', 'R', 'AO2', 'S', 'IH0', 'NG']`
2. **Syllabification:**
   - `K-R-IH1`
   - `S-K-R-AO2`
   - `S-IH0-NG`
3. **Word Complexity Measure (WCM):** `5`

**Pretty-Printed Syllabification:**

```
K-R-IH1.S-K-R-AO2.S-IH0-NG
```

---

## Troubleshooting

### Common Issues

1. **Missing Modules or Files:**

   - **Error:**
     ```
     Error: syllabify.py not found in the current directory.
     ```
   
   - **Solution:** Ensure that `syllabify.py` and `wcm.py` are present in the same directory as `test_script.py`. Verify the file names and paths.

2. **Missing NLTK Data:**

   - **Error:**
     ```
     LookupError: 
     **********************************************************************
       Resource cmudict not found.
       Please use the NLTK Downloader to obtain the resource:
   
           >>> import nltk
           >>> nltk.download('cmudict')
     ```
   
   - **Solution:** Run the following command to download the CMU Pronouncing Dictionary:
   
     ```bash
     python -c "import nltk; nltk.download('cmudict')"
     ```

3. **TypeErrors or ValueErrors:**

   - **Cause:** Mismatch in function arguments or incorrect syllabification rules.
   
   - **Solution:** Ensure that all required arguments are passed to functions and that syllabification rules (`SLAX`, `O3`, `O2`) are correctly defined.

4. **Syllabification Mismatch:**

   - **Error:**
     ```
     ValueError: Could not syllabify ['K', 'R', 'IH1', 'S', 'K', 'R', 'AO2', 'S', 'IH0', 'NG']. Syllabified output: ['K', 'R', 'IH1', 'S', 'K', 'R', 'AO2', 'S', 'IH0', 'NG']
     ```
   
   - **Cause:** The syllabified output does not match the original pronunciation.
   
   - **Solution:** Review the syllabification rules and ensure that all phonemes are correctly assigned to syllables.

### Seeking Help

If you encounter issues not covered here:

1. **Check the Logs:** Review any error messages or logs for clues.
2. **Review Code:** Ensure that all scripts are correctly implemented and that dependencies are met.
3. **Contact Maintainers:** Reach out to the project maintainers or contributors for assistance.

---

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository.**
2. **Create a Feature Branch:**
   
   ```bash
   git checkout -b feature/YourFeatureName
   ```
   
3. **Commit Your Changes:**
   
   ```bash
   git commit -m "Add Your Feature"
   ```
   
4. **Push to the Branch:**
   
   ```bash
   git push origin feature/YourFeatureName
   ```
   
5. **Open a Pull Request:** Describe your changes and submit for review.