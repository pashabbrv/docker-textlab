import re
from collections import Counter

WORD_PATTERN = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*", re.UNICODE)


def analyze(text: str) -> dict:
    original_words = WORD_PATTERN.findall(text)
    normalized_words = [word.casefold() for word in original_words]
    frequency = Counter(normalized_words)
    most_common = sorted(frequency.items(), key=lambda item: (-item[1], item[0]))[:5]

    return {
        "characters": len(text),
        "characters_without_spaces": sum(not char.isspace() for char in text),
        "words": len(original_words),
        "unique_words": len(frequency),
        "sentences": max(1, len(re.findall(r"[.!?]+", text))) if original_words else 0,
        "longest_word": max(original_words, key=len, default=None),
        "top_words": [{"word": word, "count": count} for word, count in most_common],
    }