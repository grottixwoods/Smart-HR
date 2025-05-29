"""
Модуль для расчета сходства между вакансиями и резюме.
Использует SpaCy для извлечения именованных сущностей и косинусное сходство для их сравнения.
"""

import os
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Загрузка предобученной модели SpaCy
nlp = spacy.load('nlp_model')

# Веса тегов для изменения приоритетов
TAG_WEIGHTS = {
    "CoreSkills": 1,
    "Skill": 1,
    "Sex": 1,
    "Age": 1,
    "Resides": 1,
    "Nationality": 1,
    "WorkPermit": 1,
    "Relocation": 1,
    "BusinessTrips": 1,
    "Name": 1,
    "Speciality": 1,
    "DesirableTravellingTimeToWork": 1,
    "Employment": 1,
    "WorkShedule": 1,
    "WorkExperience": 1,
    "Education": 1,
    "LanguageSkills": 1,
    "DrivingLicence": 1
}


def get_entity_vacancy_UI(doc_path: str) -> pd.DataFrame:
    """
    Извлекает именованные сущности и их метки из документа с вакансией.

    Args:
        doc_path (str): Путь к файлу с вакансией.

    Returns:
        pd.DataFrame: DataFrame с метками и значениями сущностей.
    """
    with open(doc_path, 'r', encoding='utf-8') as vacancy_file:
        vacancy_text = vacancy_file.read()
    vacancy_doc = nlp(vacancy_text)
    entity_text = defaultdict(set)
    for ent in vacancy_doc.ents:
        entity_text[ent.label_].add(ent.text.lower())
    return pd.DataFrame({
        "Label": list(entity_text),
        "Value": [", ".join(x) for x in entity_text.values()]
    })


def get_entity_resume_UI(file_path: str) -> pd.DataFrame:
    """
    Извлекает именованные сущности и их метки из документа с резюме.

    Args:
        file_path (str): Путь к файлу с резюме.

    Returns:
        pd.DataFrame: DataFrame с метками и значениями сущностей.
    """
    with open(file_path, 'r', encoding='utf-8') as resume_file:
        resume_text = resume_file.read()
    resume_doc = nlp(resume_text)
    entity_text = defaultdict(set)
    for ent in resume_doc.ents:
        entity_text[ent.label_].add(ent.text.lower())
    return pd.DataFrame({
        "Label": list(entity_text),
        "Value": [", ".join(x) for x in entity_text.values()]
    })


def get_entity_text(doc: spacy.tokens.Doc) -> Dict[str, Set[str]]:
    """
    Извлекает именованные сущности и их метки из обработанного SpaCy документа.

    Args:
        doc (spacy.tokens.Doc): Обработанный SpaCy документ.

    Returns:
        Dict[str, Set[str]]: Словарь с метками и множествами сущностей.
    """
    entity_text = defaultdict(set)
    for ent in doc.ents:
        entity_text[ent.label_].add(ent.text.lower())
    return entity_text


def calculate_cosine_similarity(
    vacancy_entities: Dict[str, Set[str]],
    resume_entities: Dict[str, Set[str]]
) -> Dict[str, float]:
    """
    Рассчитывает косинусное сходство между именованными сущностями вакансии и резюме.

    Args:
        vacancy_entities (Dict[str, Set[str]]): Сущности из вакансии.
        resume_entities (Dict[str, Set[str]]): Сущности из резюме.

    Returns:
        Dict[str, float]: Словарь с метками и значениями сходства.
    """
    similarity_dict = {}
    for label, vacancy_entity_list in vacancy_entities.items():
        resume_entity_list = resume_entities.get(label, [])
        similarity_list = []

        for vacancy_entity in vacancy_entity_list:
            max_similarity = 0.0

            for resume_entity in resume_entity_list:
                tfidf_vectorizer = TfidfVectorizer()
                tfidf_matrix = tfidf_vectorizer.fit_transform([vacancy_entity, resume_entity])
                similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

                if similarity > max_similarity:
                    max_similarity = similarity

            similarity_list.append(max_similarity)

        if similarity_list:
            entity_similarity = sum(similarity_list) / len(similarity_list)
            weighted_similarity = min(entity_similarity * TAG_WEIGHTS[label], 1.0)
            similarity_dict[label] = weighted_similarity

    return similarity_dict


def calculate_avg_cosine_similarity(
    vacancy_path: str,
    resume_list: List[str]
) -> pd.DataFrame:
    """
    Рассчитывает среднее косинусное сходство между вакансией и списком резюме.

    Args:
        vacancy_path (str): Путь к файлу вакансии.
        resume_list (List[str]): Список путей к файлам резюме.

    Returns:
        pd.DataFrame: DataFrame с именами файлов и значениями сходства.
    """
    avg_list = []
    with open(vacancy_path, 'r', encoding='utf-8') as vacancy_file:
        vacancy_text = vacancy_file.read()
        vacancy_doc = nlp(vacancy_text)
        unique_vacancy_entities = get_entity_text(vacancy_doc)

    for resume in resume_list:
        with open(resume, 'r', encoding='utf-8') as resume_file:
            resume_text = resume_file.read()
            resume_doc = nlp(resume_text)
            resume_entity_text = get_entity_text(resume_doc)

            similarity_dict = calculate_cosine_similarity(
                unique_vacancy_entities,
                resume_entity_text
            )

            total_similarity = sum(similarity_dict.values())
            average_similarity = total_similarity / max(1, len(similarity_dict))
            avg_list.append(average_similarity)

    return pd.DataFrame({
        'Filename': resume_list,
        'Similarity': avg_list
    })


def process_resumes(
    resume_folder: str,
    vacancy_doc: spacy.tokens.Doc,
    unique_vacancy_entities: Dict[str, Set[str]]
) -> Tuple[List[Tuple[str, float]], float, float]:
    """
    Обрабатывает резюме и рассчитывает метрики сходства.

    Args:
        resume_folder (str): Путь к папке с резюме.
        vacancy_doc (spacy.tokens.Doc): Документ вакансии.
        unique_vacancy_entities (Dict[str, Set[str]]): Сущности из вакансии.

    Returns:
        Tuple[List[Tuple[str, float]], float, float]: 
            Список наиболее похожих резюме, максимальное сходство,
            максимальное среднее сходство.
    """
    most_similar_resumes = []
    highest_similarity = -1.0
    highest_average_similarity = -1.0

    scored_folder = 'scored'
    if not os.path.exists(scored_folder):
        os.mkdir(scored_folder)

    for idx, resume_file in enumerate(os.listdir(resume_folder)):
        if resume_file.endswith('.txt'):
            with open(os.path.join(resume_folder, resume_file), 'r', encoding='utf-8') as f:
                resume_text = f.read()
                resume_doc = nlp(resume_text)
                resume_entity_text = get_entity_text(resume_doc)

                print(f"Уникальные Entity из файла резюме - {resume_file}:")
                for label, entities in resume_entity_text.items():
                    print(f"{label}: {', '.join(entities)}")

                similarity_dict = calculate_cosine_similarity(
                    unique_vacancy_entities,
                    resume_entity_text
                )
                total_similarity = sum(similarity_dict.values())
                average_similarity = total_similarity / max(1, len(similarity_dict))

                print("Сходство резюме по тегам:")
                for label, similarity in similarity_dict.items():
                    print(f"{label}: {similarity * 100:.2f}%")

                print(f"Общая близость: {average_similarity * 100:.2f}%")
                
                if average_similarity > 0.0:
                    new_filename = f"{idx + 1}_resume_score{int(average_similarity * 100)}.txt"
                    new_filepath = os.path.join(scored_folder, new_filename)
                    with open(new_filepath, 'w', encoding='utf-8') as scored_file:
                        scored_file.write(resume_text)

                if average_similarity > highest_average_similarity:
                    highest_average_similarity = average_similarity
                if average_similarity > highest_similarity:
                    highest_similarity = average_similarity
                    most_similar_resumes = [(resume_file, average_similarity)]
                elif average_similarity == highest_similarity:
                    most_similar_resumes.append((resume_file, average_similarity))
                print()

    return most_similar_resumes, highest_similarity, highest_average_similarity


def main() -> None:
    """
    Основная функция для обработки вакансий и резюме.
    """
    with open('data_collector/vacancy.txt', 'r', encoding='utf-8') as vacancy_file:
        vacancy_text = vacancy_file.read()

    vacancy_doc = nlp(vacancy_text)
    resume_folder = 'data_collector/resume'

    print("Уникальные Entity из vacancy.txt:")
    unique_vacancy_entities = get_entity_text(vacancy_doc)
    for label, entities in unique_vacancy_entities.items():
        print(f"{label}: {', '.join(entities)}")
    print()

    most_similar_resumes, highest_similarity, highest_average_similarity = process_resumes(
        resume_folder,
        vacancy_doc,
        unique_vacancy_entities
    )


if __name__ == '__main__':
    main()
