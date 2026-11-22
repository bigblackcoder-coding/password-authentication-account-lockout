from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Required for Flask sessions
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-key-change-in-production"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

DATABASE = "users.db"
MAX_FAILED_ATTEMPTS = 3


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ---------------------------------------------------------
# CREATE DATABASE
# ---------------------------------------------------------

def initialize_database():

    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            is_locked INTEGER DEFAULT 0
        )
        """
    )

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():

    if "username" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        # Password is converted into a salted hash.
        # The plaintext password is NEVER stored.
        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users
                (username, password_hash, failed_attempts, is_locked)
                VALUES (?, ?, 0, 0)
                """,
                (username, password_hash)
            )

            connection.commit()

            flash(
                "Account created successfully. You can now log in.",
                "success"
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("Username already exists.", "error")

        finally:

            connection.close()

    return render_template("register.html")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        # Username does not exist
        if user is None:

            connection.close()

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(url_for("login"))

        # -------------------------------------------------
        # CHECK WHETHER ACCOUNT IS ALREADY LOCKED
        # -------------------------------------------------

        if user["is_locked"] == 1:

            connection.close()

            flash(
                "Account is locked because of too many failed login attempts.",
                "error"
            )

            return redirect(url_for("login"))

        # -------------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------------

        if check_password_hash(
            user["password_hash"],
            password
        ):

            # Correct password:
            # reset failed attempts

            connection.execute(
                """
                UPDATE users
                SET failed_attempts = 0
                WHERE id = ?
                """,
                (user["id"],)
            )

            connection.commit()
            connection.close()

            session["username"] = user["username"]

            flash(
                "Authentication successful.",
                "success"
            )

            return redirect(url_for("dashboard"))

        # -------------------------------------------------
        # INCORRECT PASSWORD
        # -------------------------------------------------

        failed_attempts = user["failed_attempts"] + 1

        # -------------------------------------------------
        # LOCK ACCOUNT AFTER THREE WRONG ATTEMPTS
        # -------------------------------------------------

        if failed_attempts >= MAX_FAILED_ATTEMPTS:

            connection.execute(
                """
                UPDATE users
                SET failed_attempts = ?,
                    is_locked = 1
                WHERE id = ?
                """,
                (
                    failed_attempts,
                    user["id"]
                )
            )

            connection.commit()
            connection.close()

            flash(
                "Account locked after 3 incorrect login attempts.",
                "error"
            )

            return redirect(url_for("login"))

        # -------------------------------------------------
        # ACCOUNT NOT LOCKED YET
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE users
            SET failed_attempts = ?
            WHERE id = ?
            """,
            (
                failed_attempts,
                user["id"]
            )
        )

        connection.commit()
        connection.close()

        attempts_remaining = (
            MAX_FAILED_ATTEMPTS - failed_attempts
        )

        flash(
            f"Incorrect password. "
            f"{attempts_remaining} attempt(s) remaining.",
            "error"
        )

        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        flash(
            "Please log in to access the dashboard.",
            "error"
        )

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("login"))


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------
# ---------------------------------------------------------
# ADMIN SECURITY PANEL
# ---------------------------------------------------------

@app.route("/admin")
def admin():

    connection = get_db_connection()

    users = connection.execute(
        """
        SELECT id, username, failed_attempts, is_locked
        FROM users
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        users=users
    )


# ---------------------------------------------------------
# UNLOCK ACCOUNT
# ---------------------------------------------------------

@app.route("/admin/unlock/<int:user_id>", methods=["POST"])
def unlock_account(user_id):

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT username
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        flash("User not found.", "error")
        return redirect(url_for("admin"))

    connection.execute(
        """
        UPDATE users
        SET failed_attempts = 0,
            is_locked = 0
        WHERE id = ?
        """,
        (user_id,)
    )

    connection.commit()
    connection.close()

    flash(
        f"Account '{user['username']}' has been unlocked.",
        "success"
    )

    return redirect(url_for("admin"))

if __name__ == "__main__":

    initialize_database()

    app.run(debug=True)