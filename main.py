from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

announcements = []
discussions = []
resources = [
    {'name': 'Course Materials', 'url': '/static/coursematerial.pdf'}, 
    {'name': 'Readings', 'url': '/static/coursematerial.pdf'},  
    {'name': 'Study Guides', 'url': '/static/insert.pdf'} 
]
attendance = {}  # {date: {student_name: reason}}
upcoming_assignments = [
    {'name': 'Assignment 1', 'due_date': '2024-08-30'},
    {'name': 'Assignment 2', 'due_date': '2024-09-15'}
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes

@app.route('/', methods=['GET','POST']) #home page
def home():  
    announcements = []
    discussions = []
    if request.method == 'POST':
        if 'announcement' in request.form:
            announcements = add_announcement()
        elif 'discussion' in request.form:
            discussions = add_discussion()
    return render_template('home.html', announcements=announcements, discussions=discussions, 
                               upcoming_assignments=upcoming_assignments, resources=resources)

# Announcement routes
def add_announcement():
    print(123)
    announcement_text = request.form['announcement']
    if announcement_text: #not empty
            #file closes after with block
        with open('announcements.txt', 'a') as file:
            file.write(f"{datetime.now()} - {announcement_text}\n")

    announcements = [] # store a list of dictionaries
    try:
            #file closes after with block
        with open('announcements.txt', 'r') as file:
            for line in file:
                datetime_str, announcement_text = line.split(" - ", 1) # split at first instance of "-"
                announcements.append({'datetime': datetime_str, 'announcement': announcement_text.strip()})
    except FileNotFoundError:
        pass
    return announcements

# Discussion routes
def add_discussion():
    discussion_text = request.form['discussion']
    if discussion_text: #not empty
        #file closes after with block
        with open('discussions.txt', 'a') as file:
            file.write(f"{datetime.now()} - {discussion_text}\n")
       
    discussions = [] # store a list of dictionaries
    try:
        #file closes after with block
        with open('discussions.txt', 'r') as file:
            for line in file:
                datetime_str, discussion_text = line.split(" - ", 1) # split at first instance of "-"
                discussions.append({'datetime': datetime_str, "discussion": discussion_text.strip()})
    except FileNotFoundError:
        pass
    return discussions
        
# Timetable routes
@app.route('/<filename>')
def timetable(filename):
    return send_from_directory('static', filename)

# External resources routes
@app.route('/external_resources')
def external_resources():
    return redirect(url_for('home'))

# Attendance routes
@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    if request.method == 'POST':
        date = request.form['date']
        absent_students = request.form.getlist('absent_students')
        reasons = request.form.getlist('reasons')

        # Initialize attendance for the date
        attendance[date] = {} 
        
        # Mark absent students with their reasons
        for student, reason in zip(absent_students, reasons):
            attendance[date][student] = reason

        # Get all student names
        all_students = get_all_student_names()  

        # Mark all other students as present
        for student in all_students:
            if student not in attendance[date]:
                attendance[date][student] = "Present"

    return render_template('teacher.html', attendance=attendance)

def get_all_student_names():
    #file closes after with block
    stu_names = []
    with open('static/student_names.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            stu_names.append(row[0])
    return stu_names

# Students routes
@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        student_name = request.form['student_name']

        try:
            with open('static/student_scores.csv', 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                student_score = [row for row in reader if row[0] == student_name]
        except FileNotFoundError:
            return render_template('error.html', message="Student data file not found.")
        except Exception as e:
            return render_template('error.html', message=f"An error occurred: {str(e)}")

        return render_template('student.html', student_score=student_score, upcoming_assignments=upcoming_assignments)
    else:
        return render_template('student.html', upcoming_assignments=upcoming_assignments)

# Run webapp
if __name__ == '__main__':
    app.run(debug=True, port=5555)