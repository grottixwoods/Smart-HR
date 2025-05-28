"""
Модуль для контроля и корректировки пробелов в сущностях JSON файлов.
Удаляет лишние пробелы в начале и конце сущностей.
"""

import json
from typing import Dict, List, Any


def correct_offsets(text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Корректирует начальные и конечные индексы сущностей в соответствии с текстом.

    Args:
        text (str): Исходный текст.
        entities (List[Dict[str, Any]]): Список сущностей, каждая представлена словарем
            с ключами 'start_offset', 'end_offset' и 'label'.

    Returns:
        List[Dict[str, Any]]: Список скорректированных сущностей.
    """
    corrected_entities = []

    for entity in entities:
        start_offset = entity['start_offset']
        end_offset = entity['end_offset']
        label = entity['label']

        # Ограничиваем индексы длиной текста
        start_offset = max(0, min(start_offset, len(text)))
        end_offset = max(0, min(end_offset, len(text)))

        # Удаляем пробелы в начале сущности
        while start_offset < end_offset and text[start_offset].isspace():
            start_offset += 1
            print('SPACE EDITED')

        # Удаляем пробелы в конце сущности
        while end_offset > start_offset and text[end_offset - 1].isspace():
            end_offset -= 1
            print('SPACE EDITED')

        corrected_entities.append({
            'start_offset': start_offset,
            'end_offset': end_offset,
            'label': label
        })

    return corrected_entities


def process_spaces_jsonl(input_file_path: str) -> None:
    """
    Обрабатывает JSONL-файл, корректируя пробелы в сущностях.

    Args:
        input_file_path (str): Путь к входному файлу JSONL.

    Note:
        Каждая строка файла должна содержать JSON объект с ключами:
        - 'text': текст записи
        - 'entities': список сущностей
    """
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    output_data = []

    for line in lines:
        data = json.loads(line.strip())
        text = data['text']
        entities = data['entities']
        corrected_entities = correct_offsets(text, entities)

        data['entities'] = corrected_entities
        output_data.append(data)

    with open(input_file_path, 'w', encoding='utf-8') as output_file:
        for data in output_data:
            output_file.write(json.dumps(data, ensure_ascii=False) + '\n')
