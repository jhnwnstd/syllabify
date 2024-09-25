from dataclasses import dataclass
from itertools import chain
from typing import List, Tuple, Set
import copy

# Constants
SLAX = {
    'IH1', 'IH2', 'EH1', 'EH2', 'AE1', 'AE2', 'AH1', 'AH2',
    'UH1', 'UH2',
}

VOWELS = {
    'IY1', 'IY2', 'IY0', 'EY1', 'EY2', 'EY0', 'AA1', 'AA2', 'AA0',
    'ER1', 'ER2', 'ER0', 'AW1', 'AW2', 'AW0', 'AO1', 'AO2', 'AO0',
    'AY1', 'AY2', 'AY0', 'OW1', 'OW2', 'OW0', 'OY1', 'OY2', 'OY0',
    'IH0', 'EH0', 'AE0', 'AH0', 'UH0', 'UW1', 'UW2', 'UW0', 'UW',
    'IY', 'EY', 'AA', 'ER', 'AW', 'AO', 'AY', 'OW', 'OY',
    'UH', 'IH', 'EH', 'AE', 'AH',
} | SLAX

# Licit medial onsets
O2 = {
    ('P', 'R'), ('T', 'R'), ('K', 'R'), ('B', 'R'), ('D', 'R'),
    ('G', 'R'), ('F', 'R'), ('TH', 'R'),
    ('P', 'L'), ('K', 'L'), ('B', 'L'), ('G', 'L'),
    ('F', 'L'), ('S', 'L'),
    ('K', 'W'), ('G', 'W'), ('S', 'W'),
    ('S', 'P'), ('S', 'T'), ('S', 'K'),
    ('HH', 'Y'),  # "clerihew"
    ('R', 'W'),
}

O3 = {
    ('S', 'T', 'R'), ('S', 'K', 'L'), ('T', 'R', 'W')  # "octroi"
}

@dataclass
class Syllable:
    onset: List[str]
    nucleus: List[str]
    coda: List[str]

def identify_nuclei_and_onsets(pronunciation: List[str]) -> Tuple[List[List[str]], List[List[str]], List[str]]:
    """
    Identify nuclei and onsets in the pronunciation.

    Args:
        pronunciation (List[str]): List of ARPABET phonemes.

    Returns:
        Tuple containing:
            - nuclei (List[List[str]]): List of nuclei per syllable.
            - onsets (List[List[str]]): List of onsets per syllable.
            - codas (List[str]): Remaining phonemes after the last nucleus.
    """
    nuclei = []
    onsets = []
    last_vowel_index = -1

    for index, segment in enumerate(pronunciation):
        if segment in VOWELS:
            nuclei.append([segment])
            onsets.append(pronunciation[last_vowel_index + 1:index])
            last_vowel_index = index

    # Collect remaining segments as coda
    codas = pronunciation[last_vowel_index + 1:]
    return nuclei, onsets, codas

def resolve_onsets_and_codas(
    nuclei: List[List[str]],
    onsets: List[List[str]],
    codas: List[str],
    alaska_rule: bool,
    SLAX: Set[str],
    O3: Set[Tuple[str, ...]],
    O2: Set[Tuple[str, ...]]
) -> Tuple[List[List[str]], List[List[str]]]:
    """
    Resolve onsets and compute codas based on syllabification rules.

    This function adjusts the onsets of syllables to maximize onset clusters according to specified rules.
    It also computes the codas for each syllable based on the adjusted onsets and remaining phonemes.
    Optionally, it applies the Alaska rule to handle specific consonant clusters.

    Args:
        nuclei (List[List[str]]): List of nuclei (vowels) per syllable.
        onsets (List[List[str]]): List of onsets (consonant clusters) per syllable.
        codas (List[str]): Remaining phonemes after the last nucleus to be assigned as codas.
        alaska_rule (bool): Whether to apply the Alaska syllabification rule.
        SLAX (Set[str]): Set of consonant clusters relevant to the Alaska rule.
        O3 (Set[Tuple[str, ...]]): Set of three-consonant clusters for onset maximization.
        O2 (Set[Tuple[str, ...]]): Set of two-consonant clusters for onset maximization.

    Returns:
        Tuple[List[List[str]], List[List[str]]]:
            - Updated onsets per syllable after resolving.
            - Updated codas per syllable after resolving.

    Raises:
        ValueError: If input lists are empty or mismatched in length.

    Example:
        >>> nuclei = [['AH0'], ['AE1']]
        >>> onsets = [['K'], ['S', 'T']]
        >>> codas = ['D']
        >>> resolve_onsets_and_codas(nuclei, onsets, codas, True, SLAX, O3, O2)
        ([['K'], ['S', 'T']], [['D'], []])
    """
    # Validate inputs
    if not nuclei or not onsets:
        raise ValueError("Nuclei and onsets lists must not be empty.")
    if len(nuclei) != len(onsets):
        raise ValueError("Nuclei and onsets lists must be of the same length.")

    # Create deep copies to avoid mutating original inputs
    nuclei = copy.deepcopy(nuclei)
    onsets = copy.deepcopy(onsets)
    resolved_codas = [[] for _ in range(len(onsets))]

    for i in range(1, len(onsets)):
        coda = []
        current_onset = onsets[i]

        # Handle special case: Onset starts with 'R' and has more than one phoneme
        starts_with_R = len(current_onset) > 1 and current_onset[0] == 'R'
        if starts_with_R:
            nuclei[i - 1].append(current_onset.pop(0))

        # Handle special case: Onset ends with 'Y' and has more than two phonemes
        ends_with_Y = len(current_onset) > 2 and current_onset[-1] == 'Y'
        if ends_with_Y:
            nuclei[i].insert(0, current_onset.pop())

        # Apply Alaska rule
        applies_alaska_rule = (
            len(current_onset) > 1 and
            alaska_rule and
            nuclei[i - 1][-1] in SLAX and
            current_onset[0] == 'S'
        )
        if applies_alaska_rule:
            coda.append(current_onset.pop(0))

        # Onset maximization
        depth = 1
        if len(current_onset) > 1:
            last_two = tuple(current_onset[-2:])
            last_three = tuple(current_onset[-3:]) if len(current_onset) >= 3 else ()
            if last_three in O3:
                depth = 3
            elif last_two in O2:
                depth = 2

        # Transfer phonemes from onset to coda based on depth
        while len(current_onset) > depth:
            coda.append(current_onset.pop(0))

        resolved_codas[i - 1] = coda

    # Assign remaining codas to the last syllable's coda
    if codas:
        resolved_codas[-1].extend(codas)

    return onsets, resolved_codas

def syllabify(pron: List[str], alaska_rule: bool = True) -> List[Syllable]:
    """
    Syllabifies a CMU dictionary (ARPABET) word pronunciation.

    Args:
        pron (List[str]): A list of ARPABET phonemes representing a word.
        alaska_rule (bool): Whether to apply the Alaska rule for syllabification.

    Returns:
        List[Syllable]: A list of Syllable dataclasses representing the syllables.

    Raises:
        ValueError: If syllabification does not include all phonemes.
    
    Examples:
        >>> syllabify(['AH0', 'L', 'AE1', 'S', 'K', 'AH0'])
        [Syllable(onset=[], nucleus=['AH0'], coda=[]), Syllable(onset=['L'], nucleus=['AE1'], coda=[]), Syllable(onset=['S', 'K'], nucleus=['AH0'], coda=[])]
    """
    pronunciation = list(pron)
    nuclei, onsets, codas = identify_nuclei_and_onsets(pronunciation)
    onsets, resolved_codas = resolve_onsets_and_codas(nuclei, onsets, codas, alaska_rule, SLAX, O3, O2)

    syllables = [
        Syllable(onset, nucleus, coda)
        for onset, nucleus, coda in zip(onsets, nuclei, resolved_codas)
    ]

    # Assign any remaining coda to the last syllable
    if len(resolved_codas) > len(onsets):
        syllables[-1].coda.extend(resolved_codas[-1])

    # Flatten syllables and verify all segments are included
    flat_output = list(chain.from_iterable([s.onset + s.nucleus + s.coda for s in syllables]))
    if flat_output != pronunciation:
        raise ValueError(f"Could not syllabify {pronunciation}. Syllabified output: {flat_output}")

    return syllables

def pretty_print(syllab: List[Syllable]) -> str:
    """
    Pretty-print a syllabification.

    Args:
        syllab (List[Syllable]): List of Syllable dataclasses.

    Returns:
        str: A human-readable string representation of the syllabification.
    """
    syllable_strings = []
    for syl in syllab:
        onset = ' '.join(syl.onset)
        nucleus = ' '.join(syl.nucleus)
        coda = ' '.join(syl.coda)
        syllable = '-'.join(filter(None, [onset, nucleus, coda]))
        syllable_strings.append(syllable)
    return '.'.join(syllable_strings)

def destress(syllab: List[Syllable]) -> List[Syllable]:
    """
    Generate a syllabification with nuclear stress information removed.

    Args:
        syllab (List[Syllable]): List of Syllable dataclasses.

    Returns:
        List[Syllable]: Syllabification without stress markers.
    """
    destressed_syllables = []
    for syllable in syllab:
        nuke = [
            phoneme[:-1] if phoneme[-1] in {'0', '1', '2'} else phoneme
            for phoneme in syllable.nucleus
        ]
        destressed_syllables.append(Syllable(syllable.onset, nuke, syllable.coda))
    return destressed_syllables

if __name__ == '__main__':
    import doctest
    doctest.testmod()
