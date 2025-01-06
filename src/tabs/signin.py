import streamlit as st


def signin_section():
    with st.form("signin_form"):
        name = st.text_input("Nom")
        username = st.text_input("Usuari")
        pwd = st.text_input("Contrassenya")
        if st.form_submit_button("Registra't"):
            user = st.session_state.db.get_user(username=username)
            if user:
                st.error("L'usuari ja existeix")
            else:
                st.session_state.db.add_user(name=name, username=username, password=pwd)
                st.success("Usuari registrat!")
                st.session_state.username = username
                st.session_state.name = name.capitalize()
                st.switch_page(st.Page("tabs/salut.py"))


def show():
    """
    Display Log In.

    This function displays the main page for managing pending payments. It allows the
    user to select a month, load the corresponding data, and either view existing debts
    or create a new debt sheet if no data is available.
    """
    st.title("Registre")

    signin_section()


show()
