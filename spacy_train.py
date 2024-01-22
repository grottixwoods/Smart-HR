import spacy
import json
import random
from spacy.training import Example

# Main section:
# Загружает языковую модель SpaCy для русского языка и тренирует ее на метках и текстах из JSON-файла.
# Сохраняет обученную модель в файл "nlp_model".

nlp = spacy.load("ru_core_news_lg") # Загрузка предварительно обученной языковой модели SpaCy для русского языка.

data = []
with open("json_data/jsons/all_pythons.jsonl", "r", encoding="utf-8") as json_file:
    for line in json_file:
        data.append(json.loads(line))

# Разделение данных на тренировочный, валидационный и тестовый наборы:
random.shuffle(data)
split_ratio = 0.8
split_index1 = int(split_ratio * len(data))
split_index2 = int(split_ratio * len(data) * 2)
train_data = data[:split_index1]
validate_data = data[split_index1:split_index2]
test_data = data[split_index2:]

# def evaluate_model(nlp, data): - Оценивает модель по потерям на наборе данных.
# nlp - загруженная модель SpaCy
# data - набор данных для обучения

def evaluate_model(nlp, data):
    losses = {}
    for item in data:
        text = item['text']
        annotations = {"entities": []}
        for entity in item['entities']:
            start = entity['start_offset']
            end = entity['end_offset']
            label = entity['label']
            annotations["entities"].append((start, end, label))
        example = Example.from_dict(nlp.make_doc(text), annotations)
        nlp.update([example], drop=0.3, losses=losses)
    return losses.get("ner", 0.0)

if 'ner' not in nlp.pipe_names:
    ner = nlp.add_pipe('ner')
else:
    ner = nlp.get_pipe('ner')

# Определение уникальных меток сущностей и добавление их к компоненту NER:
unique_labels = set()
for item in data:
    for entity in item['entities']:
        unique_labels.add(entity['label'])

for label in unique_labels:
    ner.add_label(label)

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']

initial_validate_loss = evaluate_model(nlp, validate_data)
print(f"Initial Validation loss: {initial_validate_loss}")

# Обучение модели:
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for itn in range(200):
        print("Starting iteration " + str(itn))
        random.shuffle(train_data)
        losses = {}
        for item in train_data:
            text = item['text']
            annotations = {"entities": []}
            for entity in item['entities']:
                start = entity['start_offset']
                end = entity['end_offset']
                label = entity['label']
                annotations["entities"].append((start, end, label))
            example = Example.from_dict(nlp.make_doc(text), annotations)
            nlp.update([example], drop=0.3, losses=losses)

        validate_loss = evaluate_model(nlp, validate_data)
        print(f"Iteration {itn}: Validation loss: {validate_loss}")

# Сохранение обученной модели:
nlp.to_disk('nlp_model')
