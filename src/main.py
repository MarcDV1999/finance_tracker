from datetime import datetime

import streamlit as st

import src.utils.common as common
from src.db.database import DatabaseManager


def logout():
    """Logout."""
    st.session_state.username = None
    st.session_state.name = None


# count = st_autorefresh(interval=2000, key="fizzbuzzcounter")

# Create some session parameters
# Database
if "db" not in st.session_state:
    st.session_state.db = DatabaseManager()

# Date data
if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.now()
    st.session_state.current_month = common.get_month_name(
        st.session_state.current_date.month
    ).capitalize()
    st.session_state.current_year = str(st.session_state.current_date.year)

# User data
if "username" not in st.session_state:
    st.session_state.username = None
if "name" not in st.session_state:
    st.session_state.name = None

# Side Navigation Sections
# Fincanes tabs
finance_pages = {
    "Aquest mes": [
        st.Page(
            "tabs/salut.py",
            title="Salut Mensual",
            icon=":material/ecg_heart:",
            default=False,
        ),
        st.Page("tabs/deutes.py", title="Pendent", icon=":material/pending_actions:"),
    ],
}

# User Login/Signin Tabs
logged_out_user_pages = {
    "El meu compte": [
        st.Page(
            "tabs/login.py",
            title="Inicia Sessió",
            icon=":material/login:",
            default=True,
        ),
        st.Page(
            "tabs/signin.py",
            title="Registre",
            icon=":material/login:",
            default=False,
        ),
    ],
}


pages_dict = {}

# If no user logged in
if st.session_state.username is None:
    pages_dict = logged_out_user_pages
    st.sidebar.header("Inicia sessió o Registra't")
    st.sidebar.write(
        """
        Per a poder utilitzar l'app necessites iniciar sessió
        o registrar-te.
        """
    )
# If user logged id
else:
    pages_dict = finance_pages
    st.sidebar.markdown(f"## 👋 Hola :blue[{st.session_state.name.capitalize()}]!")
    st.sidebar.button(
        "Tanca Sessió", type="primary", use_container_width=True, on_click=logout
    )

# Show side bar
pg = st.navigation(pages_dict)
pg.run()
