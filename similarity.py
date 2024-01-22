import spacy
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

# Загрузка предобученной модели SpaCy.
nlp = spacy.load('nlp_model')

with open('data_collector/vacancy.txt', 'r', encoding='utf-8') as vacancy_file:
    vacancy_text = vacancy_file.read()

vacancy_doc = nlp(vacancy_text)

resume_folder = 'data_collector/resume'

# Веса тегов, для изменения приоритетов в зависимости от необходимости.
tag_weights = {
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

# def get_entity_vacancy_UI(doc): - Извлекает именованные сущности и их метки из документа с вакансией.
# doc - Обработанный SpaCy документ вакансии.

def get_entity_vacancy_UI(doc):
    with open(doc, 'r', encoding='utf-8') as vacancy_file:
        vacancy_text = vacancy_file.read()
    vacancy_doc = nlp(vacancy_text)
    entity_text = defaultdict(set)
    for ent in vacancy_doc.ents:
        entity_text[ent.label_].add(ent.text.lower())
    return pd.DataFrame({"Label": list(entity_text), "Value": [", ".join(x) for x in entity_text.values()]})

# def get_entity_resume_UI(file): - Извлекает именованные сущности и их метки из документа с резюме.
# file - Путь к файлу с резюме.

def get_entity_resume_UI(file):
    with open(file, 'r', encoding='utf-8') as resume_file:
        resume_text = resume_file.read()
    resume_doc = nlp(resume_text)
    entity_text = defaultdict(set)
    for ent in resume_doc.ents:
        entity_text[ent.label_].add(ent.text.lower())
    return pd.DataFrame({"Label": list(entity_text), "Value": [", ".join(x) for x in entity_text.values()]})


# def get_entity_text(doc): - Извлекает именованные сущности и их метки из обработанного SpaCy документа.
# doc - Обработанный SpaCy документ.

def get_entity_text(doc):
    entity_text = defaultdict(set)
    for ent in doc.ents:
        entity_text[ent.label_].add(ent.text.lower())
    return entity_text

# def calculate_cosine_similarity(vacancy_entities, resume_entities): - Рассчитывает косинусное сходство между именованными сущностями вакансии и резюме.
# vacancy_entities - Словарь, содержащий именованные сущности и их метки из вакансии.
# resume_entities - Словарь, содержащий именованные сущности и их метки из резюме.

def calculate_cosine_similarity(vacancy_entities, resume_entities):
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
            weighted_similarity = min(entity_similarity * tag_weights[label], 1.0)
            similarity_dict[label] = weighted_similarity

    return similarity_dict

# def calculate_avg_cosine_similarity(vacancy, resume_list): - Рассчитывает среднее косинусное сходство между вакансией и списком резюме.
# vacancy - Путь к файлу вакансии.
# resume_list - Список путей к файлам резюме.

def calculate_avg_cosine_similarity(vacancy, resume_list):
    avg_list = []
    with open(vacancy, 'r', encoding='utf-8') as vacancy_file:
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

    return pd.DataFrame({'Filename': resume_list, 'Similarity': avg_list})

# Главная секция:
# Выводит уникальные сущности из файла vacancy.txt.
# Итерируется по файлам резюме, рассчитывает метрики сходства и сохраняет отмеченные резюме.

if __name__ == '__main__':
    most_similar_resumes = []
    highest_similarity = -1.0
    highest_average_similarity = -1.0

    print("Уникальные Entity из vacancy.txt:")
    unique_vacancy_entities = get_entity_text(vacancy_doc)
    for label, entities in unique_vacancy_entities.items():
        print(f"{label}: {', '.join(entities)}")
    print()

    scored_folder = 'scored'
    if not os.path.exists(scored_folder):
        os.mkdir(scored_folder)

    for idx, resume_file in enumerate(os.listdir(resume_folder)):
        if resume_file.endswith('.txt'):
            with open(os.path.join(resume_folder, resume_file), 'r', encoding='utf-8') as resume_file:
                resume_text = resume_file.read()
                resume_doc = nlp(resume_text)

                resume_entity_text = get_entity_text(resume_doc)

                print(f"Уникальные Entity из файла резюме - {resume_file.name}:")

                for label, entities in resume_entity_text.items():
                    print(f"{label}: {', '.join(entities)}")

                similarity_dict = calculate_cosine_similarity(unique_vacancy_entities, resume_entity_text)
                total_similarity = sum(similarity_dict.values())
                average_similarity = total_similarity / max(1, len(similarity_dict))

                print("Сходство резюме по тегам:")
                for label, similarity in similarity_dict.items():
                    print(f"{label}: {similarity * 100:.2f}%")

                print(f"Общая близость: {average_similarity * 100:.2f}%")
                if average_similarity > 0.0:
                    new_filename = f"{idx + 1}_resume_score{int(average_similarity * 100)}.txt"
                    new_filepath = os.path.join(scored_folder, new_filename)
                    with open(new_filepath, 'w', encoding='utf-8') as scored_resume_file:
                        scored_resume_file.write(resume_text)

                if average_similarity > highest_average_similarity:
                    highest_average_similarity = average_similarity
                if average_similarity > highest_similarity:
                    highest_similarity = average_similarity
                    most_similar_resumes = [(resume_file, average_similarity)]
                elif average_similarity == highest_similarity:
                    most_similar_resumes.append((resume_file, average_similarity))
                print()
