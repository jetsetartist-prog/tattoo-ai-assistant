"""
Определение языка текста: ru / he / en.
Без AI — на основе алфавита и статистики.
"""
import re


# Карта раскладки: английские клавиши → русские
LAYOUT_MAP = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?~",
    "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
)

# Частые русские буквосочетания (биграммы)
RU_BIGRAMS = {
    'ст', 'но', 'то', 'на', 'но', 'пр', 'по', 'ко', 'ро', 'ре',
    'ни', 'ка', 'та', 'ла', 'ли', 'ле', 'ра', 'да', 'до', 'во',
    'ол', 'ор', 'он', 'ен', 'ер', 'ел', 'ет', 'ат', 'ит', 'от',
    'не', 'де', 'те', 'ме', 'ве', 'се', 'ке', 'пе', 'бе', 'ге',
}

# Частые английские биграммы
EN_BIGRAMS = {
    'th', 'he', 'in', 'er', 'an', 're', 'on', 'at', 'en', 'nd',
    'ti', 'es', 'or', 'te', 'of', 'ed', 'is', 'it', 'al', 'ar',
    'st', 'to', 'nt', 'ng', 'se', 'ha', 'as', 'ou', 'io', 'le',
    've', 'co', 'me', 'de', 'hi', 'ri', 'ro', 'ic', 'ne', 'ea',
}


def _has_hebrew(text: str) -> bool:
    return bool(re.search(r'[\u0590-\u05FF]', text))


def _has_cyrillic(text: str) -> bool:
    return bool(re.search(r'[а-яА-ЯёЁ]', text))


def _has_latin(text: str) -> bool:
    return bool(re.search(r'[a-zA-Z]', text))


def _count_vowels_ratio(text: str, vowels: str) -> float:
    """Доля гласных в тексте."""
    letters = [c.lower() for c in text if c.isalpha()]
    if not letters:
        return 0.0
    vowels_count = sum(1 for c in letters if c in vowels)
    return vowels_count / len(letters)


def _has_meaningful_cyrillic(text: str) -> bool:
    """
    Проверяет, есть ли в тексте осмысленные русские биграммы
    или ключевые слова команд.
    """
    text_lower = text.lower()

    # 1. Проверяем ключевые слова (для транслита команд)
    KEYWORDS = [
        'привет', 'прайс', 'цена', 'записаться', 'запись',
        'меню', 'портфолио', 'контакты', 'стоимость', 'сколько',
    ]
    for kw in KEYWORDS:
        # Ищем вхождение первых 3-4 букв
        prefix = kw[:4]
        if prefix in text_lower:
            return True
        # Или нечёткое сравнение — первые 3 буквы
        prefix3 = kw[:3]
        if prefix3 in text_lower:
            return True

    # 2. Проверяем биграммы
    cyrillic_words = re.findall(r'[а-яё]+', text_lower)

    for word in cyrillic_words:
        if len(word) < 3:
            continue
        bigrams_in_word = {word[i:i+2] for i in range(len(word) - 1)}
        if bigrams_in_word & RU_BIGRAMS:
            vowel_ratio = _count_vowels_ratio(word, 'аеёиоуыэюя')
            if 0.3 <= vowel_ratio <= 0.6:
                return True

    return False


def _has_meaningful_latin(text: str) -> bool:
    """
    Проверяет, есть ли в тексте осмысленные английские биграммы.
    """
    text_lower = text.lower()
    latin_words = re.findall(r'[a-z]+', text_lower)

    for word in latin_words:
        if len(word) < 3:
            continue
        bigrams_in_word = {word[i:i+2] for i in range(len(word) - 1)}
        if bigrams_in_word & EN_BIGRAMS:
            vowel_ratio = _count_vowels_ratio(word, 'aeiouy')
            if 0.3 <= vowel_ratio <= 0.6:
                return True

    return False


def _is_translit(text: str) -> bool:
    """
    Проверяет, является ли латинский текст транслитом русского.
    Транслит — когда латиница после перевода через LAYOUT_MAP
    даёт ОСМЫСЛЕННЫЕ русские слова.
    """
    if not _has_latin(text):
        return False

    transliterated = text.translate(LAYOUT_MAP)

    # После перевода должна появиться кириллица
    if not _has_cyrillic(transliterated):
        return False

    # И эта кириллица должна быть осмысленной
    return _has_meaningful_cyrillic(transliterated)


def detect_language(text: str) -> str:
    """
    Определяет язык текста.
    Возвращает: 'ru', 'he' или 'en'.
    """
    if not text or not text.strip():
        return 'ru'

    text = text.strip()

    # 1. Иврит — по алфавиту
    if _has_hebrew(text):
        return 'he'

    # 2. Кириллица — точно русский
    if _has_cyrillic(text):
        return 'ru'

    # 3. Латиница
    if _has_latin(text):
        # 3a. Проверяем, не транслит ли это
        if _is_translit(text):
            return 'ru'

        # 3b. Проверяем, английский ли это
        if _has_meaningful_latin(text):
            return 'en'

        # 3c. Если не поняли — считаем английским
        # (если есть латиница, но нет русских паттернов)
        return 'en'

    # 4. По умолчанию — русский
    return 'ru'