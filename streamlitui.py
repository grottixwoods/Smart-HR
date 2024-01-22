import streamlit as st

from similarity import (get_entity_vacancy_UI,
                        get_entity_resume_UI,
                        calculate_avg_cosine_similarity)

# def save_uploadedfile(uploadedfile) -> None: - Сохраняет загруженный файл.
# uploadedfile - Загруженный файл.

def save_uploadedfile(uploadedfile) -> None:
    with open(uploadedfile.name, "wb") as f:
        f.write(uploadedfile.getbuffer())

# Main section:
# Использует библиотеку Streamlit для построения веб-приложения ЦИАРС.КАДР.
# Позволяет загрузить вакансию и одно или несколько резюме, а затем отображает информацию по сущностям и сходству.        

st.title('ЦИАРС.КАДР') # Заголовок страницы.

vacancy_uploader = st.file_uploader(label='Загрузите вакансию', # Компонент для загрузки вакансии.
                                    accept_multiple_files=False)
resume_uploader = st.file_uploader(label='Загрузите резюме',    # Компонент для загрузки резюме.
                                   accept_multiple_files=True)


if resume_uploader is not None:
    resume_list = []
    for resume in resume_uploader:
        save_uploadedfile(resume)
        resume_list.append(resume.name)
    resume_selector = st.selectbox('Выбор резюме', resume_list, index=None, # Выбор из загруженных резюме.
                                   placeholder='Выбор резюме',
                                   label_visibility='collapsed')

col1, col2 = st.columns(2) # Разделение страницы на две колонки.
with col2:
    if resume_selector is not None:
        df = get_entity_resume_UI(resume_selector) # Получение сущностей из выбранного резюме.
        st.write('Резюме') # Вывод заголовка.
        st.dataframe(data=df, hide_index=True, use_container_width=True) # Вывод данных о сущностях резюме.
with col1:
    if vacancy_uploader is not None:
        save_uploadedfile(vacancy_uploader) # Сохранение загруженной вакансии.
        st.write('Вакансия') # Вывод заголовка.
        df = get_entity_vacancy_UI(vacancy_uploader.name) # Получение сущностей из вакансии
        st.dataframe(data=df, hide_index=True, use_container_width=True) # Вывод данных о сущностях вакансии.

if resume_uploader and vacancy_uploader is not None:
    df_similarity = calculate_avg_cosine_similarity(vacancy_uploader.name, # Рассчет среднего косинусного сходства между вакансией и резюме.
                                                    resume_list)
    st.dataframe(data=df_similarity, hide_index=True, use_container_width=True) # Вывод данных о сходстве.
