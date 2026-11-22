import sqlite3

DATABASE = "users.db"

connection = sqlite3.connect(DATABASE)

users = connection.execute(
    """
    SELECT
        username,
        password_hash,
        failed_attempts,
        is_locked
    FROM users
    """
).fetchall()

connection.close()

print("\n=== SECUREAUTH DATABASE VERIFICATION ===\n")

if not users:
    print("No users found.")

for user in users:

    username = user[0]
    password_hash = user[1]
    failed_attempts = user[2]
    is_locked = user[3]

    print(f"Username        : {username}")
    print(f"Stored Password : {password_hash}")
    print(f"Failed Attempts : {failed_attempts}")
    print(
        f"Account Status  : "
        f"{'LOCKED' if is_locked else 'ACTIVE'}"
    )

    print("-" * 60)

print("\nVerification:")
print("Passwords shown above are hashes, not plaintext passwords.")