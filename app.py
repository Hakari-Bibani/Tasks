"""
app.py

Main entry point for the Streamlit web app.
Displays a board with 4 columns: 'Task', 'In Progress', 'Done', 'BrainStorm'.
Allows adding new items to each column, and moving items between columns.
"""

import streamlit as st
from sidebar import show_sidebar
from handle import get_tasks, add_task, update_task_column

def main():
    st.title("Trello-like Board with Neon Postgres")

    # 1. Sidebar: user selects an existing table or creates a new one
    current_table = show_sidebar()

    st.subheader(f"Currently Viewing: {current_table}")

    # 2. Fetch all rows from the chosen table
    all_tasks = get_tasks(current_table)

    # We'll store tasks in a dict keyed by column name
    tasks_by_col = {
        "Task": [],
        "In Progress": [],
        "Done": [],
        "BrainStorm": []
    }

    # 3. Sort tasks into the correct column
    for item in all_tasks:
        # Only one column will have text for each row
        if item["Task"]:
            tasks_by_col["Task"].append(item)
        elif item["In Progress"]:
            tasks_by_col["In Progress"].append(item)
        elif item["Done"]:
            tasks_by_col["Done"].append(item)
        elif item["BrainStorm"]:
            tasks_by_col["BrainStorm"].append(item)

    # 4. Create four columns in Streamlit layout
    col_task, col_inprog, col_done, col_brain = st.columns(4)

    # --- Task Column ---
    with col_task:
        st.subheader("Task")
        for t in tasks_by_col["Task"]:
            st.write(f"- {t['Task']}")
            if st.button(f"Move to In Progress [{t['id']}]", key=f"task_to_inprog_{t['id']}"):
                update_task_column(current_table, t["id"], "Task", "In Progress")
                st.experimental_rerun()
            if st.button(f"Move to BrainStorm [{t['id']}]", key=f"task_to_brain_{t['id']}"):
                update_task_column(current_table, t["id"], "Task", "BrainStorm")
                st.experimental_rerun()

        new_task_text = st.text_input("Add a new Task", key="new_task_text")
        if st.button("Add Task", key="add_task_button"):
            if new_task_text.strip():
                add_task(current_table, "Task", new_task_text.strip())
                st.experimental_rerun()

    # --- In Progress Column ---
    with col_inprog:
        st.subheader("In Progress")
        for t in tasks_by_col["In Progress"]:
            st.write(f"- {t['In Progress']}")
            if st.button(f"Move to Done [{t['id']}]", key=f"inprog_to_done_{t['id']}"):
                update_task_column(current_table, t["id"], "In Progress", "Done")
                st.experimental_rerun()
            if st.button(f"Move to BrainStorm [{t['id']}]", key=f"inprog_to_brain_{t['id']}"):
                update_task_column(current_table, t["id"], "In Progress", "BrainStorm")
                st.experimental_rerun()

        new_inprog_text = st.text_input("Add a new In Progress", key="new_inprog_text")
        if st.button("Add In Progress", key="add_inprog_button"):
            if new_inprog_text.strip():
                add_task(current_table, "In Progress", new_inprog_text.strip())
                st.experimental_rerun()

    # --- Done Column ---
    with col_done:
        st.subheader("Done")
        for t in tasks_by_col["Done"]:
            st.write(f"- {t['Done']}")
            if st.button(f"Move to BrainStorm [{t['id']}]", key=f"done_to_brain_{t['id']}"):
                update_task_column(current_table, t["id"], "Done", "BrainStorm")
                st.experimental_rerun()

        new_done_text = st.text_input("Add a new Done", key="new_done_text")
        if st.button("Add Done", key="add_done_button"):
            if new_done_text.strip():
                add_task(current_table, "Done", new_done_text.strip())
                st.experimental_rerun()

    # --- BrainStorm Column ---
    with col_brain:
        st.subheader("BrainStorm")
        for t in tasks_by_col["BrainStorm"]:
            st.write(f"- {t['BrainStorm']}")
            if st.button(f"Move to Task [{t['id']}]", key=f"brain_to_task_{t['id']}"):
                update_task_column(current_table, t["id"], "BrainStorm", "Task")
                st.experimental_rerun()
            if st.button(f"Move to In Progress [{t['id']}]", key=f"brain_to_inprog_{t['id']}"):
                update_task_column(current_table, t["id"], "BrainStorm", "In Progress")
                st.experimental_rerun()

        new_brain_text = st.text_input("Add new BrainStorm", key="new_brain_text")
        if st.button("Add BrainStorm", key="add_brain_button"):
            if new_brain_text.strip():
                add_task(current_table, "BrainStorm", new_brain_text.strip())
                st.experimental_rerun()

if __name__ == "__main__":
    main()
