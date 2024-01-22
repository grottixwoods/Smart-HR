import jsonlines
import os

# def check_overlap(entity1, entity2) проверяет, перекрываются ли две сущности в тексте.
# entity1 и entity2 представляют собой словари с ключами 'start_offset' и 'end_offset', указывающими на начальный и конечный индексы сущности.

def check_overlap(entity1, entity2):
    return (entity1['start_offset'] < entity2['end_offset'] and
            entity1['end_offset'] > entity2['start_offset'])

# def remove_overlapping_entities(entities) удаляет перекрывающиеся сущности из списка entities.
# entities - список сущностей, представленных словарями с ключами 'start_offset' и 'end_offset'.

def remove_overlapping_entities(entities):
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

# def process_records(records) обрабатывает записи, удаляя перекрывающиеся сущности в каждой записи.
# records - список записей, каждая из которых содержит ключ 'entities', представляющий собой список сущностей.

def process_records(records):
    for record in records:
        entities = record['entities']
        entities_to_keep = remove_overlapping_entities(entities)
        record['entities'] = entities_to_keep
        yield record

# def fix_overlapping(file_path) исправляет перекрывающиеся сущности в файле JSON.
# file_path - путь к файлу JSON. Функция создает временный файл для обработки данных.        

def fix_overlapping(file_path):
    temp_file_path = file_path + '.tmp'
    with jsonlines.open(file_path) as reader, jsonlines.open(temp_file_path, 'w') as writer:
        records = list(reader)
        new_records = process_records(records)
        writer.write_all(new_records)

    with open(temp_file_path, 'r', encoding='utf-8') as temp_file, open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(temp_file.read())

    os.remove(temp_file_path)

