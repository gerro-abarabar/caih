import time
from datetime import datetime

import streamlit as st
from streamlit_scroll_to_top import scroll_to_here

if st.session_state.should_scroll:
    scroll_to_here(delay=0, key="top_anchor")
    # st.session_state.should_scroll = False


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
            image_in_question = False
            for image in question.images:
                if image.name in question.question:
                    question.question = question.question.replace(
                        image.name, f"data:image/png;base64,{image.data}"
                    )
                    image_in_question = True
            st.markdown(
                f"#### {question.id}.  {question.question}", unsafe_allow_html=True
            )
            if not image_in_question:
                for image in question.images:
                    base64_str = str(image.data.decode("utf-8")).strip()
                    # TODO: Make this work in mathematics.json
                    # Determine the correct MIME type based on the starting characters
                    if base64_str.startswith("/9j/"):
                        mime_type = "image/jpeg"
                    elif base64_str.startswith("iVBORw0KGg"):
                        mime_type = "image/png"
                    elif base64_str.startswith("R0lGOD"):
                        mime_type = "image/gif"
                    else:
                        mime_type = "image/png"  # Default fallback

                    data_url = f"data:{mime_type};base64,{base64_str}"

                    st.image(
                        data_url, caption=image.description, use_container_width=True
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


def trigger_scroll():
    st.session_state.should_scroll = True


# Define the callback functions
def next_page():
    trigger_scroll()  # Set the flag to trigger scrolling on the next rerun

    st.session_state.question_type += 1


def go_back():
    trigger_scroll()  # Set the flag to trigger scrolling on the next rerun

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
if (
    not timer.ended and not st.session_state.should_scroll
):  # Would stop rerunning if the user is scrolling to top
    time.sleep(0.1)  # Prevents the script from pegged CPU usage
    st.rerun()
