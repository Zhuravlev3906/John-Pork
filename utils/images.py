import random
from pathlib import Path


def load_images(dir_path: Path):
    """
    Возвращает список путей к изображениям.
    """
    supported = (".jpg", ".jpeg", ".png", ".gif")
    images = [p for p in dir_path.iterdir() if p.suffix.lower() in supported]

    if not images:
        raise FileNotFoundError(f"Папка {dir_path} не содержит изображений!")

    return images


def get_random_image(dir_path: Path) -> Path:
    """
    Выбирает случайное изображение.
    """
    images = load_images(dir_path)
    return random.choice(images)
