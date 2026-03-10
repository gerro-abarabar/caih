# marker_single assets/language-profeciency-example.pdf --output_format json --ollama_base_url http://localhost:11434 --ollama_model gemini-3-flash-preview:cloud --llm_service=marker.services.ollama.OllamaService --output_dir language-profeciency-example.md --force_ocr --debug --disable_image_extraction

from datafetch import DataFetcher
import streamlit as st

st.session_state.data = DataFetcher()

st.set_page_config(
    page_title="Exam Generator"
)

if 'exam' not in st.session_state:
    st.session_state.exam = None
if 'explanation' not in st.session_state:
    st.session_state.explanation = None


print("In main page")
st.title("Welcome to the Exam Generator!")
st.write("Click the button below to generate a new exam.")
start = st.button("Generate Exam")

st.session_state.question_amount = st.slider("Select number of questions for the exam", min_value=1, max_value=100, value=10, step=1)
if start:
    st.session_state.question_type=0
    st.session_state.score={}
    st.switch_page("pages/exam.py")
    print("Now going to exam page")

