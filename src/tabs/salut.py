from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import src.utils.common as common
from src.config import EXPENSE_TYPES
from src.utils.logger import logger_all


def prep_expenses_df(expenses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares the expenses DataFrame by ensuring correct data types for its columns.

    Parameters
    ----------
    expenses_df : pd.DataFrame
        The DataFrame containing expense data to be processed.

    Returns
    -------
    pd.DataFrame
        The processed DataFrame with standardized column data types.

    Notes
    -----
    The function enforces the following column data types:
    - "concept" : str
    - "amount" : float
    - "category" : str
    """
    # Ensure the DataFrame columns have the expected data types.
    expenses_df = expenses_df.astype({"concept": str, "amount": float, "category": str})

    return expenses_df


def load_data(current_date: date, create: None | str = "empty"):
    """
    Loads and initializes session data for expense tracking.

    Parameters
    ----------
    current_date : date
        The current date for which expense data should be loaded.
    create : str or None, optional
        Specifies the action to take if no expense file exists for the current date.
        Options include:
        - "empty" (default): Create an empty file.
        - "duplicate": Duplicate data from the previous month.
        - None: Do not create any file.

    Notes
    -----
    Updates the Streamlit session state with the following:
    - Previous expenses filepath and associated metadata.
    - Current expenses filepath and associated metadata.
    - Loads the corresponding DataFrames into session state.
    """

    st.session_state.expenses_df = st.session_state.db.get_user_expenses(
        username=st.session_state.username,
        date=current_date,
    )

    st.session_state.prev_expenses_df, prev_date = (
        st.session_state.db.get_prev_user_expenses(
            username=st.session_state.username,
            date=current_date,
        )
    )

    # Update prev_date
    if prev_date:
        st.session_state.prev_month_name = prev_date.strftime("%B").lower()
        st.session_state.prev_year = str(prev_date.year)
        st.session_state.prev_date = prev_date
    else:
        st.session_state.prev_month_name = None
        st.session_state.prev_year = None
        st.session_state.prev_date = None

    # Create expenses sheet

    print(st.session_state.expenses_df)
    print(st.session_state.prev_expenses_df)
    print()
    print()


def load_data2(current_date: date, create: None | str = "empty"):
    """
    Loads and initializes session data for expense tracking.

    Parameters
    ----------
    current_date : date
        The current date for which expense data should be loaded.
    create : str or None, optional
        Specifies the action to take if no expense file exists for the current date.
        Options include:
        - "empty" (default): Create an empty file.
        - "duplicate": Duplicate data from the previous month.
        - None: Do not create any file.

    Notes
    -----
    Updates the Streamlit session state with the following:
    - Previous expenses filepath and associated metadata.
    - Current expenses filepath and associated metadata.
    - Loads the corresponding DataFrames into session state.
    """
    # Fetch the previous expenses file and metadata.
    prev_expenses_filepath, prev_date = common.get_previous_file(
        current_date, "expenses.csv"
    )

    # Update session state with previous file data.
    st.session_state.prev_expenses_filepath = prev_expenses_filepath
    st.session_state.prev_date = prev_date
    st.session_state.prev_year = str(prev_date.year) if prev_date else None
    st.session_state.prev_month_name = (
        common.get_month_name(prev_date.month) if prev_date else None
    )

    # Load the previous expenses DataFrame if it exists.
    if isinstance(prev_expenses_filepath, Path) and prev_expenses_filepath.exists():
        st.session_state.prev_expenses_df = common.load_csv(
            filepath=prev_expenses_filepath
        )
        st.session_state.prev_expenses_df = prep_expenses_df(
            st.session_state.prev_expenses_df
        )
    else:
        # Initialize an empty DataFrame if no previous expenses are found.
        st.session_state.prev_expenses_df = pd.DataFrame(
            columns=["concept", "amount", "category"]
        )
        st.toast("No hi ha despeses de mesos passats!", icon=":material/warning:")

    # Load the current expenses file.
    expenses_filepath = common.load_file(current_date, filename="expenses.csv")

    # Update session state with current file data.
    st.session_state.expenses_filepath = expenses_filepath
    st.session_state.current_date = current_date
    st.session_state.current_year = str(current_date.year)
    st.session_state.current_month_name = common.get_month_name(current_date.month)

    # Load or initialize the current expenses DataFrame based on file existence.
    if st.session_state.expenses_filepath.exists():
        logger_all.info(f"Existeix la data {st.session_state.expenses_filepath}")
        st.session_state.expenses_df = common.load_csv(filepath=expenses_filepath)
        st.session_state.expenses_df = prep_expenses_df(st.session_state.expenses_df)
    elif create is None:
        logger_all.info("No es crea")
        st.session_state.expenses_df = None
    elif create == "empty":
        logger_all.info("Es crea buit")
        st.session_state.expenses_df = pd.DataFrame(
            columns=["concept", "amount", "category"]
        )
        common.export_csv(st.session_state.expenses_df, expenses_filepath)
        st.toast("S'ha creat un nou full de despeses buit", icon=":material/info:")
    elif create == "duplicate" and prev_expenses_filepath.exists():
        logger_all.info(f"Es duplica de {prev_expenses_filepath}")
        st.session_state.expenses_df = common.load_csv(filepath=prev_expenses_filepath)
        st.session_state.expenses_df = prep_expenses_df(st.session_state.expenses_df)
        common.export_csv(st.session_state.expenses_df, expenses_filepath)
        st.toast(
            f"S'ha creat un nou full de despeses basat en el mes de "
            f"{st.session_state.prev_month_name} de {st.session_state.prev_year}",
            icon=":material/info:",
        )
    else:
        logger_all.error("No s'ha pogut carregar les despeses del mes seleccionat")


def plot_health(df: pd.DataFrame, salary: int):
    """
    Creates and displays a stacked bar chart showing expenses and savings.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing expense data with columns "category" (type) and "amount" (amount).
    salary : int
        The total monthly salary, used to calculate savings.

    Notes
    -----
    The function calculates savings as the difference between the salary and total expenses,
    groups the data by expense type, and plots a horizontal stacked bar chart with customized
    colors for each type.
    """
    # Calculate savings and add it as a new row.
    estalvi_row = dict(tipus="estalvi", total=salary - df["amount"].sum())
    df = pd.concat([df, pd.DataFrame([estalvi_row])], ignore_index=True)

    # Round the "amount" column to avoid decimals.
    df["amount"] = df["amount"].round(0)

    # Group data by "category" and sum totals.
    df_grouped = df.groupby("category", as_index=False)["amount"].sum()

    # Ensure the categories are displayed in a specific order.
    order = list(EXPENSE_TYPES.keys()) + ["estalvi"]
    df_grouped["category"] = pd.Categorical(
        df_grouped["category"], categories=order, ordered=True
    )
    df_grouped = df_grouped.sort_values("category")

    # Create a color map based on expense types.
    color_map = {
        type_name: data.get("color", None) for type_name, data in EXPENSE_TYPES.items()
    }

    # Generate the bar chart using Plotly.
    fig = px.bar(
        df_grouped,
        x="amount",
        y=["Despeses"] * len(df_grouped),  # Placeholder for consistent formatting.
        orientation="h",
        title="Despeses",
        labels={
            "amount": "Total (€)",
            "category": "Tipus de despesa",
            "x": "",
            "y": "",
        },
        color="category",
        height=300,
        barmode="stack",
        text="amount",
        color_discrete_map=color_map,
    )

    # Customize text inside the bars.
    fig.update_traces(
        texttemplate="%{text} €", textposition="inside", insidetextanchor="middle"
    )

    # Display the chart in Streamlit.
    st.plotly_chart(fig, use_container_width=True)


def show_editable_df(df: pd.DataFrame, tipus: str):
    """
    Displays an editable table for a specific expense type, allowing modifications.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing expense data with columns 'nom', "amount", and "category".
    tipus : str
        The expense type to filter and display.

    Notes
    -----
    The function filters the DataFrame for the specified type, shows an editable table,
    and updates the data if changes are made. Changes are saved to a CSV file, and the app
    reloads the updated data.
    """
    # Capitalize the 'nom' column for consistency.
    df["concept"] = df["concept"].str.capitalize()

    # Filter the DataFrame to only include rows of the specified type.
    mask = df["category"] == tipus

    # Display the total amount for the selected type.
    st.markdown(f"**Total: :blue[{df.loc[mask, "amount"].sum()} €]**")

    # Show an editable table using Streamlit's data editor.
    edited_df = st.data_editor(
        df.loc[mask],
        key=f"{tipus}_editable_df",
        hide_index=True,
        column_config={
            "concept": st.column_config.TextColumn(
                "Concepte", max_chars=50, pinned=True
            ),
            "amount": st.column_config.NumberColumn(
                "Total (€)",
                min_value=1,
                step=1,
                format="%d €",
            ),
            "category": None,  # "category" is not editable in this table.
        },
        use_container_width=True,
    )

    # Check if the DataFrame has been edited.
    if not edited_df.equals(df.loc[mask]):
        logger_all.info("Ha canviat el DF")
        df.loc[mask] = edited_df

        # Save the updated data to a CSV file.
        common.export_csv(df, st.session_state.expenses_filepath)

        # Reload the app to reflect changes.
        st.rerun()


@st.dialog("Crear nou full de despeses")
def new_expenses_sheet():
    st.markdown(
        f"Vols crear un nou full de despesa pel **{st.session_state.current_month.lower()} "
        f"de {st.session_state.current_year}**? Tens les opcions següents:\n"
        f"- Crear-lo com un full nou sense dades\n"
        f"- Duplicar les despeses del full anterior. En aquest cas del "
        f"{st.session_state.prev_month_name} de {st.session_state.prev_year}"
    )

    if st.session_state.prev_date is None:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Buit",
                type="secondary",
                use_container_width=True,
                icon=":material/check_box_outline_blank:",
            ):
                load_data(current_date=st.session_state.current_date, create="empty")
                st.rerun()
        with col2:
            if st.button("Cancel·lar", type="primary", use_container_width=True):
                st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(
                "Buit",
                type="secondary",
                use_container_width=True,
                icon=":material/check_box_outline_blank:",
            ):
                load_data(current_date=st.session_state.current_date, create="empty")
                st.rerun()
        with col2:
            if st.button(
                "Duplicar",
                type="secondary",
                use_container_width=True,
                icon=":material/content_copy:",
            ):
                load_data(
                    current_date=st.session_state.current_date, create="duplicate"
                )
                st.rerun()
        with col3:
            if st.button("Cancel·lar", type="primary", use_container_width=True):
                st.rerun()


def summary():
    expenses_df = st.session_state.expenses_df
    prev_expenses_df = st.session_state.prev_expenses_df
    salary = st.session_state.salary

    st.header(
        f":material/space_dashboard: Resum {st.session_state.current_month} "
        + f"{st.session_state.current_year}",
        divider="rainbow",
    )
    st.write(
        f"Les despeses anteriors són de {st.session_state.prev_month_name} "
        + f"de {st.session_state.prev_year}"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        # Nombre de despeses
        current_despeses = expenses_df.shape[0]
        prev_despeses = prev_expenses_df.shape[0]
        delta = None if prev_expenses_df.empty else current_despeses - prev_despeses
        st.metric("Nombre de despeses", f"{current_despeses}", delta=delta, border=True)

    with col2:
        # Total Despeses
        current_despeses = expenses_df["amount"].sum()
        prev_despeses = prev_expenses_df["amount"].sum()
        delta = (
            None
            if prev_expenses_df.empty
            else f"{round(current_despeses-prev_despeses, 2)} €"
        )
        st.metric(
            "Total Despeses",
            f"{round(current_despeses, 2)} €",
            delta=delta,
            border=True,
            delta_color="inverse",
        )

    with col3:
        # Total Estalvi
        current_estalvi = salary - expenses_df["amount"].sum()
        prev_estalvi = salary - prev_expenses_df["amount"].sum()
        delta = (
            None if prev_expenses_df.empty else round(current_estalvi - prev_estalvi, 2)
        )
        st.metric("Estalvi", f"{round(current_estalvi, 2)} €", delta=delta, border=True)

    # Health Plot
    plot_health(df=expenses_df, salary=salary)


def details():
    st.header(":material/info: Detall de les despeses", divider="rainbow")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏡 Imprescindible")
        st.write(
            "Totes les despeses imprescindibles. Exemples com poden ser l'aportació a casa, etc."
        )
        show_editable_df(st.session_state.expenses_df, tipus="imprescindible")
    with col2:
        st.subheader("🪩 Oci")
        st.write(
            "Totes les despeses d'oci. Exemples com poden ser anar al cinema, sopars, festes, etc."
        )
        show_editable_df(st.session_state.expenses_df, tipus="oci")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 Subscripcions")
        st.write(
            "Totes les subscripcions. Exemples com poden ser Apple Music, Gimnàs, ChatGPT, etc."
        )
        show_editable_df(st.session_state.expenses_df, tipus="subscripcio")
    with col2:
        st.subheader("🗺️ Micro Estalvis")
        st.write(
            "Petits estalvis. Exemples com poden ser estalviar per les vacances, concerts, etc."
        )
        show_editable_df(st.session_state.expenses_df, tipus="microestalvi")


def add_expense():
    with st.form("add_despesa"):
        st.subheader("🆕 Afegir Despesa", divider="green")
        on = st.toggle("Duplicar mes sencer")

        if on:
            # Formulario para ingresar gastos
            with st.form("get"):
                current_date = st.date_input(
                    "Data a duplicar",
                    st.session_state.current_date,
                    format="DD/MM/YYYY",
                )
                st.form_submit_button("Duplicar despeses", icon=":material/add:")
        else:
            nom = st.text_input("Concepte de la despesa")
            col1, col2 = st.columns(2)
            with col1:
                total = st.number_input("Total (€)", min_value=1, step=1)
            with col2:
                tipus_list = set(EXPENSE_TYPES.keys()) - set(["estalvi"])
                tipus_list = list(map(str.capitalize, tipus_list))
                tipus = st.selectbox("category", tipus_list).lower()

            add = st.form_submit_button("Afegir", type="primary", icon=":material/add:")

            if add and nom and total > 0 and tipus:
                st.session_state.db.add_expense(
                    username=st.session_state.username,
                    date=st.session_state.current_date,
                    concept=nom.capitalize(),
                    amount=total,
                    category=tipus,
                    description="None",
                )
                st.success("Despesa afegida!")
                st.rerun()
            elif add and nom == "":
                st.error("Has d'introduir un concepte")


def drop_expense():
    expenses_df = st.session_state.expenses_df
    conceptes = set({}) | set(expenses_df["concept"].unique())
    if conceptes != set({}):
        with st.form("remove_despesa"):
            st.subheader("❌ Eliminar Despesa", divider="red")
            concepte = st.selectbox("Conceptes", conceptes).lower()
            drop = st.form_submit_button(
                "Eliminar", type="primary", icon=":material/delete:"
            )

            if drop and concepte:
                # updated_df = expenses_df.loc[expenses_df["concept"].str.lower() != concepte]
                # removed = len(expenses_df) - len(updated_df)
                # expenses_df = updated_df
                # common.export_csv(
                #    expenses_df, st.session_state.expenses_filepath
                # )  # Guardar datos en CSV
                st.session_state.db.delete_expense(
                    username=st.session_state.username,
                    concept=concepte.lower(),
                )
                st.success(f"S'han eliminat {concepte} despeses!")
                st.rerun()
            elif drop and concepte == "":
                st.error("Has de seleccionar un concepte")
    else:
        st.subheader("❌ Eliminar Despesa", divider="red")
        st.write("Encara no hi ha despeses")


def modify_expenses():
    st.header(":material/edit: Modificar despeses", divider="rainbow")
    col1, col2 = st.columns(2)
    with col1:
        add_expense()
    with col2:
        drop_expense()


def show():
    # Title
    st.title("❤️ Salut Econòmica")

    if st.session_state.username:
        # Select Month
        col1, col2 = st.columns(2)
        with col1:
            current_date = st.date_input(
                "Quin mes vols mirar?",
                st.session_state.current_date,
                format="DD/MM/YYYY",
            )
            st.session_state.current_month = common.get_month_name(
                current_date.month
            ).capitalize()
            st.session_state.current_year = current_date.year
        with col2:
            salary = st.number_input(
                "Salari d'aquest mes?",
                key="salary",
                value=1000,
                placeholder="Insereix el teu salari",
                step=100,
            )

        # Load Data
        load_data(current_date, create=None)

        # Show sections
        summary()
        details()
        modify_expenses()
    else:
        st.write("Inicia sessió per a veure la teva informació.")


show()
