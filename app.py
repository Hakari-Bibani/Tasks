import streamlit as st
import uuid
from handler import DatabaseHandler

# Initialize database handler with direct connection string
db = DatabaseHandler(connection_string="postgresql://neondb_owner:npg_vJSrcVfZ7N6a@ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")

def init_session_state():
    if 'current_board' not in st.session_state:
        st.session_state.current_board = None

def main():
    st.title("Task Management Board")
    init_session_state()
    
    # Display current user
    st.sidebar.write(f"User: Hakari-Bibani")
    
    # Board selection
    tables = ["table1", "table2", "table3", "table4", "table5", "table6"]
    selected_board = st.selectbox("Select Board", tables)
    st.session_state.current_board = selected_board

    if st.session_state.current_board:
        # Create columns for the board
        cols = st.columns(4)
        columns = ['task', 'in progress', 'done', 'brainstorm']  # Changed to lowercase
        display_names = ['Task', 'In Progress', 'Done', 'BrainStorm']  # For display purposes
        
        # Display each column
        for i, (column, display_name) in enumerate(zip(columns, display_names)):
            with cols[i]:
                st.subheader(display_name)
                
                # Add new card
                with st.container():
                    new_task = st.text_area(f"New {display_name}", key=f"new_{column}_{uuid.uuid4()}")
                    if st.button("Add", key=f"add_{column}_{uuid.uuid4()}"):
                        if new_task.strip():
                            data = {
                                'id': str(uuid.uuid4()),
                                'task': new_task if column == 'task' else None,
                                'in progress': new_task if column == 'in progress' else None,
                                'done': new_task if column == 'done' else None,
                                'brainstorm': new_task if column == 'brainstorm' else None
                            }
                            db.insert_card(st.session_state.current_board, data)
                            st.experimental_rerun()
                
                # Display existing cards
                cards = db.get_cards_for_column(st.session_state.current_board, column)
                for card in cards:
                    with st.container():
                        col1, col2 = st.columns([5,1])
                        with col1:
                            updated_content = st.text_area(
                                "",
                                value=card[column],
                                key=f"card_{card['id']}_{column}",
                                on_change=lambda: db.update_card(
                                    st.session_state.current_board,
                                    card['id'],
                                    column,
                                    st.session_state[f"card_{card['id']}_{column}"]
                                )
                            )
                        with col2:
                            if st.button("🗑️", key=f"delete_{card['id']}"):
                                if st.button("Confirm", key=f"confirm_{card['id']}"):
                                    db.delete_card(st.session_state.current_board, card['id'])
                                    st.experimental_rerun()

    # Add CSS for better styling
    st.markdown("""
        <style>
        .stTextArea textarea {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .stButton button {
            width: 100%;
            margin: 2px 0;
        }
        .container {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
