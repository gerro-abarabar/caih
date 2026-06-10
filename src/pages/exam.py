import time
from datetime import datetime

import streamlit as st


@st.cache_resource
def get_exam(amount, subject, _data_fetcher):
    exam = _data_fetcher.fetch_exam(amount, subject)
    # Pre-process images HERE so it only happens once
    for category in exam.types:
        for q in category.questions:
            for img in q.images:
                q.question = q.question.replace(
                    img.name, f"data:image/png;base64,{img.data}"
                )

    st.session_state.timer.start(st.session_state.time_amount)
    return exam


# Pass the dependencies as arguments
if st.session_state.exam is None:
    exam = get_exam(
        st.session_state.question_amount,
        st.session_state.subject,
        st.session_state.data,
    )
else:
    exam = st.session_state.exam
# print(exam)
st.title(exam.subject + " Exam")
timer = st.session_state.timer
if timer.ended:
    st.session_state.question_type = len(exam.types)
st.session_state.exam = exam
current_page_type = exam.types[min(st.session_state.question_type, len(exam.types) - 1)]

if timer.started:  # If there is an exam that has just been generated, it will show the timer, if there is no timer, it will not
    st.write(
        f"### Time left: {time.strftime('%M:%S', time.gmtime(timer.get_time_left()))}"
    )

exam.taken_at = datetime.now().isoformat()


def render_questions():
    exam_dict_key = current_page_type.instruction  # Grabs the instructions
    st.write("## " + exam_dict_key)
    for question in current_page_type.questions:
        if len(question.images) != 0:
            for image in question.images:
                question.question = question.question.replace(
                    image.name, f"data:image/png;base64,{image.data}"
                )
            st.markdown(
                f"#### {question.id}.  {question.question}", unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"#### {question.id}.  {question.question}", unsafe_allow_html=True
            )

        def on_choice_click(button_id, choice, selected_question):

            page_key = str(st.session_state.question_type)
            if st.session_state.choices.get(page_key) is None:
                st.session_state.choices[
                    page_key
                ] = {}  # Change from List [] to Dict {}

            # Removes any previous choice if the same button is clicked again
            # print(choice)
            if (
                st.session_state.choices[page_key].get(
                    selected_question.id, (None, None)
                )[1]
                == choice
            ):
                st.session_state.choices[page_key][selected_question.id] = (None, None)
                st.session_state.selected_buttons[selected_question.id] = None
                print(
                    "remove answer",
                )
                return
            st.session_state.selected_buttons[selected_question.id] = button_id
            # This overwrites any previous choice for this specific question ID
            st.session_state.choices[page_key][selected_question.id] = (
                selected_question,
                choice,
            )
            # print(
            #     "save answer",
            #     st.session_state.choices[str(st.session_state.question_type)],
            # )

        for i, choice in enumerate(question.choices):
            # st.session_state[f"button_{question.id}{choice.id.lower()}_value"] = st.session_state.get(f"button_{question.id}{choice.id.lower()}_value", 0)
            button_id = f"button_{question.id}{choice.id.lower()}"
            # print(button_id)
            st.button(
                f"{choice.choice}",
                on_click=on_choice_click,
                key=button_id,
                args=(
                    button_id,
                    choice,
                    question,
                ),
                use_container_width=False,
            )


if st.session_state.question_type < len(exam.types):
    render_questions()


# --- NAVIGATION LOGIC ---


# Define the callback functions
def next_page():
    st.session_state.question_type += 1


def go_back():
    if st.session_state.question_type > 0:
        st.session_state.question_type -= 1


if st.session_state.question_type < len(exam.types):
    # Create a layout for buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.question_type > 0:
            st.button("Go back", on_click=go_back)

    with col2:
        # Check if we are on the very last category/page
        if st.session_state.question_type < len(exam.types) - 1:
            st.button("Next", on_click=next_page)
        else:
            # This only shows on the absolute last page
            if st.button("Complete Exam", on_click=next_page):
                st.balloons()  # Optional flair!
                st.switch_page(
                    "pages/explanations.py"
                )  # Navigate to the explanations page after completing the exam

# --- SCORE DISPLAY ---
# This part handles the "Exam Completed" state
if st.session_state.question_type >= len(exam.types):
    st.switch_page("pages/explanations.py")

# INVISIBLE DATA

for button_key in st.session_state.selected_buttons.values():
    st.markdown(
        f"""
        <style>
        .st-key-{button_key} button {{
            color: #5f6814;
            background-color: #e6e9ef;
            border: 2px solid #5f6814;
            font-weight: bold;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <style>
    div.stButton {
        padding-left: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Instead of just st.rerun()
if not timer.ended:
    time.sleep(0.1)  # Prevents the script from pegged CPU usage
    st.rerun()
