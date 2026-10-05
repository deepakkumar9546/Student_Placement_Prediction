from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import joblib
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "placement-predictor-secret-key"

model = joblib.load("placement_model.pkl")

DATABASE = "placement.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cgpa REAL,
            internships INTEGER,
            projects INTEGER,
            aptitude_score REAL,
            communication_score REAL,
            result TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:

            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            conn.commit()
            conn.close()

            flash("Registration successful. Please login.")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            conn.close()

            flash("Email already registered.")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    successful = conn.execute(
        """SELECT COUNT(*) FROM predictions
           WHERE user_id = ? AND result LIKE 'High%'""",
        (session["user_id"],)
    ).fetchone()[0]

    recent = conn.execute(
        """SELECT * FROM predictions
           WHERE user_id = ?
           ORDER BY id DESC
           LIMIT 5""",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        successful=successful,
        recent=recent
    )


# ---------------- PREDICTION ----------------

@app.route("/predict", methods=["GET", "POST"])
def predict():

    if "user_id" not in session:
        return redirect(url_for("login"))

    prediction = None

    if request.method == "POST":

        cgpa = float(request.form["cgpa"])
        internships = int(request.form["internships"])
        projects = int(request.form["projects"])
        aptitude_score = float(request.form["aptitude_score"])
        communication_score = float(request.form["communication_score"])

        result_value = model.predict([[
            cgpa,
            internships,
            projects,
            aptitude_score,
            communication_score
        ]])

        if result_value[0] == 1:
            prediction = "High Chance of Placement"
        else:
            prediction = "Low Chance of Placement"

        conn = get_db()

        conn.execute(
            """INSERT INTO predictions
            (user_id, cgpa, internships, projects,
             aptitude_score, communication_score, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session["user_id"],
                cgpa,
                internships,
                projects,
                aptitude_score,
                communication_score,
                prediction
            )
        )

        conn.commit()
        conn.close()

    return render_template(
        "predict.html",
        prediction=prediction
    )


# ---------------- HISTORY ----------------

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    predictions = conn.execute(
        """SELECT * FROM predictions
           WHERE user_id = ?
           ORDER BY id DESC""",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "history.html",
        predictions=predictions
    )


# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("profile.html")


# ---------------- ABOUT ----------------

@app.route("/about")
def about():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("about.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)