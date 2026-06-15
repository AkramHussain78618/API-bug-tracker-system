from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from models import db, User, Bug, Comment
from dotenv import load_dotenv
import os
app = Flask(__name__)

# SECRET KEY
app.secret_key = "bugtrackersecret"


# DATABASE CONFIGURATION
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugtracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# EMAIL CONFIGURATION
load_dotenv()
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

# INITIALIZE MAIL
mail = Mail(app)

# INITIALIZE DATABASE
db.init_app(app)

with app.app_context():
    db.create_all()


# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # CHECK EXISTING EMAIL
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered"

        # CREATE USER
        new_user = User(
            username=username,
            email=email,
            password=password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            return redirect("/dashboard")

        else:
            return "Invalid Email or Password"

    return render_template("login.html")


# DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    role = session["role"].lower()

    # ADMIN: see all bugs including deleted
    if role == "admin":

        bugs = Bug.query.all()

    # TESTER: see all active bugs + own deleted bugs
    elif role == "tester":

        bugs = []

        for bug in Bug.query.all():

            if bug.status != "Deleted":
                bugs.append(bug)

            elif bug.created_by_id == session["user_id"]:
                bugs.append(bug)

    # DEVELOPER: hide deleted bugs
    else:

        bugs = Bug.query.filter(
            Bug.status != "Deleted"
        ).all()

    developers = User.query.filter(
        User.role.ilike("developer")
    ).all()

    total_bugs = Bug.query.filter(
        Bug.status != "Deleted"
    ).count()

    open_bugs = Bug.query.filter_by(
        status="Open"
    ).count()

    in_progress_bugs = Bug.query.filter_by(
        status="In Progress"
    ).count()

    resolved_bugs = Bug.query.filter_by(
        status="Resolved"
    ).count()

    closed_bugs = Bug.query.filter_by(
        status="Closed"
    ).count()

    deleted_bugs = Bug.query.filter_by(
        status="Deleted"
    ).count()

    return render_template(
        "dashboard.html",
        bugs=bugs,
        developers=developers,
        total_bugs=total_bugs,
        open_bugs=open_bugs,
        in_progress_bugs=in_progress_bugs,
        resolved_bugs=resolved_bugs,
        closed_bugs=closed_bugs,
        deleted_bugs=deleted_bugs
    )


# CREATE BUG PAGE
@app.route("/create_bug", methods=["GET", "POST"])
def create_bug():

    if "user_id" not in session:
        return redirect("/login")

    developers = User.query.filter_by(role="developer").all()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]
        bug_source = request.form.get("bug_source", "Unknown")
        assign_to = int(request.form["assign_to"])

        # GET ASSIGNED DEVELOPER
        assigned_dev = db.session.get(User, assign_to)

        # CREATE BUG
        new_bug = Bug(
            title=title,
            description=description,
            priority=priority,
            bug_source=bug_source,
            status="Open",
            assigned_to_id=assign_to,
            created_by_id=session["user_id"]
        )

        db.session.add(new_bug)
        print("Assigned Developer ID:", new_bug.assigned_to_id)
        db.session.commit()

        # SEND EMAIL TO ASSIGNED DEVELOPER ONLY
        try:
            assigned_dev = User.query.get(assign_to)

            print("assign_to =", assign_to)
            print("assigned_dev =", assigned_dev)

            if assigned_dev and assigned_dev.email:
                print("Developer Email =", assigned_dev.email)

                msg = Message(
                    subject="New Bug Assigned",
                    sender=app.config["MAIL_USERNAME"],
                    recipients=[assigned_dev.email]
                )

                msg.body = f"""
Hello {assigned_dev.username},

A new bug has been assigned to you.

Bug Title: {title}
Priority: {priority}
Status: Open

Please log in to the Bug Tracking System to review and resolve the issue.

Regards,
Bug Tracking System
"""

                mail.send(msg)
                print(f"Email sent successfully to {assigned_dev.email}")
            else:
                print("Developer not found or email is missing.")
        except Exception as e:
            print(f"Mail Error: {str(e)}")

        return redirect("/dashboard")

    return render_template("create_bug.html", developers=developers)

# ADD COMMENT
@app.route("/add_comment/<int:id>", methods=["POST"])
def add_comment(id):

    if "user_id" not in session:
        return redirect("/login")

    text = request.form["comment"]

    new_comment = Comment(
        comment=text,
        bug_id=id,
        user_id=session["user_id"]
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect("/dashboard")

# Verify Fix
@app.route("/verify_fix/<int:id>")
def verify_fix(id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"].lower() != "tester":
        return redirect("/dashboard")

    bug = Bug.query.get_or_404(id)

    bug.status = "Closed"

    db.session.commit()

    return redirect("/dashboard")

# Reopen Bug
@app.route("/reopen_bug/<int:id>")
def reopen_bug(id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"].lower() != "tester":
        return redirect("/dashboard")

    bug = Bug.query.get_or_404(id)

    bug.status = "Open"

    # Remove assignment so admin can reassign
    bug.assigned_to_id = None

    db.session.commit()

    return redirect("/dashboard")

# RE-ASSIGN BUG
@app.route("/reassign_bug/<int:id>", methods=["POST"])
def reassign_bug(id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"].lower() != "admin":
        return redirect("/dashboard")

    bug = Bug.query.get_or_404(id)

    developer_id = request.form["developer"]

    bug.assigned_to_id = int(developer_id)

    db.session.commit()

    try:
        assigned_dev = User.query.get(bug.assigned_to_id)

        if assigned_dev:
            msg = Message(
                subject="Bug Reassigned",
                sender=app.config["MAIL_USERNAME"],
                recipients=[assigned_dev.email]
            )

            msg.body = f"""
Hello {assigned_dev.username},

A bug has been reassigned to you.

Bug Title: {bug.title}
Priority: {bug.priority}
Status: {bug.status}

Please login and review the bug.

Regards,
Bug Tracker
"""

            mail.send(msg)
            print("Reassignment email sent")
    except Exception as e:
        print("Reassignment Mail Error:", str(e))

    return redirect("/dashboard")

# /edit_bug/<id>
@app.route("/edit_bug/<int:id>", methods=["GET", "POST"])
def edit_bug(id):
    if "user_id" not in session:
        return redirect("/login")

    bug = Bug.query.get_or_404(id)

    role = session["role"].lower()

    # Admin can edit any bug
    if role == "admin":
        pass

    # Tester can edit only own bug
    elif role == "tester":
        if bug.created_by_id != session["user_id"]:
            return redirect("/dashboard")

    else:
        return redirect("/dashboard")

    if request.method == "POST":
        bug.title = request.form["title"]
        bug.description = request.form["description"]
        bug.priority = request.form["priority"]
        bug.bug_source = request.form["bug_source"]

        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "edit_bug.html",
        bug=bug
    )


# UPDATE BUG STATUS
@app.route("/update_status/<int:id>")
def update_status(id):
    if "user_id" not in session:
        return redirect("/login")

    bug = Bug.query.get_or_404(id)

    if session["role"].lower() != "developer":
        return redirect("/dashboard")

    if bug.assigned_to_id != session["user_id"]:
        return redirect("/dashboard")

    if bug.status.lower() == "open":
        bug.status = "In Progress"
    elif bug.status.lower() == "in progress":
        bug.status = "Resolved"

    db.session.commit()

    return redirect("/dashboard")



# TEST EMAIL ROUTE
@app.route("/test_mail")
def test_mail():

    try:

        msg = Message(
            subject="Bug Tracker Test Email",
            sender=app.config["MAIL_USERNAME"],
            recipients=[app.config["MAIL_USERNAME"]]
        )

        msg.body = "Bug Tracker Email Notification Working Successfully"

        mail.send(msg)

        return "Email Sent Successfully"

    except Exception as e:

        return str(e)
    
# Delete bug route
@app.route("/delete_bug/<int:id>")
def delete_bug(id):

    if "user_id" not in session:
        return redirect("/login")

    bug = Bug.query.get_or_404(id)

    role = session["role"].lower()

    # Admin can delete any bug
    # Admin can soft delete any bug
    if role == "admin":
        db.session.delete(bug)
        db.session.commit()
        return redirect("/dashboard")

    # Tester can delete only own unassigned bug
    elif role == "tester" and bug.created_by_id == session["user_id"]:
        db.session.delete(bug)
        db.session.commit()
        return redirect("/dashboard")

    else:
        return redirect("/dashboard")

# Restore Route
@app.route("/restore_bug/<int:id>")
def restore_bug(id):

    if "user_id" not in session:
        return redirect("/login")

    bug = Bug.query.get_or_404(id)

    role = session["role"].lower()

    if role == "admin":

        bug.status = "Open"

    elif role == "tester" and bug.created_by_id == session["user_id"]:

        bug.status = "Open"

    else:

        return redirect("/dashboard")

    db.session.commit()

    return redirect("/dashboard")

    
# LOGOUT PAGE
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
    
#Delete all deleted bugs route
@app.route("/cleanup_deleted")
def cleanup_deleted():

    deleted_bugs = Bug.query.filter_by(status="Deleted").all()

    for bug in deleted_bugs:
        db.session.delete(bug)

    db.session.commit()

    return "Deleted bugs cleaned successfully"
# Test email