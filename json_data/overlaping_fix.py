"""
Модуль для исправления перекрывающихся сущностей в JSON файлах.
Удаляет перекрывающиеся сущности, сохраняя только одну из них.
"""

import os
from typing import Dict, List, Iterator, Any

import jsonlines


def check_overlap(entity1: Dict[str, int], entity2: Dict[str, int]) -> bool:
    """
    Проверяет, перекрываются ли две сущности в тексте.

    Args:
        entity1 (Dict[str, int]): Первая сущность с ключами 'start_offset' и 'end_offset'.
        entity2 (Dict[str, int]): Вторая сущность с ключами 'start_offset' и 'end_offset'.

    Returns:
        bool: True если сущности перекрываются, False в противном случае.
    """
    return (entity1['start_offset'] < entity2['end_offset'] and
            entity1['end_offset'] > entity2['start_offset'])


def remove_overlapping_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Удаляет перекрывающиеся сущности из списка.

    Args:
        entities (List[Dict[str, Any]]): Список сущностей, каждая из которых содержит
            ключи 'start_offset' и 'end_offset'.

    Returns:
        List[Dict[str, Any]]: Список сущностей без перекрытий.
    """
    entities_to_keep = []

    for i, entity1 in enumerate(entities):
        overlapping = False
        for j, entity2 in enumerate(entities):
            if i != j and check_overlap(entity1, entity2):
                overlapping = True
                break
        if not overlapping:
            entities_to_keep.append(entity1)

    return entities_to_keep


def process_records(records: List[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """
    Обрабатывает записи, удаляя перекрывающиеся сущности в каждой записи.

    Args:
        records (List[Dict[str, Any]]): Список записей, каждая из которых содержит
            ключ 'entities' со списком сущностей.

    Yields:
        Dict[str, Any]: Обработанная запись без перекрывающихся сущностей.
    """
    for record in records:
        entities = record['entities']
        entities_to_keep = remove_overlapping_entities(entities)
        record['entities'] = entities_to_keep
        yield record


def fix_overlapping(file_path: str) -> None:
    """
    Исправляет перекрывающиеся сущности в файле JSON.

    Args:
        file_path (str): Путь к файлу JSON для обработки.
    """
    temp_file_path = file_path + '.tmp'
    
    with jsonlines.open(file_path) as reader, jsonlines.open(temp_file_path, 'w') as writer:
        records = list(reader)
        new_records = process_records(records)
        writer.write_all(new_records)

    with open(temp_file_path, 'r', encoding='utf-8') as temp_file, \
         open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(temp_file.read())

    os.remove(temp_file_path)

