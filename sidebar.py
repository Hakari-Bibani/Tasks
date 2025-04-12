[postgres]
host = "ep-snowy-bar-a5zv1qhw-pooler.us-east-2.aws.neon.tech"
database = "neondb"
user = "neondb_owner"
password = "npg_vJSrcVfZ7N6a"

[auth]
usernames = """
johndoe:
  email: johndoe@example.com
  name: John Doe
  password: $2b$12$HbXGBK7q6RR2YBXfMAUVBuLxWdQzE1qLyJ.zVj7Lt5R73lLLbj4FO
janedoe:
  email: janedoe@example.com
  name: Jane Doe
  password: $2b$12$HbXGBK7q6RR2YBXfMAUVBuLxWdQzE1qLyJ.zVj7Lt5R73lLLbj4FO
"""

[cookie]
name = "kanban_cookie"
key = "random_signature_key_change_this"
expiry_days = 30
