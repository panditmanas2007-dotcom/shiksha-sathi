import json
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

def load_scholarships():
    try:
        with open("scholarships.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    scholarships = load_scholarships()
    eligible_scholarships = None
    searched = False
    current_date = datetime.now().strftime("%Y-%m-%d")

    # TFWS check flag based on input
    tfws_eligible = False

    if request.method == "POST":
        searched = True
        percentage = float(request.form.get("percentage", 0))
        income = float(request.form.get("income", 0))
        gender = request.form.get("gender", "ALL")
        category = request.form.get("category", "General")
        course = request.form.get("course", "ALL")

        # TFWS Rule: AICTE rule says Family Income < 8 LPA for 100% Tuition Fee Waiver in Engineering
        if income <= 8.0 and (course == "B.Tech" or course == "ALL"):
            tfws_eligible = True

        matched = []
        for item in scholarships:
            # 1. Deadline verification
            if item.get("deadline") and item["deadline"] < current_date:
                continue

            # 2. Percentage verification
            if percentage < item.get("min_percentage", 0):
                continue

            # 3. Family income limit
            if income > item.get("max_income_lpa", 999):
                continue

            # 4. Gender match
            if item.get("gender") != "ALL" and item.get("gender") != gender:
                continue

            # 5. Category match
            if item.get("category") != "ALL":
                if item.get("category") == "SC/ST" and category not in ["SC", "ST"]:
                    continue
                if item.get("category") == "OBC" and category != "OBC":
                    continue
                if item.get("category") == "General/OBC" and category not in ["General", "OBC", "EWS"]:
                    continue

            # 6. Course match
            if item.get("course") != "ALL" and course != "ALL" and item.get("course") != course:
                continue

            matched.append(item)

        matched.sort(key=lambda x: x.get("deadline", "9999-12-31"))
        eligible_scholarships = matched

    return render_template(
        "index.html", 
        scholarships=eligible_scholarships, 
        searched=searched,
        tfws_eligible=tfws_eligible
    )

@app.route("/loans")
def loans():
    # Dedicated page for Education Loan Schemes & Interest Subsidy (CSIS)
    return render_template("loans.html")

if __name__ == "__main__":
    app.run(debug=True)