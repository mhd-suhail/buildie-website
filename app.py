from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = "buildcore_secret"

# DATABASE CONFIG

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# DATABASE MODEL

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    category = db.Column(db.String(100))

    image = db.Column(db.String(300))

# HOME PAGE

@app.route("/")
def home():
    return render_template("index.html")

# ABOUT PAGE

@app.route("/about")
def about():
    return render_template("about.html")

# SERVICES PAGE

@app.route("/services")
def services():
    return render_template("services.html")

# PROJECTS PAGE

@app.route("/projects")
def projects():
    return render_template("projects.html")

# CONTACT PAGE

@app.route("/contact")
def contact():
    return render_template("contact.html")

# CATEGORY PAGE

@app.route("/category/<name>")
def category(name):

    projects = Project.query.filter_by(category=name).all()

    return render_template(
        "category.html",
        projects=projects,
        category=name
    )
# PROJECT DETAILS PAGE

@app.route("/project/<int:id>")
def project_details(id):

    project = Project.query.get(id)

    return render_template(
        "project_details.html",
        project=project
    )

# ADMIN LOGIN

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":

            session["admin"] = True

            return redirect("/admin-dashboard")

    return render_template("admin_login.html")

# ADMIN DASHBOARD

@app.route("/admin-dashboard", methods=["GET", "POST"])
def admin_dashboard():

    if not session.get("admin"):
        return redirect("/admin-login")

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        category = request.form.get("category")

        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

        new_project = Project(
            title=title,
            description=description,
            category=category,
            image=filename
        )

        db.session.add(new_project)
        db.session.commit()

    projects = Project.query.all()

    return render_template(
        "admin_dashboard.html",
        projects=projects
    )
# DELETE PROJECT

@app.route("/delete-project/<int:id>")
def delete_project(id):

    if not session.get("admin"):
        return redirect("/admin-login")

    project = Project.query.get(id)

    db.session.delete(project)

    db.session.commit()

    return redirect("/admin-dashboard")
# UPDATE PROJECT

@app.route("/update-project/<int:id>", methods=["GET", "POST"])
def update_project(id):

    if not session.get("admin"):
        return redirect("/admin-login")

    project = Project.query.get(id)

    if request.method == "POST":

        project.title = request.form.get("title")

        project.description = request.form.get("description")

        project.category = request.form.get("category")

        image = request.files["image"]

        if image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            project.image = filename

        db.session.commit()

        return redirect("/admin-dashboard")

    return render_template(
        "update_project.html",
        project=project
    )
# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# CREATE DATABASE

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)