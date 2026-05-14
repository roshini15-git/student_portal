from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def create_table():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

create_table()

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        roll = request.form["roll"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students (roll_number, email, password) VALUES (?, ?, ?)",
                (roll, email, password)
            )
            conn.commit()
        except:
            return "Roll number already exists!"

        conn.close()
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    roll = request.form["roll"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()

    # Step 1: Check if user exists
    cursor.execute(
        "SELECT * FROM students WHERE roll_number=?",
        (roll,)
    )
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return render_template("login.html", error="Invalid Roll Number")

    # Step 2: Check password
    if user[3] != password:
        return render_template("login.html", error="Invalid Password")

    # Step 3: Success
    session["user"] = roll
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", roll=session["user"])
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)