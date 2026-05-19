import streamlit as st

from utils.user_data import DEFAULT_DATA, get_data_file, load_user_data, save_user_data

st.set_page_config(page_title="User Profile", layout="centered")
st.title("User Profile")


# -----------------------------------------------------------------------------
# Main app logic
# -----------------------------------------------------------------------------

DATA_FILE = get_data_file()
user_data = load_user_data(DATA_FILE)
user = user_data.get("user", DEFAULT_DATA["user"])  # convenience reference

# Header / profile display
col_avatar, col_info = st.columns([1, 3])
with col_avatar:
    avatar_url = user.get("avatar_url", "")
    if avatar_url:
        st.image(avatar_url, width=120)
    else:
        # lightweight placeholder image
        st.markdown("![avatar](https://via.placeholder.com/120)")

with col_info:
    st.markdown(f"**Name:** {user.get('name', '')}")
    st.markdown(f"**Username:** {user.get('username', '')}")
    st.markdown(f"**Email:** {user.get('email', '')}")
    st.markdown("**Bio:**")
    st.write(user.get("bio", ""))

# Session state: toggle an edit form reliably
if "editing_profile" not in st.session_state:
    st.session_state["editing_profile"] = False

_, action_col = st.columns([6, 1])
with action_col:
    if st.session_state["editing_profile"]:
        if st.button("Cancel", key="cancel_edit"):
            st.session_state["editing_profile"] = False
            st.rerun()
    else:
        if st.button("Edit", key="start_edit"):
            st.session_state["editing_profile"] = True
            st.rerun()

# Edit form
if st.session_state["editing_profile"]:
    with st.form("edit_profile_form"):
        name = st.text_input("Full name", value=user.get("name", ""))
        username = st.text_input("Username", value=user.get("username", ""))
        email = st.text_input("Email", value=user.get("email", ""))
        avatar_url = st.text_input("Avatar URL", value=user.get("avatar_url", ""))
        bio = st.text_area("Bio", value=user.get("bio", ""), height=120)

        # Preferences (simple example)
        prefs = user.get("preferences", {})
        theme = st.selectbox(
            "Theme",
            ["light", "dark"],
            index=0 if prefs.get("theme", "light") == "light" else 1,
        )
        notifications = st.checkbox(
            "Email notifications", value=prefs.get("notifications", True)
        )

        submitted = st.form_submit_button("Save")

        if submitted:
            # Update the in-memory structure and persist
            user_update = {
                "name": name,
                "username": username,
                "email": email,
                "avatar_url": avatar_url,
                "bio": bio,
                "preferences": {"theme": theme, "notifications": notifications},
            }

            user_data["user"] = user_update
            save_user_data(DATA_FILE, user_data)

            st.success("Profile updated.")
            st.session_state["editing_profile"] = False
            st.rerun()

# Developer / future-facing debug view
with st.expander("Raw user data (for developers)"):
    st.json(user_data)
