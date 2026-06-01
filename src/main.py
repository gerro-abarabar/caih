# marker_single assets/language-profeciency-example.pdf --output_format json --ollama_base_url http://localhost:11434 --ollama_model gemini-3-flash-preview:cloud --llm_service=marker.services.ollama.OllamaService --output_dir language-profeciency-example.md --force_ocr --debug --disable_image_extraction

import os

import streamlit as st

from datafetch import DataFetcher
from utils.flashcards import get_flashcard_topics, get_flashcards
from utils.initiate_exam import initate_exam
from utils.save_exam import get_exam, get_exam_files
from utils.user_data import get_data_file, load_user_data, save_user_data

st.set_page_config(page_title="Exam Generator")
SUBJECTS = [
    subject.capitalize()
    for subject in [
        subject
        for subject in os.listdir("assets")
        if os.path.isdir(os.path.join("assets", subject))
    ]
]

st.title("CAIH")

DATA_FILE = get_data_file()
user_data = load_user_data(DATA_FILE)
st.session_state.user_data = (
    user_data  # Store in session state for easy access across pages
)

progress_data = user_data.get("progress", {})
for subject in progress_data.get("subjects", []):
    if not progress_data.get(subject.lower(), False):
        progress_data[subject.lower()] = 0


st.header(f"Welcome back, **{user_data.get('user', {}).get('name', 'User')}**!")

levels_expander = st.expander("See your progress")

with levels_expander:
    st.write(f"- Exams Taken: {progress_data.get('exams_taken', 0)}")
    st.write(f"- Lessons Completed: {progress_data.get('lessons_completed', 0)}")
    st.write(f"- Flashcards Reviewed: {progress_data.get('flashcards_reviewed', 0)}")
    for subject, value in progress_data.get("subjects", {}).items():
        with st.container():
            st.markdown(f"#### {subject.capitalize()}")
            level, progress = st.columns([1, 4])
            with level:
                st.markdown(f"Level: {value // 100}")
            with progress:
                st.progress(value % 100)

save_user_data(DATA_FILE, user_data)

exam_page, lessons_page, flashcards_page, saved_exams_page = st.tabs(
    ["Generate Exam", "Lessons", "Flashcards", "Saved Exams"]
)
with exam_page:
    st.write("Click the button below to generate a new exam.")
    start = st.button("Generate Exam")
    st.session_state.subject = st.selectbox(
        "Select what type of exam you want to generate",
        options=SUBJECTS,
    )
    question_amount = st.slider(
        "Select number of questions for the exam",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
    )
    time_amount = st.slider(
        "Set time limit for the exam (mins)",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
    )
    st.session_state.data = DataFetcher()
    datafetcher = st.session_state.data

with lessons_page:
    st.write("## Pick your latest lessons")
    with st.container(horizontal_alignment="left", border=True):
        for i, lesson in enumerate(datafetcher.get_lessons()[::-1]):
            if st.button(f"{i + 1}. {lesson[:-7]}", args=[lesson]):
                st.session_state.lesson = datafetcher.get_lesson(lesson)
                st.switch_page("pages/lesson.py")

with flashcards_page:
    st.write("## Flashcards")
    with st.container(horizontal_alignment="left", border=True):
        for i, topic in enumerate(get_flashcard_topics()):
            if st.button(f"{i + 1}. {topic}", args=[topic], key=f"flashcard_{topic}"):
                st.session_state.flashcards_set = get_flashcards(topic)
                st.switch_page("pages/flashcards.py")

with saved_exams_page:
    st.write("## Saved Exams")
    with st.container(horizontal_alignment="left", border=True):
        for i, exam in enumerate(get_exam_files()[::-1]):
            if st.button(
                f"{i + 1}. {exam[:-5]}", args=[exam], key=f"saved_exam_{exam}"
            ):
                initate_exam()  # forgive me for my bad spelling
                st.session_state.exam = get_exam(exam)
                st.session_state.exam.is_lesson = False

                st.switch_page("pages/exam.py")

if start:
    st.cache_resource.clear()
    st.session_state.question_amount = question_amount
    st.session_state.time_amount = time_amount * 60  # Converts into seconds
    initate_exam()

    st.switch_page("pages/exam.py")

st.write("---")
if st.button("Edit User Profile"):
    st.switch_page("pages/user.py")
