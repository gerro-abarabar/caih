import streamlit as st
from streamlit_scroll_to_top import scroll_to_here

# 1. Initialize a session state variable to track the scroll trigger
if "should_scroll" not in st.session_state:
    st.session_state.should_scroll = False

# 2. Place the anchor right at the very top of your script execution
if st.session_state.should_scroll:
    st.session_state.should_scroll = False  # Reset it so it doesn't loop

# --- Dummy Content to fill page height ---
st.title("My App")
for i in range(100):
    st.write(f"Line of text {i}...")
# ----------------------------------------


# 3. Create a clean callback function for your button
def trigger_scroll():
    scroll_to_here(delay=0, key="top_anchor")


# Use a standard native Streamlit button
st.button("Scroll to Top", on_click=trigger_scroll)
