"""
Основной модуль для обработки JSON файлов.
Выполняет последовательную обработку файла:
1. Корректировка пробелов в сущностях
2. Проверка перекрытий сущностей
3. Исправление перекрытий
"""

from space_controller import process_spaces_jsonl
from overlaping_check import check_overlapping
from overlaping_fix import fix_overlapping


def process_json_file(file_path: str) -> None:
    """
    Выполняет полную обработку JSON файла.

    Args:
        file_path (str): Путь к JSON файлу для обработки.
    """

    process_spaces_jsonl(file_path)
    check_overlapping(file_path)
    fix_overlapping(file_path)


def main() -> None:
    """
    Основная функция для обработки JSON файла.
    """
    json_path = 'json_data/jsons/all.jsonl'
    process_json_file(json_path)


if __name__ == '__main__':
    main()
    