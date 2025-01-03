from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

import src.utils.common as common
from src.utils.logger import logger_all

DEBT_COLUMNS = [
    ("nom", str),
    ("total", float),
    ("start_date", "datetime64[ns]"),
    ("end_date", "datetime64[ns]"),
    ("pagat", bool),
    ("estat", int),
    ("mesos_pagats", int),
]


def prep_debts_df(debts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares the debts dataframe by converting the columns to their appropriate data types.

    Parameters
    ----------
    debts_df : pd.DataFrame
        A pandas dataframe containing debt information.

    Returns
    -------
    pd.DataFrame
        A dataframe with columns converted to the appropriate data types.
    """

    # Convert columns to specified data types using the DEBT_COLUMNS dictionary
    debts_df = debts_df.astype(dict(DEBT_COLUMNS))

    return debts_df


def load_data(current_date: date, create: None | str = "empty"):
    """
    Loads and initializes the debt data for the current session.

    This function handles loading previous and current month's debt data, preparing
    it for use in the session state. It also supports creating new or duplicate data
    if necessary.

    Parameters
    ----------
    current_date : date
        The current date used to determine the month and year for loading the debt data.

    create : None or str, optional, default="empty"
        A flag indicating whether to create new or duplicate debt data:
        - None: Does not create new data.
        - "empty": Creates an empty debt data file.
        - "duplicate": Creates a new debt data file by duplicating the previous month's data.

    Returns
    -------
    None
        This function updates the session state with the loaded or created debt data.

    Notes
    -----
    The function uses session state to store data file paths, debt data, and other
    related information. If no previous debt data is found, the function shows a toast
    notification.

    Examples
    --------
    >>> load_data(current_date=date(2025, 1, 1), create="empty")
    >>> load_data(current_date=date(2025, 1, 1), create="duplicate")
    """

    # Get Previous debts
    prev_debts_filepath, prev_date = common.get_previous_file(current_date, "debts.csv")

    # Update session state with previous data details
    st.session_state.prev_debts_filepath = prev_debts_filepath
    st.session_state.prev_date = prev_date
    st.session_state.prev_year = str(prev_date.year) if prev_date else None
    st.session_state.prev_month_name = (
        common.get_month_name(prev_date.month) if prev_date else None
    )

    # Load previous debts DataFrame
    if isinstance(prev_debts_filepath, Path) and prev_debts_filepath.exists():
        st.session_state.prev_debts_df = common.load_csv(filepath=prev_debts_filepath)
        st.session_state.prev_debts_df = prep_debts_df(st.session_state.prev_debts_df)
    else:
        st.session_state.prev_debts_df = pd.DataFrame(
            columns=[col for col, _ in DEBT_COLUMNS]
        )
        st.toast("No previous debts found!", icon=":material/warning:")

    # Load current month's debt data
    debts_filepath = common.load_file(current_date, filename="debts.csv")

    # Update session state with current data details
    st.session_state.debts_filepath = debts_filepath
    st.session_state.current_date = current_date
    st.session_state.current_year = str(current_date.year)
    st.session_state.current_month_name = common.get_month_name(current_date.month)

    # Load current debts DataFrame
    if st.session_state.debts_filepath.exists():
        st.session_state.debts_df = common.load_csv(filepath=debts_filepath)
        st.session_state.debts_df = prep_debts_df(st.session_state.debts_df)
    elif create is None:
        st.session_state.debts_df = None
    elif create == "empty":
        st.session_state.debts_df = pd.DataFrame(columns=["nom", "total", "tipus"])
        common.export_csv(st.session_state.debts_df, debts_filepath)
        st.toast("A new empty debts file has been created", icon=":material/info:")
    elif create == "duplicate" and prev_debts_filepath.exists():
        st.session_state.debts_df = common.load_csv(filepath=prev_debts_filepath)
        st.session_state.debts_df = prep_debts_df(st.session_state.debts_df)
        common.export_csv(st.session_state.debts_df, debts_filepath)
        st.toast(
            "A new debts file has been created based on "
            + f"{st.session_state.prev_month_name} of "
            + f"{st.session_state.prev_year}",
            icon=":material/info:",
        )
    else:
        logger_all.error("Failed to load debts for the selected month")


@st.dialog("Crear nou full de despeses")
def new_debts_sheet():
    """
    Displays a dialog for creating a new debt sheet, offering options to either
    create an empty sheet or duplicate the previous month's debts.

    The dialog also includes options to cancel the action. The function updates
    the session state based on the user's selection.

    Parameters
    ----------
    None

    Returns
    -------
    None
        The function updates the session state with the selected action (create empty,
        duplicate, or cancel) and triggers a rerun of the app.

    Notes
    -----
    The function assumes that `st.session_state.current_month`, `st.session_state.current_year`,
    `st.session_state.prev_month_name`, and `st.session_state.prev_year` are set before calling.

    Examples
    --------
    >>> new_debts_sheet()  # Opens the dialog for creating a new debt sheet.
    """

    # Display the dialog with options for creating a new debt sheet
    st.markdown(
        f"Do you want to create a new debt sheet for **{st.session_state.current_month.lower()} "
        f"of {st.session_state.current_year}**? You have the following options:\n"
        f"- Create it as a new empty sheet.\n"
        f"- Duplicate the debts from the previous sheet. In this case, from "
        f"{st.session_state.prev_month_name} of {st.session_state.prev_year}."
    )

    # If there is no previous debts file, only the empty option is available
    if st.session_state.prev_debts_filepath is None:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Empty",
                type="secondary",
                use_container_width=True,
                icon=":material/check_box_outline_blank:",
            ):
                load_data(current_date=st.session_state.current_date, create="empty")
                st.rerun()
        with col2:
            if st.button("Cancel", type="primary", use_container_width=True):
                st.rerun()
    else:
        # If there is a previous debts file, offer options for both empty and duplicate
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(
                "Empty",
                type="secondary",
                use_container_width=True,
                icon=":material/check_box_outline_blank:",
            ):
                load_data(current_date=st.session_state.current_date, create="empty")
                st.rerun()
        with col2:
            if st.button(
                "Duplicate",
                type="secondary",
                use_container_width=True,
                icon=":material/content_copy:",
            ):
                load_data(
                    current_date=st.session_state.current_date, create="duplicate"
                )
                st.rerun()
        with col3:
            if st.button("Cancel", type="primary", use_container_width=True):
                st.rerun()


def show_current_debts_section():
    """
    Displays the current month's debt list in an editable table.

    Allows users to update payment statuses and track progress
    over the months. The table is interactive, and changes are
    reflected in the session state.
    """

    # Header section for the current month's debt list
    st.header(
        f":material/schedule: Debt List for {st.session_state.current_month} "
        + f"{st.session_state.current_year}",
        divider="rainbow",
    )
    st.write(
        f"The previous payments are from {st.session_state.prev_month_name} "
        + f"of {st.session_state.prev_year}"
    )

    debts_df = st.session_state.debts_df.copy()

    # Show editable data table
    edited_df = st.data_editor(
        st.session_state.debts_df,
        key="updated_debts_editable_rows",
        hide_index=True,
        column_config={
            "nom": st.column_config.TextColumn("Name", max_chars=50, pinned=True),
            "total": st.column_config.NumberColumn(
                "Total",
                min_value=1,
                step=1,
                format="%d €",
            ),
            "start_date": st.column_config.DateColumn(
                "Start Date",
                format="MMMM YYYY",
                step=1,
            ),
            "end_date": st.column_config.DateColumn(
                "End Date",
                format="MMMM YYYY",
                step=1,
            ),
            "pagat": st.column_config.CheckboxColumn(
                "Paid",
                default=False,
            ),
            "estat": st.column_config.ProgressColumn(
                "Status",
                help="Paid",
                format="%d",
                min_value=0,
                max_value=100,
            ),
            "mesos_pagats": st.column_config.NumberColumn(
                "Paid Months",
                min_value=1,
                step=1,
                format="%d",
                disabled=True,
            ),
        },
        use_container_width=True,
    )

    # Detect changes in the 'paid' column
    cambio_a_true = (~debts_df["pagat"]) & (edited_df["pagat"])
    cambio_a_false = (debts_df["pagat"]) & (~edited_df["pagat"])

    # If there are any changes in the 'paid' column, update the 'paid months' and 'status'
    if any(cambio_a_true) or any(cambio_a_false):
        # Update 'paid months' based on changes in the 'paid' column
        edited_df.loc[cambio_a_true, "mesos_pagats"] += 1
        edited_df.loc[cambio_a_false, "mesos_pagats"] -= 1

        # Calculate total months between start and end dates
        total_meses = (
            edited_df["end_date"].dt.year - edited_df["start_date"].dt.year
        ) * 12 + (edited_df["end_date"].dt.month - edited_df["start_date"].dt.month)

        # Update 'status' based on the proportion of paid months
        edited_df["estat"] = ((edited_df["mesos_pagats"] / total_meses) * 100).astype(
            int
        )

        # Save the updated dataframe to the session state and export to CSV
        st.session_state.debts_df = edited_df.copy()
        common.export_csv(st.session_state.debts_df, st.session_state.debts_filepath)
        st.rerun()


def new_debt_section():
    """
    Displays a form for adding a new debt entry.

    Users can input the debt's concept, total amount, start date,
    and end date. The new debt is added to the existing DataFrame
    and saved to a CSV file.
    """

    # Header for the new debt section
    st.header(":material/add: New Debt", divider="rainbow")
    st.write("In this section, you can add new debts.")

    # Form for adding a new debt
    with st.form(key="new_debt_form"):
        description = st.text_input("Concept")
        col1, col2, col3 = st.columns(3)
        with col1:
            total = st.number_input("Total (€)", min_value=1, step=1)
        with col2:
            start_date = st.date_input(
                "Start Date",
                value="today",
            )
        with col3:
            end_date = st.date_input(
                "End Date",
                value=datetime.now() + relativedelta(years=1),
            )

        # Submit button
        add = st.form_submit_button("Add", type="primary", icon=":material/add:")

        # If form is submitted with valid data
        if add and description and start_date < end_date:
            new_cost = {
                "nom": description,
                "total": total,
                "start_date": start_date,
                "end_date": end_date,
                "pagat": False,
                "estat": 0.0,
                "mesos_pagats": 0,
            }

            # Add the new debt to the existing DataFrame
            updated_df = pd.concat(
                [st.session_state.debts_df, pd.DataFrame([new_cost])], ignore_index=True
            )
            st.session_state.debts_df = updated_df

            # Save the updated DataFrame to CSV
            common.export_csv(
                st.session_state.debts_df, st.session_state.debts_filepath
            )  # Save data to CSV
            st.rerun()


def show():
    """
    Display Pending Payments Section

    This function displays the main page for managing pending payments. It allows the
    user to select a month, load the corresponding data, and either view existing debts
    or create a new debt sheet if no data is available.
    """
    # Title
    st.title("⏳ Pending Payments")

    # Select Month
    current_date = st.date_input(
        "Which month would you like to view?",
        st.session_state.current_date,
        format="DD/MM/YYYY",
    )
    st.session_state.current_month = common.get_month_name(
        current_date.month
    ).capitalize()
    st.session_state.current_year = current_date.year

    # Load Data
    load_data(current_date, create=None)

    if st.session_state.debts_df is None:
        st.error("No debt sheet available for this month")
        if st.button(
            "Create New Debt Sheet",
            icon=":material/add:",
            use_container_width=True,
            type="primary",
        ):
            new_debts_sheet()
    else:
        show_current_debts_section()
        new_debt_section()


show()
