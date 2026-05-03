"""
app.py
------
Main Flask application for the Crop Yield Prediction System.
Handles all routes: login, dashboard, prediction, analytics, logout.

Usage:
    python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle
import numpy as np
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "crop_yield_secret_key_2024"  # Required for session handling

# ─────────────────────────────────────────────
# Load ML Model
# ─────────────────────────────────────────────
with open("model/model.pkl", "rb") as f:
    model_data = pickle.load(f)

model         = model_data["model"]
label_encoder = model_data["label_encoder"]
CROPS         = model_data["crops"]

# ─────────────────────────────────────────────
# Database Setup (SQLite)
# ─────────────────────────────────────────────
DB_PATH = "database.db"

def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL,
            crop        TEXT NOT NULL,
            rainfall    REAL NOT NULL,
            temperature REAL NOT NULL,
            area        REAL NOT NULL,
            yield       REAL NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)

    # Insert a default admin user if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password)
        VALUES (?, ?)
    """, ("admin", "admin123"))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# Helper: get DB connection
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # allows dict-like row access
    return conn

# ─────────────────────────────────────────────
# Route: Home → redirect to login
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return redirect(url_for("login"))

# ─────────────────────────────────────────────
# Route: Login
# ─────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password. Try admin / admin123"

    return render_template("login.html", error=error)

# ─────────────────────────────────────────────
# Route: Logout
# ─────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─────────────────────────────────────────────
# Route: Dashboard
# ─────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    predictions = conn.execute(
        "SELECT * FROM predictions WHERE username=? ORDER BY id DESC",
        (session["username"],)
    ).fetchall()
    conn.close()

    return render_template("dashboard.html",
                           username=session["username"],
                           predictions=predictions)

# ─────────────────────────────────────────────
# Route: Predict
# ─────────────────────────────────────────────
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "username" not in session:
        return redirect(url_for("login"))

    result = None
    error  = None

    if request.method == "POST":
        try:
            crop        = request.form.get("crop")
            rainfall    = float(request.form.get("rainfall"))
            temperature = float(request.form.get("temperature"))
            area        = float(request.form.get("area"))

            # Encode crop name to number
            crop_encoded = label_encoder.transform([crop])[0]

            # Make prediction
            features     = np.array([[crop_encoded, rainfall, temperature, area]])
            predicted    = model.predict(features)[0]
            result       = round(predicted, 2)

            # Save to database
            conn = get_db()
            conn.execute("""
                INSERT INTO predictions (username, crop, rainfall, temperature, area, yield, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session["username"], crop, rainfall,
                temperature, area, result,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()

        except Exception as e:
            error = f"Prediction failed: {str(e)}"

    return render_template("predict.html",
                           username=session["username"],
                           crops=CROPS,
                           result=result,
                           error=error)

# ─────────────────────────────────────────────
# Route: Analytics
# ─────────────────────────────────────────────
@app.route("/analytics")
def analytics():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    predictions = conn.execute(
        "SELECT * FROM predictions WHERE username=?",
        (session["username"],)
    ).fetchall()
    conn.close()

    # Prepare data for charts
    crop_counts  = {}   # for pie chart
    crop_yields  = {}   # for bar chart (avg yield per crop)
    trend_data   = []   # for line chart (yield over time)

    for p in predictions:
        crop  = p["crop"]
        yield_ = p["yield"]
        date  = p["created_at"][:10]   # YYYY-MM-DD

        # Pie chart data
        crop_counts[crop] = crop_counts.get(crop, 0) + 1

        # Bar chart data (collect yields per crop)
        if crop not in crop_yields:
            crop_yields[crop] = []
        crop_yields[crop].append(yield_)

        # Line chart data
        trend_data.append({"date": date, "yield": yield_})

    # Average yield per crop
    avg_yields = {
        crop: round(sum(vals) / len(vals), 2)
        for crop, vals in crop_yields.items()
    }

    return render_template("analytics.html",
                           username=session["username"],
                           crop_counts=crop_counts,
                           avg_yields=avg_yields,
                           trend_data=trend_data)

# ─────────────────────────────────────────────
# API: Get all predictions as JSON (for charts)
# ─────────────────────────────────────────────
@app.route("/api/predictions")
def api_predictions():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM predictions WHERE username=? ORDER BY id DESC",
        (session["username"],)
    ).fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    return jsonify(data)

# ─────────────────────────────────────────────
# Run the app
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()    # Create DB and tables on startup
    app.run(debug=True)