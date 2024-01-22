import json

# Функция correct_offsets(text, entities) корректирует начальные и конечные индексы сущностей в соответствии с текстом.
# text - текст, entities - список сущностей, каждая представлена словарем с ключами 'start_offset', 'end_offset' и 'label'.


def correct_offsets(text, entities):
    corrected_entities = []

    for entity in entities:
        start_offset = entity['start_offset']
        end_offset = entity['end_offset']
        label = entity['label']

        start_offset = max(0, min(start_offset, len(text)))
        end_offset = max(0, min(end_offset, len(text)))

        while start_offset < end_offset and text[start_offset].isspace():
            start_offset += 1
            print('SPACE EDITED')

        while end_offset > start_offset and text[end_offset - 1].isspace():
            end_offset -= 1
            print('SPACE EDITED')

        corrected_entities.append({
            'start_offset': start_offset,
            'end_offset': end_offset,
            'label': label
        })

    return corrected_entities

# Функция process_spaces_jsonl(input_file_path) обрабатывает JSONL-файл, содержащий записи в формате JSON по одной на строку.
# input_file_path - путь к входному файлу JSONL.
# Каждая строка файла обрабатывается, данные извлекаются в формате JSON, и вызывается correct_offsets для коррекции сущностей.
# Скорректированные данные записываются обратно в выходной файл.

def process_spaces_jsonl(input_file_path):
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
