import pandas as pd

def create_board(db, table_name, task):
    query = f"INSERT INTO {table_name} (task, in_progress, done, brainstorm) VALUES (%s, %s, %s, %s)"
    db.query(query, params=(task, None, None, None))

def get_tasks(db, table_name):
    query = f"SELECT * FROM {table_name}"
    df = db.query(query)
    tasks = df.to_dict(orient="records")
    result = {"Tasks": [], "In Progress": [], "Done": [], "BrainStorm": []}
    for task in tasks:
        if task["in_progress"]:
            result["In Progress"].append(task)
        elif task["done"]:
            result["Done"].append(task)
        elif task["brainstorm"]:
            result["BrainStorm"].append(task)
        else:
            result["Tasks"].append(task)
    return result

def update_task(db, table_name, task_id, new_column):
    query = f"UPDATE {table_name} SET {new_column} = %s WHERE id = %s"
    db.query(query, params=(True, task_id))

def delete_task(db, table_name, task_id):
    query = f"DELETE FROM {table_name} WHERE id = %s"
    db.query(query, params=(task_id,))
