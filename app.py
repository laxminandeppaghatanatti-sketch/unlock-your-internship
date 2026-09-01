import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from database import get_connection, init_db
from impact_engine import get_skill_impact, get_top_recommendation

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard.html")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/path-know.html")
def path_know_page():
    return render_template("path-know.html")

@app.route("/path-find.html")
def path_find_page():
    return render_template("path-find.html")

@app.route("/path-lost.html")
def path_lost_page():
    return render_template("path-lost.html")

@app.route("/my-skills.html")
def my_skills_page():
    return render_template("my-skills.html")

@app.route("/unlock-map.html")
def unlock_map_page():
    return render_template("unlock-map.html")

@app.route("/applications.html")
def applications_page():
    return render_template("applications.html")


@app.route("/targets", methods=["POST"])
def add_target():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    role_title = data.get("role_title")
    company = data.get("company", "")
    source_url = data.get("source_url", "")
    priority = data.get("priority", "Target")
    skills = data.get("skills", [])

    if not role_title:
        return jsonify({"error": "role_title is required"}), 400

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO targets (role_title, company, source_url, priority) VALUES (?, ?, ?, ?)",
        (role_title, company, source_url, priority)
    )
    target_id = cursor.lastrowid

    for skill in skills:
        conn.execute(
            "INSERT INTO target_skills (target_id, skill_name) VALUES (?, ?)",
            (target_id, skill)
        )

    conn.commit()
    conn.close()

    return jsonify({"message": "Target internship saved", "id": target_id}), 201


@app.route("/targets", methods=["GET"])
def get_targets():
    conn = get_connection()
    targets = conn.execute("SELECT * FROM targets").fetchall()

    result = []
    for t in targets:
        skills = conn.execute(
            "SELECT skill_name FROM target_skills WHERE target_id = ?", (t["id"],)
        ).fetchall()
        result.append({
            "id": t["id"],
            "role_title": t["role_title"],
            "company": t["company"],
            "source_url": t["source_url"],
            "priority": t["priority"],
            "skills": [s["skill_name"] for s in skills]
        })

    conn.close()
    return jsonify(result)


@app.route("/targets/<int:target_id>", methods=["DELETE"])
def delete_target(target_id):
    conn = get_connection()
    conn.execute("DELETE FROM target_skills WHERE target_id = ?", (target_id,))
    conn.execute("DELETE FROM targets WHERE id = ?", (target_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Target deleted"})


@app.route("/my-skills", methods=["POST"])
def add_my_skill():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    skill_name = data.get("skill_name")
    level = data.get("level")

    if not skill_name or not isinstance(skill_name, str):
        return jsonify({"error": "skill_name is required"}), 400
    if level is None or not isinstance(level, int) or not (0 <= level <= 100):
        return jsonify({"error": "level must be a number between 0 and 100"}), 400

    conn = get_connection()
    existing = conn.execute("SELECT id FROM my_skills WHERE skill_name = ?", (skill_name,)).fetchone()

    if existing:
        conn.execute("UPDATE my_skills SET level = ? WHERE skill_name = ?", (level, skill_name))
    else:
        conn.execute("INSERT INTO my_skills (skill_name, level) VALUES (?, ?)", (skill_name, level))

    conn.commit()
    conn.close()
    return jsonify({"message": "Skill saved"}), 201


@app.route("/my-skills", methods=["GET"])
def get_my_skills():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM my_skills").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/my-skills/<int:skill_id>", methods=["DELETE"])
def delete_my_skill(skill_id):
    conn = get_connection()
    conn.execute("DELETE FROM my_skills WHERE id = ?", (skill_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Skill deleted"})


@app.route("/skill-impact", methods=["GET"])
def skill_impact_route():
    return jsonify(get_skill_impact())


@app.route("/top-recommendation", methods=["GET"])
def top_recommendation_route():
    return jsonify(get_top_recommendation())


@app.route("/applications", methods=["POST"])
def add_application():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    role_title = data.get("role_title")
    company = data.get("company", "")
    date_applied = data.get("date_applied", "")
    status = data.get("status", "Saved")
    notes = data.get("notes", "")

    if not role_title:
        return jsonify({"error": "role_title is required"}), 400

    conn = get_connection()
    conn.execute(
        "INSERT INTO applications (role_title, company, date_applied, status, notes) VALUES (?, ?, ?, ?, ?)",
        (role_title, company, date_applied, status, notes)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Application saved"}), 201


@app.route("/applications", methods=["GET"])
def get_applications():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/applications/<int:app_id>", methods=["PUT"])
def update_application_status(app_id):
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "status is required"}), 400

    conn = get_connection()
    conn.execute("UPDATE applications SET status = ? WHERE id = ?", (data["status"], app_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Status updated"})


@app.route("/applications/<int:app_id>", methods=["DELETE"])
def delete_application(app_id):
    conn = get_connection()
    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Application deleted"})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
