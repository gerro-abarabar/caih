import copy
import json
from typing import List, Optional

import streamlit as st

from datafetch.exam_model import Exam, Question, QuestionList

st.set_page_config(layout="wide")


def lower_headings(markdown: str, amount: int = 1):
    line_by_line = markdown.split("\n")
    new_lines = []

    for line in line_by_line:
        if line.startswith("#"):
            # Add the extra hashes to the start
            new_lines.append("#" * amount + line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


@st.cache_resource
def create_lesson(exam: List[QuestionList]):
    st.session_state.lesson = st.session_state.data.create_lesson(exam)
    st.switch_page("pages/lesson.py")


# These are ids of questions that have been clicked to be able to ask AI.
if "opened_chats" not in st.session_state:
    st.session_state.opened_chats = {}


if "chat_opened" not in st.session_state:
    st.session_state.chat_opened = False
    print("Initialized chat_opened to False")


def print_exam(exam: List[QuestionList], is_all=False):
    # print(exam)
    chat_opened = st.session_state.chat_opened
    opened_chats = st.session_state.opened_chats
    print("Opened chats", chat_opened)
    if chat_opened:
        questions, chat = st.columns([3, 1])
        with chat:
            st.markdown("## Chat")
            tabs = st.tabs([str(question_id) for question_id in opened_chats.keys()])
            for i, question_id in enumerate(opened_chats.keys()):
                with tabs[i]:
                    st.markdown(f"### Question {question_id}")
                    ai_stream = st.session_state.get(
                        f"chat_response_{question_id}", False
                    )
                    if ai_stream:
                        if not st.session_state.get("in_thinking", False):
                            st.session_state.in_thinking = False
                        print("AI stream found", ai_stream)
                        for chunk in ai_stream:
                            if chunk.message.thinking:  # Prints out the "AI is thinking..." message only once per question, and not for every chunk
                                if not st.session_state.in_thinking:
                                    st.markdown(f"**AI is thinking...**")
                                    st.session_state.in_thinking = True
                            elif chunk.message.content:
                                if st.session_state.in_thinking:
                                    st.session_state.in_thinking = False
                                    st.markdown(f"**AI:**")
                                st.markdown(chunk.message.content)
                                print("Chunk content", chunk.message.content)
                            st.rerun()

                    st.text_area(
                        "Your question to the AI",
                        key=f"chat_input_{question_id}",
                    )
                    if st.button("Send", key=f"chat_send_{question_id}"):
                        user_input = st.session_state[f"chat_input_{question_id}"]
                        if user_input.strip() == "":
                            st.warning("Please enter a question before sending.")
                        else:
                            with st.spinner("Getting AI response..."):
                                for question_list in exam:
                                    try:
                                        question = question_list.get_question(
                                            question_id
                                        )
                                        break
                                    except Exception:
                                        st.error("Question not found.")
                                        return
                                print("Question found", question)
                                ai_response = st.session_state.data.send_message(
                                    question,  # pyright: ignore
                                    user_input,
                                    "You are an expert tutor. Answer the question as best as you can, and give detailed explanations. If the question has images, take them into account when answering.",  # TODO: make this prompt better
                                )
                                st.session_state[f"chat_response_{question_id}"] = (
                                    ai_response
                                )
                                st.rerun()
    else:
        questions = st.container()
    with questions:
        for question_list in exam:
            if len(question_list.questions) == 0:
                continue
            st.markdown(f"# {question_list.instruction}")

            for question in question_list.questions:
                st.markdown(
                    f"## {question.id}.  {question.question}", unsafe_allow_html=True
                )
                if question.answer == None:
                    st.write("You did not answer this question")
                    pass
                else:
                    user_answer = question.get_choice(question.answer)
                    st.write(f"Your answer: {user_answer.choice}")

                st.write(
                    f"Correct answer: {question.get_choice(question.correct_answer).choice}"
                )
                st.write(
                    "---"
                    + "\n\n"
                    + lower_headings(question.explanation, 1)
                    + "\n\n"
                    + "---",
                    unsafe_allow_html=True,
                )
                col1, col2 = st.columns(2)
                with col1:  # Ask for better explanation
                    with st.container(
                        horizontal_alignment="center"
                    ):  # just so it looks better hehe
                        if st.button(
                            "Ask for better explanation",
                            key=f"explanation-{question.id}",
                        ):
                            print(question.explanation)
                            with st.spinner("Making better explanation..."):
                                question.explanation = (
                                    st.session_state.data.remake_explanation(question)
                                )
                                st.rerun()

                with col2:  # Ask chat for help
                    with st.container(
                        horizontal_alignment="center"
                    ):  # just so it looks better hehe
                        if st.button("Ask for help from AI", key=f"chat-{question.id}"):
                            print("Opening chat")
                            st.session_state.chat_opened = True
                            st.session_state.opened_chats[question.id] = True
                            st.rerun()
        if not EXAM.is_lesson:
            if st.button("Create a new lesson"):
                create_lesson(exam)


st.title("Explanations")

st.write("# Completed Exam")


CHOICES = st.session_state.choices

score = 0
correct_questions = []
unanswered_questions = []
wrong_questions = []

EXAM = st.session_state.exam

total_questions = sum(len(page.questions) for page in EXAM.types)

CORRECT = 1
UNANSWERED = 0
WRONG = 2


score_type = st.toggle('Use "Right minus wrong"')
if CHOICES == {}:  # if no choices has been made
    print("No choices have been made")
    for i, page in enumerate(
        EXAM.types
    ):  # Page: (questions,[questions]),(instructions,"instruction")
        # page=dict(page)

        unanswered_questions.append(copy.deepcopy(page))
        correct_questions.append(copy.deepcopy(page))
        wrong_questions.append(copy.deepcopy(page))
        # print("Un answered",unanswered_questions)

        for question in page.questions:
            try:
                correct_questions[i].delete_question(question.id)
                wrong_questions[i].delete_question(question.id)

            except:
                pass
else:
    for i, page in enumerate(
        EXAM.types
    ):  # Page: (questions,[questions]),(instructions,"instruction")
        # page=dict(page)

        unanswered_questions.append(copy.deepcopy(page))
        correct_questions.append(copy.deepcopy(page))
        wrong_questions.append(copy.deepcopy(page))
        # print("Un answered",unanswered_questions)
        # print(f"{CHOICES=}")
        for question, answer in CHOICES.get(str(i), []):
            try:
                unanswered_questions[i].delete_question(question.id)
            except:
                pass
            print(question, "Rizzer")
            if answer.id == question.correct_answer:  # Correct
                print("youre right")
                wrong_questions[i].delete_question(question.id)
                correct_questions[i].add_answer(question.id, answer.id)
                page.add_answer(question.id, answer.id)  # Puts back the original answer
                score += 1
            else:  # Wrong
                print("youre wron")
                correct_questions[i].delete_question(question.id)
                wrong_questions[i].add_answer(question.id, answer.id)
                page.add_answer(question.id, answer.id)  # Puts back the original answer
                if score_type:
                    score -= 0.25


st.write(f"Your final score is {max(score, 0)}/{total_questions}.")

question_type = st.radio(
    "Select question type to review:", ("All", "Correct", "Wrong", "Unanswered")
)

if question_type == "Correct":
    print_exam(correct_questions)
elif question_type == "Wrong":
    print_exam(wrong_questions)
elif question_type == "Unanswered":
    print_exam(unanswered_questions)
else:
    print_exam(EXAM.types)

if st.button("Go Home"):
    st.switch_page("main.py")
