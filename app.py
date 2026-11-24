# Student Report Card Generator
# Beginner-friendly website using Python standard library only.
# No Flask or other package installation is required.

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote
import json
import os
import html

HOST = "127.0.0.1"
PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")

SUBJECTS = ["English", "Maths", "Science", "Computer", "Social Science"]


def load_students():
    """Read saved student records from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_students(students):
    """Save all student records in the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=4)


def calculate_result(marks):
    """Calculate total, percentage, grade and pass/fail result."""
    total = sum(marks)
    percentage = total / len(marks)

    if any(mark < 33 for mark in marks):
        grade = "F"
        result = "Fail"
    else:
        result = "Pass"
        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "E"

    return total, round(percentage, 2), grade, result


def safe(value):
    """Escape text before showing it on the web page."""
    return html.escape(str(value))


def page(title, content):
    """Create the common layout used by all website pages."""
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>""" + safe(title) + """</title>
<style>
body{font-family:Arial,sans-serif;background:#edf2f8;margin:0;padding:22px;color:#1f2937}
.container{max-width:760px;margin:20px auto;background:white;padding:26px;border-radius:12px;box-shadow:0 3px 14px #0001}
h1,h2{color:#174b87;text-align:center}
p.note{text-align:center;color:#536273}
label{display:block;margin-top:12px;font-weight:bold}
input{width:100%;box-sizing:border-box;padding:10px;margin-top:5px;border:1px solid #cbd5e1;border-radius:6px}
button,.button{display:inline-block;background:#174b87;color:white;padding:11px 18px;border:0;border-radius:6px;text-decoration:none;cursor:pointer;margin-top:16px}
button:hover,.button:hover{background:#103762}
table{width:100%;border-collapse:collapse;margin-top:18px}
th,td{border:1px solid #cbd5e1;padding:10px;text-align:left}
th{background:#e7eff9}
.error{background:#fff0f0;color:#a11;padding:10px;border-radius:6px}
.success{color:#176b37}
.actions{text-align:center}
.small{font-size:13px;color:#64748b}
@media print{body{background:white;padding:0}.container{box-shadow:none;margin:0}.no-print{display:none}}
</style>
</head>
<body><div class="container">""" + content + """</div></body></html>"""


def home_page(message=""):
    students = load_students()
    msg = '<p class="error">' + safe(message) + '</p>' if message else ""
    rows = ""
    for student in students:
        rows += (
            "<tr><td>" + safe(student["name"]) + "</td>"
            "<td>" + safe(student["roll"]) + "</td>"
            '<td><a href="/report?roll=' + quote(student["roll"]) + '">View report</a></td></tr>'
        )
    if not rows:
        rows = '<tr><td colspan="3">No student records saved yet.</td></tr>'

    content = """
<h1>Student Report Card Generator</h1>
<p class="note">Enter student details and marks to generate a report card.</p>
""" + msg + """
<form method="POST" action="/save">
<label>Student Name</label><input name="name" required maxlength="60">
<label>Roll Number</label><input name="roll" required maxlength="20">
<label>Course / Class</label><input name="course" required maxlength="40">
<h2>Subject Marks (Out of 100)</h2>
"""
    for subject in SUBJECTS:
        content += '<label>' + safe(subject) + '</label>'
        content += '<input type="number" name="' + safe(subject) + '" min="0" max="100" required>'
    content += """
<div class="actions"><button type="submit">Generate Report Card</button></div>
</form>
<hr>
<h2>Saved Student Records</h2>
<table><tr><th>Name</th><th>Roll Number</th><th>Report</th></tr>""" + rows + """</table>
<p class="small">Records are saved in students.json in this project folder.</p>
"""
    return page("Student Report Card Generator", content)


def report_page(student):
    rows = ""
    for subject, marks in student["subjects"].items():
        rows += "<tr><td>" + safe(subject) + "</td><td>" + safe(marks) + "</td></tr>"

    content = """
<h1>STUDENT REPORT CARD</h1>
<p class="note">Student Academic Performance</p>
<p><b>Name:</b> """ + safe(student["name"]) + """</p>
<p><b>Roll Number:</b> """ + safe(student["roll"]) + """</p>
<p><b>Course / Class:</b> """ + safe(student["course"]) + """</p>
<table><tr><th>Subject</th><th>Marks</th></tr>""" + rows + """</table>
<h2>Total: """ + safe(student["total"]) + """ / 500</h2>
<h2>Percentage: """ + safe(student["percentage"]) + """%</h2>
<h2>Grade: """ + safe(student["grade"]) + """</h2>
<h2>Result: """ + safe(student["result"]) + """</h2>
<div class="actions no-print">
<p>To print or save this report as PDF, press Ctrl+P on your keyboard.</p>
<a class="button" href="/">Back to Home</a>
</div>
"""
    return page("Student Report Card", content)


class WebsiteHandler(BaseHTTPRequestHandler):
    def send_page(self, content, status=200):
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.send_page(home_page())
        elif self.path.startswith("/report"):
            query = self.path.split("?", 1)
            params = parse_qs(query[1]) if len(query) > 1 else {}
            roll = params.get("roll", [""])[0]
            for student in load_students():
                if student["roll"] == roll:
                    self.send_page(report_page(student))
                    return
            self.send_page(page("Not Found", '<h1>Student record not found</h1><p><a href="/">Back to Home</a></p>'), 404)
        else:
            self.send_page(page("Not Found", '<h1>Page not found</h1><p><a href="/">Back to Home</a></p>'), 404)

    def do_POST(self):
        if self.path != "/save":
            self.send_page(page("Not Found", '<h1>Page not found</h1><p><a href="/">Back to Home</a></p>'), 404)
            return

        length = int(self.headers.get("Content-Length", 0))
        form_data = self.rfile.read(length).decode("utf-8")
        form = parse_qs(form_data)

        def value(key):
            return form.get(key, [""])[0].strip()

        name = value("name")
        roll = value("roll")
        course = value("course")

        if not name or not roll or not course:
            self.send_page(home_page("Please fill in all student details."), 400)
            return

        students = load_students()
        if any(s["roll"].lower() == roll.lower() for s in students):
            self.send_page(home_page("This roll number already exists. Use a different roll number."), 400)
            return

        try:
            marks = [int(value(subject)) for subject in SUBJECTS]
        except ValueError:
            self.send_page(home_page("Please enter valid whole-number marks for every subject."), 400)
            return

        if any(mark < 0 or mark > 100 for mark in marks):
            self.send_page(home_page("Marks must be between 0 and 100."), 400)
            return

        total, percentage, grade, result = calculate_result(marks)
        student = {
            "name": name,
            "roll": roll,
            "course": course,
            "subjects": dict(zip(SUBJECTS, marks)),
            "total": total,
            "percentage": percentage,
            "grade": grade,
            "result": result
        }

        students.append(student)
        save_students(students)
        self.send_page(report_page(student))

    def log_message(self, format, *args):
        # Keep terminal output short and readable.
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    print("Student Report Card Generator is starting...")
    print("Open this address in your browser: http://127.0.0.1:8000")
    print("Keep this window open while using the website.")
    try:
        server = HTTPServer((HOST, PORT), WebsiteHandler)
        server.serve_forever()
    except OSError:
        print("Could not start the website. Port 8000 may already be in use.")
    except KeyboardInterrupt:
        print("\nWebsite stopped.")
