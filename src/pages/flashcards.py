import streamlit as st

st.set_page_config(page_title="Flashcards")

flashcards_set = st.session_state.flashcards_set

st.title("Flashcards")
st.write(flashcards_set.topic)

flashcards = flashcards_set.flashcards

# TODO: Add image functionality after adding it in our lessons
for flashcard in flashcards:
    with st.expander(flashcard.question):
        st.write(flashcard.answer)
