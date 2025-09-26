"""
Syllabify: CMU ARPABET phonetic syllabification library.

This module implements Maximum Onset Principle (MOP) constrained syllabification
for CMU ARPABET phonemes. The algorithm is non-ambisyllabic and deterministic.

Key features:
- Onset maximization based on licit medial clusters (O2/O3 inventories)
- Optional "Alaska rule" for S + voiceless stops after stressed lax vowels
- Modern regex-based vowel recognition with base vowel sets
- Performance caching with LRU cache for repeated syllabifications
- Configurable pretty-printing with compact notation support

The syllabification assumes exactly one vowel per nucleus (standard for CMU ARPABET).
For non-CMU phone sets, additional validation may be required.
"""

from dataclasses import dataclass
from functools import lru_cache
from itertools import chain
from typing import List, Set, Tuple

import re

__all__ = [
    'syllabify',
    'syllabify_fast',
    'pretty_print',
    'destress',
    'Syllable',
    'SyllabificationError',
    'is_vowel',
    'is_stressed_lax',
]


# Constants
STRESS_RE = re.compile(r'^(?P<base>[A-Z]{2,3})(?P<stress>[012])?$')
BASE_VOWELS = {
    'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY',
    'IH', 'IY', 'OW', 'OY', 'UH', 'UW'
}
LAX_BASE = {'IH', 'EH', 'AE', 'AH', 'UH'}  # for Alaska checks
VOICELESS_STOPS = {'P', 'T', 'K'}


# Licit medial onsets (two-consonant clusters)
O2 = {
    # Stop + liquid
    ('P', 'R'), ('T', 'R'), ('K', 'R'), ('B', 'R'),
    ('D', 'R'), ('G', 'R'), ('F', 'R'), ('TH', 'R'),
    ('P', 'L'), ('K', 'L'), ('B', 'L'), ('G', 'L'),
    ('F', 'L'), ('S', 'L'),
    # Stop/fricative + glide
    ('K', 'W'), ('G', 'W'), ('S', 'W'),
    # S + voiceless stop
    ('S', 'P'), ('S', 'T'), ('S', 'K'),
    # Special cases
    ('HH', 'Y'),  # "clerihew"
    ('R', 'W'),
}

# Licit medial onsets (three-consonant clusters)
O3 = {
    ('S', 'T', 'R'),  # "distract"
    ('S', 'K', 'L'),  # "sclerosis"
    ('T', 'R', 'W'),  # "octroi"
}

class SyllabificationError(ValueError):
    """Raised when syllabification fails to include all phonemes.

    This exception is raised when the syllabification algorithm cannot
    properly distribute all input phonemes across syllable structures,
    or when no vowel nuclei are found in the input.
    """

def is_vowel(phoneme: str) -> bool:
    """Check if a phoneme is a vowel using regex parsing.

    Args:
        phoneme: ARPABET phoneme string (e.g., 'AE1', 'IH0', 'K')

    Returns:
        True if the phoneme is a vowel, False otherwise

    Examples:
        >>> is_vowel('AE1')
        True
        >>> is_vowel('K')
        False
    """
    match = STRESS_RE.match(phoneme)
    return bool(match and match.group('base') in BASE_VOWELS)

def is_stressed_lax(phoneme: str) -> bool:
    """Check if a phoneme is a stressed lax vowel.

    Used primarily for the Alaska rule, which applies after
    stressed lax vowels.

    Args:
        phoneme: ARPABET phoneme string

    Returns:
        True if the phoneme is a stressed lax vowel, False otherwise

    Examples:
        >>> is_stressed_lax('AE1')
        True
        >>> is_stressed_lax('AE0')
        False
    """
    match = STRESS_RE.match(phoneme)
    return bool(
        match and
        match.group('base') in LAX_BASE and
        match.group('stress') in {'1', '2'}
    )

def legal_onset_depth(
    onset: List[str],
    O2: Set[Tuple[str, ...]],
    O3: Set[Tuple[str, ...]]
) -> int:
    """Determine the maximum legal onset depth for a consonant cluster.

    Uses the provided onset inventories to find the longest legal
    cluster at the end of the given onset sequence.

    Args:
        onset: List of consonant phonemes
        O2: Set of legal two-consonant clusters
        O3: Set of legal three-consonant clusters

    Returns:
        Maximum number of consonants that can form a legal onset
        (1, 2, or 3)
    """
    n = len(onset)
    if n >= 3 and tuple(onset[-3:]) in O3:
        return 3
    if n >= 2 and tuple(onset[-2:]) in O2:
        return 2
    return 1

@dataclass(slots=True)
class Syllable:
    onset: List[str]
    nucleus: List[str]
    coda: List[str]

def identify_nuclei_and_onsets(
    pronunciation: List[str]
) -> Tuple[List[List[str]], List[List[str]], List[str]]:
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
        if is_vowel(segment):
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
        >>> resolve_onsets_and_codas(nuclei, onsets, codas, True, O3, O2)
        ([['K'], ['S', 'T']], [[], ['D']])
    """
    # Validate inputs
    if not nuclei or not onsets:
        raise ValueError("Nuclei and onsets lists must not be empty.")
    if len(nuclei) != len(onsets):
        raise ValueError("Nuclei and onsets lists must be of the same length.")

    # Create shallow copies to avoid mutating original inputs
    onsets = [o[:] for o in onsets]
    resolved_codas = [[] for _ in range(len(onsets))]

    for i in range(1, len(onsets)):
        coda = []
        current_onset = onsets[i]

        # Apply Alaska rule: S + voiceless stop after stressed lax vowel
        applies_alaska_rule = (
            alaska_rule and
            len(current_onset) > 1 and
            is_stressed_lax(nuclei[i - 1][-1]) and
            current_onset[0] == 'S' and
            current_onset[1] in VOICELESS_STOPS
        )
        if applies_alaska_rule:
            coda.append(current_onset.pop(0))

        # Onset maximization using precomputed legal depth
        depth = legal_onset_depth(current_onset, O2=O2, O3=O3)
        while len(current_onset) > depth:
            coda.append(current_onset.pop(0))

        resolved_codas[i - 1] = coda

    # Assign remaining codas to the last syllable's coda
    if codas:
        resolved_codas[-1].extend(codas)

    return onsets, resolved_codas

def syllabify(pron: List[str], alaska_rule: bool = False) -> List[Syllable]:
    """
    Syllabifies a CMU dictionary (ARPABET) word pronunciation.

    Args:
        pron (List[str]): A list of ARPABET phonemes representing a word.
        alaska_rule (bool): Whether to apply the Alaska rule for syllabification.

    Returns:
        List[Syllable]: A list of Syllable dataclasses representing the syllables.

    Raises:
        SyllabificationError: If syllabification does not include all phonemes or no vowels found.

    Examples:
        >>> syllabify(['AH0', 'L', 'AE1', 'S', 'K', 'AH0'])
        [Syllable(onset=[], nucleus=['AH0'], coda=[]), Syllable(onset=['L'], nucleus=['AE1'], coda=[]), Syllable(onset=['S', 'K'], nucleus=['AH0'], coda=[])]
    """
    if not any(is_vowel(p) for p in pron):
        raise SyllabificationError(f"No vowel nucleus found in {pron}")

    pronunciation = list(pron)
    nuclei, onsets, codas = identify_nuclei_and_onsets(pronunciation)
    onsets, resolved_codas = resolve_onsets_and_codas(
        nuclei, onsets, codas, alaska_rule, O3, O2
    )

    syllables = [
        Syllable(onset, nucleus, coda)
        for onset, nucleus, coda in zip(onsets, nuclei, resolved_codas)
    ]

    # Assign any remaining coda to the last syllable
    if len(resolved_codas) > len(onsets):
        syllables[-1].coda.extend(resolved_codas[-1])

    # Flatten syllables and verify all segments are included
    flat_output = list(chain.from_iterable([
        s.onset + s.nucleus + s.coda for s in syllables
    ]))
    if flat_output != pronunciation:
        raise SyllabificationError(
            f"Could not syllabify {pronunciation}. "
            f"Syllabified output: {flat_output}"
        )

    return syllables

@lru_cache(maxsize=50000)
def syllabify_cached(
    pron: Tuple[str, ...],
    alaska_rule: bool = False
) -> Tuple[Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]], ...]:
    """
    Cached version of syllabify that works with immutable tuples.

    Args:
        pron: Tuple of ARPABET phonemes representing a word.
        alaska_rule: Whether to apply the Alaska rule for syllabification.

    Returns:
        Tuple of tuples representing syllables as (onset, nucleus, coda).
    """
    syllables = syllabify(list(pron), alaska_rule)
    return tuple(
        (tuple(s.onset), tuple(s.nucleus), tuple(s.coda))
        for s in syllables
    )

def syllabify_fast(pron: List[str], alaska_rule: bool = False) -> List[Syllable]:
    """
    Fast syllabify using cache at the public boundary.

    Args:
        pron: List of ARPABET phonemes representing a word.
        alaska_rule: Whether to apply the Alaska rule for syllabification.

    Returns:
        List[Syllable]: A list of Syllable dataclasses representing the syllables.
    """
    tup = tuple(pron)
    triple = syllabify_cached(tup, alaska_rule=alaska_rule)
    return [
        Syllable(list(o), list(n), list(c))
        for (o, n, c) in triple
    ]

def pretty_print(
    syllab: List[Syllable],
    *,
    join_with_dot: str = '.',
    intra_sep: str = '-',
    phone_join: str = ' ',  # set to '' for compact clusters
    compact: bool = False   # sugar for phone_join=''
) -> str:
    """
    Pretty-print a syllabification with configurable formatting.

    Args:
        syllab (List[Syllable]): List of Syllable dataclasses.
        join_with_dot (str): Character to join syllables (default: '.')
        intra_sep (str): Character to separate onset/nucleus/coda (default: '-')
        phone_join (str): Character to join phonemes within clusters (default: ' ')
        compact (bool): Sugar for phone_join='' (default: False)

    Returns:
        str: A human-readable string representation of the syllabification.

    Examples:
        >>> syls = [Syllable(['S','P'], ['EH1'], ['K','T'])]
        >>> pretty_print(syls)
        'S P-EH1-K T'
        >>> pretty_print(syls, phone_join='')
        'SP-EH1-KT'
        >>> pretty_print(syls, compact=True)
        'SP-EH1-KT'
    """
    if compact:
        phone_join = ''

    chunks = []
    for s in syllab:
        onset = phone_join.join(s.onset)
        nucleus = phone_join.join(s.nucleus)
        coda = phone_join.join(s.coda)
        parts = [p for p in (onset, nucleus, coda) if p]
        chunks.append(intra_sep.join(parts))
    return join_with_dot.join(chunks)


def destress(syllab: List[Syllable]) -> List[Syllable]:
    """
    Generate a syllabification with nuclear stress information removed.

    Args:
        syllab (List[Syllable]): List of Syllable dataclasses.

    Returns:
        List[Syllable]: Syllabification without stress markers.
    """
    out: List[Syllable] = []
    for s in syllab:
        nuke = [
            p[:-1] if p and p[-1] in {'0', '1', '2'} else p
            for p in s.nucleus
        ]
        out.append(Syllable(
            onset=s.onset[:], nucleus=nuke, coda=s.coda[:]
        ))
    return out


if __name__ == '__main__':
    import doctest
    doctest.testmod()