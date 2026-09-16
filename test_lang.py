"""Тест определения языка."""
from core.i18n.detector import detect_language

tests = [
    ("привет", "ru"),
    ("Привет! Как дела?", "ru"),
    ("ghbdat", "ru"),
    ("ghfqc", "ru"),
    ("hello", "en"),
    ("Hello, how are you?", "en"),
    ("price please", "en"),
    ("שלום", "he"),
    ("מה המחיר?", "he"),
    ("אני רוצה לקבוע תור", "he"),
]

print("Тест определения языка:")
print("=" * 60)
ok = 0
for text, expected in tests:
    result = detect_language(text)
    status = "✅" if result == expected else "❌"
    if result == expected:
        ok += 1
    print(f"{status} '{text}' → '{result}' (ожидался '{expected}')")
print("=" * 60)
print(f"Результат: {ok}/{len(tests)}")
