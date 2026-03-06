import json

import streamlit as st

st.title("Explanations")

st.write("# Completed Exam")

# Score
score = st.session_state.score

final_score=0
unanswered_questions={}
wrong_questions={}

# flatten exam
flattened_exam = [question for instruction in st.session_state.exam.values() for question in instruction]
total_questions = len(flattened_exam)
CORRECT = 1
print("score ",score)
for num, result in score.items():
    print(num)
    if result == CORRECT: # Correct answer
        final_score += 1
    else:
        if result == 0: # No answer
            unanswered_questions[num]=flattened_exam[num-1]
        else: # Wrong answer
            wrong_questions[num]=flattened_exam[num-1]
st.write(f"Your final score is {final_score}/{total_questions}.")

question_type = st.radio("Select question type to review:", ("All", "Wrong", "Unanswered"))

if question_type == "All":
    questions_to_review = zip(range(1, total_questions + 1), flattened_exam)
elif question_type == "Wrong":
    questions_to_review = wrong_questions.items()
elif question_type == "Unanswered":
    questions_to_review = unanswered_questions.items()

for num, question in questions_to_review:
    print(num)
    # print(question)
    st.markdown(f"### Question {num}: {question['question']}", unsafe_allow_html=True)
    st.markdown(f"**Your answer:** {score[num]}", unsafe_allow_html=True)
    st.markdown(f"**Correct answer:** {question['choices'][question['correct_answer']]}", unsafe_allow_html=True)
    st.markdown(f"**Explanation:** \n{question['explanation']}", unsafe_allow_html=True)
