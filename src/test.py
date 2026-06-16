import streamlit as st

st.title("Test Page")
container = st.container()
with container:
    st.write("This is a test container.")

if st.button("Empty container"):
    container.empty()
