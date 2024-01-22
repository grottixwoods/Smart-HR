import jsonlines

# def check_overlap(entity1, entity2) проверяет, перекрываются ли две сущности в тексте.
# entity1 и entity2 представляют собой словари с ключами 'start_offset' и 'end_offset', указывающими на начальный и конечный индексы сущности.

def check_overlap(entity1, entity2):
    return (entity1['start_offset'] < entity2['end_offset'] and
            entity1['end_offset'] > entity2['start_offset'])

# def сheck_overlaping(file_path) проверяет перекрытия сущностей в каждой записи файла JSON.
# file_path - путь к файлу JSON. Функция использует jsonlines для чтения JSON-файла построчно.
# Для каждой записи в файле, функция проходит через все пары сущностей и вызывает check_overlap.
# Если обнаруживается перекрытие, выводится информация о перекрытии, включая идентификатор записи, метку и диапазон каждой перекрывающейся сущности, а также фрагменты текста, в которых они находятся.
# Предполагается, что каждая запись содержит ключ 'id', 'entities' (список сущностей) и 'text' (текст записи).

def сheck_overlaping(file_path):
    with jsonlines.open(file_path) as reader:
        for record in reader:
            entities = record['entities']
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities):
                    if i != j and check_overlap(entity1, entity2):
                        print(f"Overlap detected in record {record['id']}:")
                        print(f"Entity {entity1['label']} ({entity1['start_offset']} - {entity1['end_offset']}) overlaps with Entity {entity2['label']} ({entity2['start_offset']} - {entity2['end_offset']})")
                        print(f"Text: {record['text'][entity1['start_offset']:entity1['end_offset']]} | {record['text'][entity2['start_offset']:entity2['end_offset']]}")
                        print()


