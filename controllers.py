from flask import Flask, request, jsonify, session,  make_response
from flask_restful import Api,Resource
from decorator import login_required
from app import app
from models import Student, db, migrate, User # Import db and migrate from models.py
from werkzeug.exceptions import BadRequest

api = Api(app)



@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return str(e)

class Register(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    def post(self):
        data  = request.get_json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")

        if not username and not password:
            return {"Message":"Username and password are required"}, 400
        
        existing_user = User.query.filter_by(username = username)

        if existing_user:
            return {"Message": "User already exists"}, 400
        
        new_user = User(username = username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return {
            "message": "User created successfully!"
        }, 201

api.add_resource(Register, "/register")

class Login(Resource):
    def post(self):
        data  = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user  = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return {"Message":"Invalid credentials"}, 401

        session["user_id"] = user.id
        return {"Message":"Login successful"}, 200

api.add_resource(Login,"/login")

class Logout(Resource):
    def post(self):
        session.pop("user_id", None)
        return {"Message":" Logout successful"}

api.add_resource(Logout,"/logout")


class StudentsApi(Resource):
    def get(self, id=None):
        """Return student with matching ID if ID has been passed"""
        if id:
            student = Student.query.get(id)
            if not student:
                return {"error": "Student not found"}, 404
            return student.to_dict()

        """Returns a list of all students."""
        all_students = Student.query.all()
        students_list = [std.to_dict() for std in all_students]
        return students_list

    def post(self):
        data = request.get_json()
        name = data.get('name')

        student = Student(name=name)
        db.session.add(student)
        db.session.commit()

        return {"message": "Student created successfully"}, 201

# add a route to the resource
api.add_resource(StudentsApi, '/students', '/students/<int:id>')
