from pathlib import Path

def load_phrases(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл с фразами {file_path} не найден!")
    with open(path, encoding="utf-8") as f:
        # Убираем пустые строки и пробельные символы
        return [line.strip() for line in f if line.strip()]
