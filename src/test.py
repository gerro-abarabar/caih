from streamlit.source_util import get_pages

pages = get_pages("main.py")
st.write(pages) # This will print a dictionary of all pages Streamlit "sees"