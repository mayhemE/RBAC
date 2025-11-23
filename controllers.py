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

# A login resource
class Login(Resource):
    """
    Handles user login functionality.

    This endpoint accepts a POST request with a JSON payload containing the user's
    username and password. It authenticates the user and, if successful, stores
    the user's ID in the session.

    Parameters:
    data (dict): A JSON object containing the following keys:
        - username (str): The user's username.
        - password (str): The user's password.

    Returns:
    dict: A JSON response with the following keys:
        - Message (str): A status message indicating the result of the login attempt.
    
    Raises:
    HTTPException: If the provided username and password are invalid, a 401 Unauthorized
        response is returned.

    Example Usage:
    ```python
    import requests

    data = {
        "username": "myusername",
        "password": "mypassword"
    }
    response = requests.post("/login", json=data)
    print(response.json())
    ```

    Notes:
    - This endpoint assumes that the `User` model has a `check_password` method that
      verifies the provided password against the stored hashed password.
    - The user's ID is stored in the session, which should be used for subsequent
      authenticated requests.
    - Developers should ensure that the session is properly managed and secured to
      prevent unauthorized access.
    """
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return {"Message": "Invalid credentials"}, 401

        session["user_id"] = user.id
        return {"Message": "Login successful"}, 200

api.add_resource(Login, "/login")

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
