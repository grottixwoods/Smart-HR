"""
Streamlit UI для приложения SMART.HR.
Позволяет загружать и анализировать вакансии и резюме.
"""

import streamlit as st
from typing import List, Optional

from similarity import (
    get_entity_vacancy_UI,
    get_entity_resume_UI,
    calculate_avg_cosine_similarity
)


def save_uploadedfile(uploadedfile: st.UploadedFile) -> None:
    """
    Сохраняет загруженный файл в текущую директорию.

    Args:
        uploadedfile (st.UploadedFile): Загруженный файл через Streamlit.
    """
    with open(uploadedfile.name, "wb") as f:
        f.write(uploadedfile.getbuffer())


def main() -> None:
    """
    Основная функция приложения.
    Создает веб-интерфейс для загрузки и анализа вакансий и резюме.
    """
    st.title('SMART.HR')

    vacancy_uploader = st.file_uploader(
        label='Загрузите вакансию',
        accept_multiple_files=False
    )
    resume_uploader = st.file_uploader(
        label='Загрузите резюме',
        accept_multiple_files=True
    )

    resume_list: List[str] = []
    resume_selector: Optional[str] = None

    if resume_uploader is not None:
        for resume in resume_uploader:
            save_uploadedfile(resume)
            resume_list.append(resume.name)
        
        resume_selector = st.selectbox(
            'Выбор резюме',
            resume_list,
            index=None,
            placeholder='Выбор резюме',
            label_visibility='collapsed'
        )

    col1, col2 = st.columns(2)

    with col2:
        if resume_selector is not None:
            df_resume = get_entity_resume_UI(resume_selector)
            st.write('Резюме')
            st.dataframe(
                data=df_resume,
                hide_index=True,
                use_container_width=True
            )

    with col1:
        if vacancy_uploader is not None:
            save_uploadedfile(vacancy_uploader)
            st.write('Вакансия')
            df_vacancy = get_entity_vacancy_UI(vacancy_uploader.name)
            st.dataframe(
                data=df_vacancy,
                hide_index=True,
                use_container_width=True
            )

    if resume_uploader and vacancy_uploader is not None:
        df_similarity = calculate_avg_cosine_similarity(
            vacancy_uploader.name,
            resume_list
        )
        st.dataframe(
            data=df_similarity,
            hide_index=True,
            use_container_width=True
        )


if __name__ == '__main__':
    main()
