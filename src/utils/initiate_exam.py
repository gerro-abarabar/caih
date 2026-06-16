import streamlit as st

from utils.timer import Timer


def initate_exam():
    st.session_state.question_type = 0
    st.session_state.exam = None
    st.session_state.choices = {}
    st.session_state.selected_buttons = {}
    st.session_state.timer = Timer()
    st.session_state.should_scroll = False
