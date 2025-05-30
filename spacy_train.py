"""
Модуль для обучения модели SpaCy на пользовательских данных.
Обучает модель распознаванию именованных сущностей (NER) на русском языке.
"""

import json
import random
from typing import Dict, List, Any, Tuple

import spacy
from spacy.training import Example


def load_training_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные для обучения из JSONL файла.

    Args:
        file_path (str): Путь к JSONL файлу с данными.

    Returns:
        List[Dict[str, Any]]: Список словарей с данными для обучения.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as json_file:
        for line in json_file:
            data.append(json.loads(line))
    return data


def split_data(data: List[Dict[str, Any]], split_ratio: float = 0.8) -> Tuple[List[Dict[str, Any]],
                                                                              List[Dict[str, Any]],
                                                                              List[Dict[str, Any]]]:
    """
    Разделяет данные на тренировочный, валидационный и тестовый наборы.

    Args:
        data (List[Dict[str, Any]]): Исходные данные.
        split_ratio (float): Коэффициент разделения данных.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]: 
            Тренировочный, валидационный и тестовый наборы данных.
    """
    random.shuffle(data)
    split_index1 = int(split_ratio * len(data))
    split_index2 = int(split_ratio * len(data) * 2)
    return data[:split_index1], data[split_index1:split_index2], data[split_index2:]


def evaluate_model(nlp: spacy.Language, data: List[Dict[str, Any]]) -> float:
    """
    Оценивает модель по потерям на наборе данных.

    Args:
        nlp (spacy.Language): Загруженная модель SpaCy.
        data (List[Dict[str, Any]]): Набор данных для оценки.

    Returns:
        float: Значение функции потерь.
    """
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


def setup_ner_pipe(nlp: spacy.Language, data: List[Dict[str, Any]]) -> None:
    """
    Настраивает компонент NER для модели.

    Args:
        nlp (spacy.Language): Модель SpaCy.
        data (List[Dict[str, Any]]): Данные для определения меток.
    """
    if 'ner' not in nlp.pipe_names:
        ner = nlp.add_pipe('ner')
    else:
        ner = nlp.get_pipe('ner')

    unique_labels = {entity['label'] for item in data for entity in item['entities']}
    for label in unique_labels:
        ner.add_label(label)


def train_model(nlp: spacy.Language, train_data: List[Dict[str, Any]], 
                validate_data: List[Dict[str, Any]], n_iterations: int = 200) -> None:
    """
    Обучает модель на предоставленных данных.

    Args:
        nlp (spacy.Language): Модель SpaCy для обучения.
        train_data (List[Dict[str, Any]]): Данные для обучения.
        validate_data (List[Dict[str, Any]]): Данные для валидации.
        n_iterations (int): Количество итераций обучения.
    """
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    
    with nlp.disable_pipes(*other_pipes):
        _ = nlp.begin_training()
        for itn in range(n_iterations):
            print(f"Starting iteration {itn}")
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


def main() -> None:
    """
    Основная функция для обучения модели.
    """
    # Загрузка модели и данных
    nlp = spacy.load("ru_core_news_lg")
    data = load_training_data("json_data/jsons/all_pythons.jsonl")
    
    # Разделение данных
    train_data, validate_data, test_data = split_data(data)
    
    # Настройка и обучение модели
    setup_ner_pipe(nlp, data)
    initial_validate_loss = evaluate_model(nlp, validate_data)
    print(f"Initial Validation loss: {initial_validate_loss}")
    
    train_model(nlp, train_data, validate_data)
    
    # Сохранение модели
    nlp.to_disk('nlp_model')


if __name__ == '__main__':
    main()
