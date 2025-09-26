"""Word Complexity Measure (WCM) implementation.

Implements the Word Complexity Measure as described in:
C. Stoel-Gammon. 2010. The Word Complexity Measure: Description and
application to developmental phonology and disorders. Clinical
Linguistics and Phonetics 24(4-5): 271-282.
"""

from syllabify import syllabify_fast

__all__ = ['wcm']

# Sound class constants for WCM scoring
DORSALS = {'K', 'G', 'NG'}
LIQUIDS = {'L', 'R'}
VOICED_FRICATIVES_AFFRICATES = {'V', 'DH', 'Z', 'ZH'}
FRICATIVES_AFFRICATES = {'F', 'TH', 'S', 'SH', 'CH'} | VOICED_FRICATIVES_AFFRICATES

def wcm(
    phonemes: list[str],
    *,
    base_bonus: bool = False,
    alaska_rule: bool = False
) -> int:
    """
    Calculate the Word Complexity Measure (WCM) for a given word based on its phonemic structure.

    Args:
        phonemes: A list of ARPABET phonemes representing a word.
        base_bonus: If True, add baseline complexity for syllable count and stress patterns.
        alaska_rule: Whether to apply the Alaska rule for syllabification.

    Returns:
        int: The complexity score of the word.

    Reference:
        C. Stoel-Gammon. 2010. The Word Complexity Measure: Description and
        application to developmental phonology and disorders. Clinical
        Linguistics and Phonetics 24(4-5): 271-282.
    """
    syllables = syllabify_fast(phonemes, alaska_rule=alaska_rule)
    score = 0

    # ---- optional: baseline complexity ----
    if base_bonus:
        # +1 per syllable, +1 per stress change (simple informative boost)
        score += len(syllables)
        stresses = [
            ('1' if s.nucleus and s.nucleus[0].endswith('1') else
             '2' if s.nucleus and s.nucleus[0].endswith('2') else '0')
            for s in syllables
        ]
        score += sum(a != b for a, b in zip(stresses, stresses[1:]))

    # ---- Stoel-Gammon categories ----
    # Word Patterns
    # (1) More than two syllables
    if len(syllables) > 2:
        score += 1

    # (2) Stress on any syllable but the first
    if len(syllables) > 1:
        # Check if any syllable other than the first has primary stress ('1')
        if any(
            '1' in syllable.nucleus[0] for syllable in syllables[1:]
        ):
            score += 1

    # Syllable Structures
    # (1) Word-final consonant
    if syllables[-1].coda:
        score += 1

    # (2) Syllable clusters
    for syllable in syllables:
        # Onset clusters (two or more consonants)
        if len(syllable.onset) > 1:
            score += 1
        # Coda clusters (two or more consonants)
        if len(syllable.coda) > 1:
            score += 1

    # Sound Classes
    for syllable in syllables:
        # Combine onset and coda phonemes
        consonants = syllable.onset + syllable.coda

        # (1) Velar consonants
        velars = sum(ph in DORSALS for ph in consonants)
        score += velars

        # (2) Liquids
        liquids = sum(ph in LIQUIDS for ph in consonants)
        score += liquids

        # (3) Fricatives and affricates
        fricatives_affricates = sum(
            ph in FRICATIVES_AFFRICATES for ph in consonants
        )
        score += fricatives_affricates

        # (4) Voiced fricatives and affricates
        # (intentionally double-counted per design)
        voiced_fricatives_affricates = sum(
            ph in VOICED_FRICATIVES_AFFRICATES for ph in consonants
        )
        score += voiced_fricatives_affricates

    return score