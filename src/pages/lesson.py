import streamlit as st

from utils.flashcards import (
    save_text_to_flashcard,
)
from utils.initiate_exam import initate_exam


def format_tabs(text: str, tab_amount: int = 8):
    return f"{'&nbsp;' * tab_amount}{('&nbsp;' * 8).join(text.split('\n'))}"


lesson = st.session_state.lesson

st.title(lesson.topic_title)
# st.write("First column&nbsp;&nbsp;&nbsp;&nbsp;Second column")

core_explanations_tab, historical_context_tab, memory_aids_tab = st.tabs(
    ["Core Explanations", "Historical Context", "Memory Aids"]
)

with core_explanations_tab:
    st.write(f"{'&nbsp;' * 8}{lesson.core_explanation}")

with historical_context_tab:
    st.write(f"{'&nbsp;' * 8}{lesson.historical_context}")

with memory_aids_tab:
    memory_aids = lesson.memory_aids

    if len(memory_aids) == 0:
        st.write("No memory aids available for this lesson.")

    else:
        for mnemonic in memory_aids:
            st.write(f"**{mnemonic.tool}**: {mnemonic.application}")
        if st.button("Save as Flashcards"):
            for mnemonic in memory_aids:
                save_text_to_flashcard(
                    question=mnemonic.tool,
                    answer=mnemonic.application,
                    images=mnemonic.images,
                    topic=lesson.topic_title,
                )
            st.success("Flashcards saved successfully!")


st.write("---")

col1, col2, col3 = st.columns(3)
with col1:
    try_exam = st.button("Try the Exam")
with col2:
    if not lesson.saved:
        if st.button("Save Lesson"):
            st.session_state.data.save_lesson(lesson, lesson.topic_title)

with col3:
    go_home = st.button("Go Home")


if go_home:
    st.switch_page("main.py")

if try_exam:
    initate_exam()
    lesson.similar_exam.saved = True
    st.session_state.exam = lesson.similar_exam
    st.switch_page("pages/exam.py")

if not lesson.similar_exam.is_lesson:
    lesson.similar_exam.is_lesson = True
