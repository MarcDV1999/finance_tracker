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
    - "nom" : str
    - "total" : float
    - "tipus" : str
    """
    # Ensure the DataFrame columns have the expected data types.
    expenses_df = expenses_df.astype({"nom": str, "total": float, "tipus": str})

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
            columns=["nom", "total", "tipus"]
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
        st.session_state.expenses_df = pd.DataFrame(columns=["nom", "total", "tipus"])
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
        DataFrame containing expense data with columns 'tipus' (type) and 'total' (amount).
    salary : int
        The total monthly salary, used to calculate savings.

    Notes
    -----
    The function calculates savings as the difference between the salary and total expenses,
    groups the data by expense type, and plots a horizontal stacked bar chart with customized
    colors for each type.
    """
    # Calculate savings and add it as a new row.
    estalvi_row = dict(tipus="estalvi", total=salary - df["total"].sum())
    df = pd.concat([df, pd.DataFrame([estalvi_row])], ignore_index=True)

    # Round the 'total' column to avoid decimals.
    df["total"] = df["total"].round(0)

    # Group data by 'tipus' and sum totals.
    df_grouped = df.groupby("tipus", as_index=False)["total"].sum()

    # Ensure the categories are displayed in a specific order.
    order = list(EXPENSE_TYPES.keys()) + ["estalvi"]
    df_grouped["tipus"] = pd.Categorical(
        df_grouped["tipus"], categories=order, ordered=True
    )
    df_grouped = df_grouped.sort_values("tipus")

    # Create a color map based on expense types.
    color_map = {
        type_name: data.get("color", None) for type_name, data in EXPENSE_TYPES.items()
    }

    # Generate the bar chart using Plotly.
    fig = px.bar(
        df_grouped,
        x="total",
        y=["Despeses"] * len(df_grouped),  # Placeholder for consistent formatting.
        orientation="h",
        title="Despeses",
        labels={"total": "Total (€)", "tipus": "Tipus de despesa", "x": "", "y": ""},
        color="tipus",
        height=300,
        barmode="stack",
        text="total",
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
        DataFrame containing expense data with columns 'nom', 'total', and 'tipus'.
    tipus : str
        The expense type to filter and display.

    Notes
    -----
    The function filters the DataFrame for the specified type, shows an editable table,
    and updates the data if changes are made. Changes are saved to a CSV file, and the app
    reloads the updated data.
    """
    # Capitalize the 'nom' column for consistency.
    df["nom"] = df["nom"].str.capitalize()

    # Filter the DataFrame to only include rows of the specified type.
    mask = df["tipus"] == tipus

    # Display the total amount for the selected type.
    st.markdown(f"**Total: :blue[{df.loc[mask, 'total'].sum()} €]**")

    # Show an editable table using Streamlit's data editor.
    edited_df = st.data_editor(
        df.loc[mask],
        key=f"{tipus}_editable_df",
        hide_index=True,
        column_config={
            "nom": st.column_config.TextColumn("Concepte", max_chars=50, pinned=True),
            "total": st.column_config.NumberColumn(
                "Total (€)",
                min_value=1,
                step=1,
                format="%d €",
            ),
            "tipus": None,  # 'tipus' is not editable in this table.
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

    if st.session_state.prev_expenses_filepath is None:
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
        current_despeses = expenses_df["total"].sum()
        prev_despeses = prev_expenses_df["total"].sum()
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
        current_estalvi = salary - expenses_df["total"].sum()
        prev_estalvi = salary - prev_expenses_df["total"].sum()
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
        nom = st.text_input("Concepte de la despesa")
        col1, col2 = st.columns(2)
        with col1:
            total = st.number_input("Total (€)", min_value=1, step=1)
        with col2:
            tipus_list = set(EXPENSE_TYPES.keys()) - set(["estalvi"])
            tipus_list = list(map(str.capitalize, tipus_list))
            tipus = st.selectbox("Tipus", tipus_list).lower()

        add = st.form_submit_button("Afegir", type="primary", icon=":material/add:")

        if add and nom and total > 0 and tipus:
            new_cost = {"nom": nom.capitalize(), "total": total, "tipus": tipus}
            st.session_state.expenses_df = pd.concat(
                [st.session_state.expenses_df, pd.DataFrame([new_cost])],
                ignore_index=True,
            )
            common.export_csv(
                st.session_state.expenses_df, st.session_state.expenses_filepath
            )  # Guardar datos en CSV
            st.success("¡Gasto agregado!")
        elif add and nom == "":
            st.error("Has d'introduir un concepte")


def drop_expense():
    expenses_df = st.session_state.expenses_df
    with st.form("remove_despesa"):
        st.subheader("❌ Eliminar Despesa", divider="red")
        conceptes = set(expenses_df["nom"].unique())
        concepte = st.selectbox("Conceptes", conceptes).lower()
        drop = st.form_submit_button(
            "Eliminar", type="primary", icon=":material/delete:"
        )

        if drop and concepte:
            updated_df = expenses_df.loc[expenses_df["nom"].str.lower() != concepte]
            removed = len(expenses_df) - len(updated_df)
            expenses_df = updated_df
            common.export_csv(
                expenses_df, st.session_state.expenses_filepath
            )  # Guardar datos en CSV
            st.success(f"S'han eliminat {removed} despeses!")
        elif drop and concepte == "":
            st.error("Has de seleccionar un concepte")


def modify_expenses():
    st.header(":material/edit: Modificar despeses", divider="rainbow")
    # Formulario para ingresar gastos
    col1, col2 = st.columns(2)
    with col1:
        add_expense()
    with col2:
        drop_expense()


def show():
    # Title
    st.title("❤️ Salut Econòmica")

    # Select Month
    col1, col2 = st.columns(2)
    with col1:
        current_date = st.date_input(
            "Quin mes vols mirar?", st.session_state.current_date, format="DD/MM/YYYY"
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

    if st.session_state.expenses_df is None:
        st.error("No hi ha full de despeses per aquest mes")
        if st.button(
            "Crear nou full de despeses",
            icon=":material/add:",
            use_container_width=True,
            type="primary",
        ):
            new_expenses_sheet()
    else:
        summary()
        details()
        modify_expenses()


show()
