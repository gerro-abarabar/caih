import copy
from typing import List

import streamlit as st

from datafetch.exam_model import QuestionList
from utils.save_exam import save_exam
from utils.user_data import evolve_subject_progress, increment_exams_taken

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


def send_message(question_id, exam, chat_message_key, response_key):
    print("We are sending")
    user_input = st.session_state.get(chat_message_key, "")
    if user_input.strip() == "":
        print("No input provided")
        return
    else:
        question = None
        for question_list in exam:
            try:
                question = question_list.get_question(question_id)
                break
            except Exception:
                continue
        if question:
            ai_response = st.session_state.data.send_message(
                question,  # pyright: ignore
                user_input,
                """You are an expert, supportive AI tutor for high school students (grades 10-12) preparing for their college entrance exams. Your job is to help them understand exam questions and resolve their specific doubts in a friendly, conversational chatbot interface.

                You will receive two inputs:
                1. A structured data object representing an exam question (which may include the question text, multiple-choice options, correct answers, and references to images).
                2. A direct message from the student asking a question or expressing confusion.

                ### Instruction Guidelines:
                1. **Analyze the Data:** Thoroughly read the structured exam question data. If the question contains images or visual data, factor those details heavily into your reasoning.
                2. **Prioritize the Student's Doubt:** Answer the student's specific inquiry directly and immediately. Do not make them read through a massive wall of text to find the answer to their exact question.
                3. **Teach, Don't Just Reveal:** Break down the core academic concepts step-by-step. Explain *why* the correct answer is right and *why* common distractors/wrong options are incorrect. Match the academic level of a high school senior—rigorous but accessible.
                4. **Multi-Subject Adaptability:** Since the exam covers various subjects (Math, Science, Language, Reading, etc.), automatically adapt your explanation style. Use clear logic for STEM subjects and contextual analysis for humanities.

                ### Chatbot Formatting & Tone Rules:
                - **Tone:** Encouraging, patient, authoritative yet approachable, and motivating. Reduce exam anxiety.
                - **Formatting:** Write in clean, beautiful Markdown for a chat interface. Use bolding for key terms, bullet points for steps/reasons, and clear spacing. Avoid outputting raw JSON or code structures.""",
            )
            st.session_state[response_key] = ai_response
            # removed and relocated to line 112 area
            print("Message sent, AI response received:", ai_response)
        for key in st.session_state.keys():
            if "chat_response" in str(key):
                val = st.session_state[key]
                print(f"Key: {key} | Type: {type(val)} | Data: {str(val)[:20]}...")
    print("successfuly working")


def print_exam(exam: List[QuestionList], is_all=False):
    # print(exam)
    chat_opened = st.session_state.chat_opened
    opened_chats = st.session_state.opened_chats
    if chat_opened:
        questions, chat = st.columns([3, 1])
        with chat:
            st.markdown("## Chat")
            tabs = st.tabs([f"Q-{question_id}" for question_id in opened_chats.keys()])
            for i, question_id in enumerate(opened_chats.keys()):
                with tabs[i]:
                    st.markdown(f"### Question {question_id}")

                    response_key = f"chat_response_{question_id}"
                    chat_input_key = f"chat_input_{question_id}"
                    print(f"{response_key=}")

                    ai_stream = st.session_state.get(response_key, False)
                    print(f"{ai_stream=}")
                    # AI Message logic
                    if ai_stream:
                        print("AI stream found", ai_stream)
                        # Copy the string
                        message = st.session_state.get(chat_input_key, "")[:]
                        print(message)
                        # st.session_state[f"chat_input_{question_id}"] = (
                        #     ""  # Resets the text area
                        # )
                        if isinstance(ai_stream, str):
                            st.markdown(
                                f"{st.session_state.user_data['user']['name']}: {message}"
                            )
                            st.markdown(f"**AI:** {ai_stream}")

                        else:
                            status_container = st.empty()
                            message_container = st.empty()
                            full_message = ""

                            for chunk in ai_stream:
                                if chunk.message.thinking:  # Prints out the "AI is thinking..." message only once per question, and not for every chunk
                                    status_container.info("AI is thinking...")

                                if chunk.message.content:
                                    status_container.empty()

                                    full_message += chunk.message.content
                                    message_container.markdown(full_message + "▌")
                            message_container.markdown(full_message)
                            st.session_state[response_key] = (
                                full_message  # Saves the full message so it doesn't disappear when the component rerenders
                            )
                            st.rerun()

                    st.text_area(
                        "Your question to the AI",
                        key=chat_input_key,
                    )
                    st.button(
                        "Send",
                        key=f"chat_send_{question_id}",
                        on_click=send_message,
                        args=[question_id, exam, chat_input_key, response_key],
                    )

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
                if question.answer is None:
                    st.write("You did not answer this question")
                    pass
                else:
                    user_answer = question.get_choice(question.answer)
                    st.write(f"Your answer: {user_answer.choice}")  # pyright: ignore[reportOptionalMemberAccess]

                st.write(
                    f"Correct answer: {question.get_choice(question.correct_answer).choice}"  # pyright: ignore[reportOptionalMemberAccess]
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
                            st.session_state.asked_better_explanation = True
                            with st.spinner("Making better explanation..."):
                                # TODO: Fix it by using stream
                                response = st.session_state.data.remake_explanation(
                                    question
                                )
                                st.rerun()

                with col2:  # Ask chat for help
                    with st.container(
                        horizontal_alignment="center"
                    ):  # just so it looks better hehe
                        if st.button("Ask for help from AI", key=f"chat-{question.id}"):
                            st.session_state.chat_opened = True
                            st.session_state.opened_chats[question.id] = True
                            st.rerun()
        if not EXAM.is_lesson:
            if st.button("Create a new lesson"):
                create_lesson(EXAM)
        elif EXAM.is_lesson:  # if it is a lesson
            print("This is a lesson")
            if asked_better_explanation:
                if st.button("Save in Lesson"):
                    if st.session_state.lesson:
                        st.session_state.exam.types = exam
                        st.session_state.lesson.similar_exam = st.session_state.exam
                        st.session_state.data.save_lesson(
                            st.session_state.lesson, st.session_state.lesson.topic_title
                        )
                        st.success("Lesson saved successfully!")
                st.session_state.asked_better_explanation = False


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

if st.session_state.get("asked_better_explanation") is None:
    st.session_state.asked_better_explanation = False
    asked_better_explanation = False
else:
    asked_better_explanation = st.session_state.asked_better_explanation


score_type = st.toggle('Use "Right minus wrong"')
if CHOICES == {}:  # if no choices has been made
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

            except Exception:
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

        if CHOICES.get(str(i)) is None:
            continue
        print(f"{CHOICES=}")
        for question, answer in CHOICES.get(
            str(i), []
        ).values():  # ( Question, Answer )
            try:
                unanswered_questions[i].delete_question(question.id)
            except Exception:
                pass
            print(
                f"Question ID: {question.id}, User Answer: {answer.choice}, Correct Answer: {question.get_choice(question.correct_answer).choice}"
            )
            if answer.id == question.correct_answer:  # Correct
                print("youre right")
                wrong_questions[i].delete_question(question.id)
                print(f"{correct_questions[i].get_question(question.id)=}")
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

EXAM.score = score

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
    st.session_state.logged = False
    st.switch_page("main.py")

if not EXAM.saved:
    if st.button("Save Exam"):
        save_exam(EXAM)
        st.success("Successfully saved exam.")

if not st.session_state.get(
    "logged", False
):  # If it is new, (not saved, and not a lesson) and it hasnt been logged, then add it to our user data
    evolve_subject_progress(st.session_state.user_data, EXAM.subject_folder, score)
    st.session_state.logged = True
    print(f"saved score: {score}. to our levels")
    increment_exams_taken(st.session_state.user_data)
