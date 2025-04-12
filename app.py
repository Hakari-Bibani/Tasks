# app.py
import streamlit as st
import handle
import streamlit_authenticator as stauth

# --- Authentication Setup ---
# In a production app you may want to store these credentials securely.
# In this demo we use an in-code dictionary.
# For example, you might store the following in Streamlit secrets as well.

names = ["John Doe"]
usernames = ["johndoe"]
# For demonstration purposes, we use a simple password.
passwords = ["123"]  # In production, use strong passwords and store them hashed.
hashed_passwords = stauth.Hasher(passwords).generate()

credentials = {
    "usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]}
    }
}

authenticator = stauth.Authenticate(credentials, 
                                    "my_cookie_name", 
                                    "my_signature_key", 
                                    cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.sidebar.write(f"Welcome {name}!")
    authenticator.logout("Logout", "sidebar")
    
    st.title("Kanban Board")
    
    # --- Load tasks from database ---
    tasks = handle.get_tasks()
    
    # Define board categories.
    categories = ["Task", "In Progress", "Done", "BrainStorm"]
    tasks_by_category = {cat: [] for cat in categories}
    for task in tasks:
        tasks_by_category[task["category"]].append(task)
    
    # Create 4 equal columns for the board
    cols = st.columns(4)
    
    # Iterate over each category to display tasks and input forms.
    for idx, cat in enumerate(categories):
        with cols[idx]:
            st.header(cat)
            
            # List tasks in this category.
            for t in tasks_by_category[cat]:
                st.write(t["text"])
                # Delete button – clicking it will remove the task.
                if st.button(f"Delete", key=f"del_{t['id']}"):
                    handle.delete_task(t['id'])
                    st.experimental_rerun()
                
                # Option to move task to another column (simulate drag and drop).
                new_cat = st.selectbox("Move to", [c for c in categories if c != cat], key=f"move_{t['id']}")
                if st.button("Update", key=f"update_{t['id']}"):
                    handle.update_task_category(t['id'], new_cat)
                    st.experimental_rerun()

            # Input to add a new task.
            new_task = st.text_input(f"Add new {cat} task", key=f"new_{cat}")
            if st.button(f"Add", key=f"add_{cat}") and new_task:
                handle.add_task(cat, new_task)
                st.experimental_rerun()
                
else:
    if authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")
