import streamlit as st


def login_section():
    """Login Section."""

    with st.form("login_form"):
        username = st.text_input("Usuari")
        pwd = st.text_input("Contrassenya")
        if st.form_submit_button("Inicia sessió"):
            user = st.session_state.db.get_user(username=username)
            if user is None:
                st.error("No existeix l'usuari")
            elif pwd != user.password:
                st.error("Contrassenya incorrecta")
            else:
                st.success("Log In")
                st.session_state.username = username
                st.session_state.name = user.name.capitalize()
                st.switch_page(st.Page("tabs/salut.py"))


def show():
    """
    Display Log In.

    This function displays the main page for managing pending payments. It allows the
    user to select a month, load the corresponding data, and either view existing debts
    or create a new debt sheet if no data is available.
    """
    st.title("Inicia Sessió")

    login_section()


show()
