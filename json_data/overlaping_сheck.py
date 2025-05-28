"""
Модуль для проверки перекрывающихся сущностей в JSON файлах.
Выявляет и выводит информацию о перекрывающихся сущностях в тексте.
"""

from typing import Dict, Any

import jsonlines

def check_overlap(entity1: Dict[str, Any], entity2: Dict[str, Any]) -> bool:
    """
    Проверяет, перекрываются ли две сущности в тексте.

    Args:
        entity1 (Dict[str, Any]): Первая сущность с ключами 'start_offset' и 'end_offset'.
        entity2 (Dict[str, Any]): Вторая сущность с ключами 'start_offset' и 'end_offset'.

    Returns:
        bool: True если сущности перекрываются, False в противном случае.
    """
    return (entity1['start_offset'] < entity2['end_offset'] and
            entity1['end_offset'] > entity2['start_offset'])

def check_overlapping(file_path: str) -> None:
    """
    Проверяет перекрытия сущностей в каждой записи файла JSON.

    Args:
        file_path (str): Путь к файлу JSON для проверки.

    Note:
        Предполагается, что каждая запись содержит ключи:
        - 'id': идентификатор записи
        - 'entities': список сущностей
        - 'text': текст записи
    """
    with jsonlines.open(file_path) as reader:
        for record in reader:
            entities = record['entities']
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities):
                    if i != j and check_overlap(entity1, entity2):
                        print(f"Overlap detected in record {record['id']}:")
                        print(
                            f"Entity {entity1['label']} "
                            f"({entity1['start_offset']} - {entity1['end_offset']}) "
                            f"overlaps with Entity {entity2['label']} "
                            f"({entity2['start_offset']} - {entity2['end_offset']})"
                        )
                        print(
                            f"Text: {record['text'][entity1['start_offset']:entity1['end_offset']]} | "
                            f"{record['text'][entity2['start_offset']:entity2['end_offset']]}"
                        )
                        print("-" * 60)


