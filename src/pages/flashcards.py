import matplotlib.pyplot as plt
import streamlit as st
from streamlit_theme import st_theme

from utils.flashcard_model import FlashcardSet

st.set_page_config(page_title="Flashcards")

flashcards_set: FlashcardSet = st.session_state.flashcards_set

st.title("Flashcards")
st.write(flashcards_set.topic)

flashcards = flashcards_set.flashcards

st.session_state.flashcard_index = st.session_state.get("flashcard_index", 0)
index = st.session_state.flashcard_index
st.session_state.show_flashcard = st.session_state.get("show_flashcard", False)


if index < len(flashcards):
    curr_flashcard = flashcards[index]

    with st.container(horizontal_alignment="center", border=True, height=200):
        if st.button(
            curr_flashcard.question,
            use_container_width=True,
            key="flashcard_button",
        ):
            st.session_state.show_flashcard = not st.session_state.show_flashcard
        show_flashcard = st.session_state.show_flashcard
        if show_flashcard:
            st.write(curr_flashcard.answer)

    st.session_state.score = st.session_state.get("score", 0)

    correct, wrong = st.columns(2)
    with correct:
        with st.container(horizontal_alignment="center"):
            if st.button("", icon=":material/check:", use_container_width=True):
                st.session_state.score += 1
                st.session_state.flashcard_index += 1
                st.success("Nice one!")
                st.session_state.show_flashcard = False
                st.rerun()

    with wrong:
        with st.container(horizontal_alignment="center"):
            if st.button("", icon=":material/close:", use_container_width=True):
                st.session_state.flashcard_index += 1
                st.error("Better luck next time!")
                st.session_state.show_flashcard = False
                st.rerun()
    if index > len(flashcards):
        st.session_state.flashcard_index = 0

else:
    st.write("## You finished it! Good job!")
    labels = ["Correct", "Wrong"]
    sizes = [st.session_state.score, len(flashcards) - st.session_state.score]
    theme = st_theme()
    plt.style.use("dark_background") if theme["base"] == "dark" else 0  # pyright: ignore[reportOptionalSubscript]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Ensures the pie is drawn as a circle

    st.pyplot(fig)
    if st.button("Save to Anki"):
        flashcards_anki = ""
        for flashcard in flashcards:
            flashcards_anki += f"{flashcard.question}\t{flashcard.answer}\n"
        file_name = f"{flashcards_set.topic}_flashcards.txt"
        with open(file_name, "w") as f:
            f.write(flashcards_anki)
        st.success(f"Flashcards saved as {file_name} for Anki import!")

    if st.button("Go home"):
        st.session_state.score = 0
        st.switch_page("main.py")
