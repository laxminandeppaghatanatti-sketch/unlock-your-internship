from database import get_connection

PRIORITY_WEIGHT = {
    "Dream": 4,
    "High": 3,
    "Target": 2,
    "Backup": 1
}


def get_skill_impact():
    conn = get_connection()

    targets = conn.execute("SELECT * FROM targets").fetchall()
    my_skills_rows = conn.execute("SELECT skill_name, level FROM my_skills").fetchall()
    conn.close()

    my_skills = {row["skill_name"].lower(): row["level"] for row in my_skills_rows}

    skill_data = {}

    for target in targets:
        conn = get_connection()
        skills = conn.execute(
            "SELECT skill_name FROM target_skills WHERE target_id = ?", (target["id"],)
        ).fetchall()
        conn.close()

        weight = PRIORITY_WEIGHT.get(target["priority"], 1)

        for row in skills:
            skill_name = row["skill_name"].lower()

            if skill_name not in skill_data:
                skill_data[skill_name] = {
                    "skill": skill_name,
                    "affects_targets": 0,
                    "impact_score": 0,
                    "target_titles": [],
                    "current_level": my_skills.get(skill_name, 0)
                }

            skill_data[skill_name]["affects_targets"] += 1
            skill_data[skill_name]["impact_score"] += weight
            skill_data[skill_name]["target_titles"].append(target["role_title"])

    results = list(skill_data.values())

    # Only recommend skills where a real gap exists (not already strong)
    results_with_gap = [r for r in results if r["current_level"] < 60]

    results_with_gap.sort(key=lambda r: r["impact_score"], reverse=True)

    return results_with_gap


def get_top_recommendation():
    ranked = get_skill_impact()
    if not ranked:
        return {
            "message": "No skill gaps found across your saved targets — you're covered, or add more targets to compare."
        }

    top = ranked[0]
    target_count = len(set(top["target_titles"]))
    unique_titles = list(set(top["target_titles"]))

    return {
        "skill": top["skill"],
        "current_level": top["current_level"],
        "affects_targets": target_count,
        "target_titles": unique_titles,
        "impact_score": top["impact_score"],
        "why": f"{top['skill'].upper()} is required by {target_count} of your saved target internships "
               f"({', '.join(unique_titles)}), and your current level is {top['current_level']}/100. "
               f"Improving this skill has the highest combined impact across your targets."
    }
