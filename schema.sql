CREATE TABLE IF NOT EXISTS logins(
    user_id integer PRIMARY KEY AUTOINCREMENT,
    login text NOT NULL,
    password text NOT NULL,
    watched text,
    planned text
)
