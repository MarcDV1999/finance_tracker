from datetime import datetime

import streamlit as st

import src.utils.common as common

# count = st_autorefresh(interval=2000, key="fizzbuzzcounter")

# st.session_state.current_month = datetime.now().strftime("%B")
st.session_state.current_month = common.get_month_name(
    datetime.now().month
).capitalize()
st.session_state.current_year = str(datetime.now().year)
st.session_state.current_date = datetime.now()

pages = {
    "Your account": [
        st.Page("tabs/login.py", title="Inicia Sessió", icon=":material/login:"),
    ],
    "Aquest mes": [
        st.Page(
            "tabs/salut.py",
            title="Salut Mensual",
            icon=":material/ecg_heart:",
            default=True,
        ),
        st.Page("tabs/deutes.py", title="Pendent", icon=":material/pending_actions:"),
    ],
}

pg = st.navigation(pages)
pg.run()
