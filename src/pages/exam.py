import json

import streamlit as st

st.title("Exam Page")

@st.cache_data
def get_exam():
    exam = st.session_state.data.fetch_exam()
    sorted= {question["instruction"]:[] for question in exam} # Sorts by instruction of every item
    
    for question in exam:
        sorted[question["instruction"]].append(question)
    return sorted
exam=get_exam()
# print(json.dumps(exam,indent=4))
exam_dict_key =list(exam.keys())[st.session_state.question_type] # Grabs the instructions
st.write(exam_dict_key)
for question in exam[exam_dict_key]:
    st.write(question["question"])
    def on_choice_click(choice,num):
        selected_button = st.session_state.get(f"button_{num}{choice[0].lower()}")
        print(choice)
        if choice[0].lower() == "abcd"[question["correct_answer"]]:
            print("Correct!")
            st.session_state.score[num]=st.session_state.score.get(num,0)+1
        else:
            print("Wrong.")
            st.session_state.score[num]=st.session_state.score.get(num,0)-1 # TODO - add a feedback system later on, or tell them if it's right or wrong
        
        for choice in question["choices"]:
            choice_name=f"button_{num}{choice[0].lower()}_value"
            st.session_state[choice_name] = True
            print(f"{choice_name} = {st.session_state[choice_name]}")
            # st.button(choice, disabled=True, key=f"button_{num}{choice[0].lower()}" )=False
    
    
    for choice in question["choices"]:
        st.session_state[f"button_{question['id']}{choice[0].lower()}_value"] = st.session_state.get(f"button_{question['id']}{choice[0].lower()}_value", False) # Initialize state for each button
        print(f"Initialized button_{question['id']}{choice[0].lower()}_value to {st.session_state[f'button_{question['id']}{choice[0].lower()}_value']}")
        st.button(
            choice, 
            on_click=on_choice_click, 
            key=f"button_{question['id']}{choice[0].lower()}", 
            args=(choice,question["id"]),
            disabled=st.session_state[f"button_{question['id']}{choice[0].lower()}_value"]
            )
        


if st.button("Go back"):
    st.switch_page("main.py")