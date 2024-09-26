from syllabify import syllabify

# Constants
DORSALS = {'K', 'G', 'NG'}
LIQUIDS = {'L', 'R'}
VOICED_AF = {'V', 'DH', 'Z', 'ZH'}
AF = {'F', 'TH', 'S', 'SH', 'CH'} | VOICED_AF

def wcm(phonemes):
    """
    Calculate the Word Complexity Measure (WCM) for a given word based on its phonemic structure.

    Args:
        phonemes (list): A list of ARPABET phonemes representing a word.

    Returns:
        int: The complexity score of the word.

    Reference:
        C. Stoel-Gammon. 2010. The Word Complexity Measure: Description and 
        application to developmental phonology and disorders. Clinical
        Linguistics and Phonetics 24(4-5): 271-282.
    """
    syllables = syllabify(phonemes)
    score = 0

    # Word Patterns
    # (1) More than two syllables
    if len(syllables) > 2:
        score += 1

    # (2) Stress on any syllable but the first (marked as FIXME)
    # Assuming syllabify returns a Syllable dataclass with a nucleus containing stress
    if len(syllables) > 1:
        # Check if any syllable other than the first has primary stress ('1')
        if any('1' in syllable.nucleus[0] for syllable in syllables[1:]):
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
        fricatives_affricates = sum(ph in AF for ph in consonants)
        score += fricatives_affricates

        # (4) Voiced fricatives and affricates
        voiced_fricatives_affricates = sum(ph in VOICED_AF for ph in consonants)
        score += voiced_fricatives_affricates

    return score