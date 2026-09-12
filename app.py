import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Load Scholarship Database
def load_scholarships():
    file_path = os.path.join(os.path.dirname(__file__), 'scholarships.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def clean_income_string(income_str):
    """Converts strings like '₹4,50,000' or '450000' to integer."""
    if not income_str or "No Limit" in income_str or "BPL" in income_str:
        return float('inf')
    clean = income_str.replace('₹', '').replace(',', '').replace('/year', '').strip()
    try:
        return float(clean)
    except ValueError:
        return float('inf')

@app.route('/', methods=['GET', 'POST'])
def index():
    scholarships_data = load_scholarships()
    matched_scholarships = []
    tfws_eligible = False
    submitted = False
    
    # Defaults for form fields
    form_data = {
        "marks_obtained": "",
        "total_marks": "500",
        "percentage": "",
        "income": "",
        "category": "General",
        "gender": "Male",
        "course": ""
    }

    if request.method == 'POST':
        submitted = True
        form_data["marks_obtained"] = request.form.get("marks_obtained", "")
        form_data["total_marks"] = request.form.get("total_marks", "500")
        form_data["income"] = request.form.get("income", "0")
        form_data["category"] = request.form.get("category", "General")
        form_data["gender"] = request.form.get("gender", "Male")
        form_data["course"] = request.form.get("course", "")

        # Calculate percentage
        try:
            obtained = float(form_data["marks_obtained"])
            total = float(form_data["total_marks"])
            percentage = round((obtained / total) * 100, 2) if total > 0 else 0.0
            form_data["percentage"] = f"{percentage}%"
        except (ValueError, ZeroDivisionError):
            percentage = 0.0
            form_data["percentage"] = "0%"

        # Parse family income
        try:
            user_income = float(form_data["income"])
        except ValueError:
            user_income = 0.0

        # TFWS Eligibility Logic (Income <= 8 LPA and Technical/Engineering courses)
        engineering_keywords = ["Engineering", "CSE", "AI", "IT", "ECE", "EE", "ME", "CE", "Diploma", "Technology"]
        is_technical = any(kw.lower() in form_data["course"].lower() for kw in engineering_keywords)
        if user_income <= 800000 and is_technical:
            tfws_eligible = True

        # Matching Logic
        for sch in scholarships_data:
            sch_income_limit = clean_income_string(sch.get("income_limit", "No Limit"))
            desc = sch.get("description", "").lower()
            name = sch.get("name", "").lower()

            # Income Check
            if user_income > sch_income_limit:
                continue

            # Gender specific filters
            if "girl" in desc or "women" in desc or "female" in desc or "kanya" in name or "ladli" in name:
                if form_data["gender"].lower() not in ["female", "girl"]:
                    continue

            matched_scholarships.append(sch)

    return render_template(
        'index.html',
        form=form_data,
        scholarships=matched_scholarships,
        tfws_eligible=tfws_eligible,
        submitted=submitted,
        total_count=len(scholarships_data)
    )

if __name__ == '__main__':
    app.run(debug=True)