from flask import Flask, request, jsonify, session,  make_response
from flask_restful import Api,Resource
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from decorator import login_required


from models import Student, db, migrate, User # Import db and migrate from models.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


CORS(app)
db.init_app(app) # Initialize db with the app
migrate.init_app(app, db) # Initialize migrate with app and db
api = Api(app)
# class that inherits Resource, then define your endpoints as methods of the class.
# ensure the endpoint names are the same as the http verbs they represent.  
# get all, get one, post, patch, delete

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



# @app.route('/students', methods=['GET'])
# def get_all_students():
#     """Returns a list of all students."""
#     all_students = Student.query.all()
#     students_list = [std.to_dict() for std in all_students]
#     return jsonify(students_list)

# @app.route('/students', methods=['POST'])
# def create_student():
#     """Creates a new student."""
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Invalid data"}), 400
#     try:
#         new_student = Student(name=data['name'])
#         db.session.add(new_student)
#         db.session.commit()
#         return jsonify(new_student.to_dict()), 201
#     except KeyError:
#         return jsonify({"error": "Missing required fields"}), 400

# @app.route('/students/<int:student_id>', methods=['GET'])
# def get_student(student_id):
#     """Returns a single student by ID."""
#     student = Student.query.get(student_id)
#     if not student:
#         return jsonify({"error": "Student not found"}), 404
#     return jsonify(student.to_dict())

# @app.route('/students/<int:student_id>', methods=['PATCH'])
# def update_student(student_id):
#     """Updates a student's information by ID."""
#     student = Student.query.get(student_id)
#     if not student:
#         return jsonify({"error": "Student not found"}), 404
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "Invalid data"}), 400
#     try:
#         if 'name' in data:
#             student.name = data['name']
#         db.session.commit()
#         return jsonify(student.to_dict())
#     except KeyError:
#         return jsonify({"error": "Invalid fields"}), 400

# @app.route('/students/<int:student_id>', methods=['DELETE'])
# def delete_student(student_id):
#     """Deletes a student by ID."""
#     student = Student.query.get(student_id)
#     if not student:
#         return jsonify({"error": "Student not found"}), 404
#     db.session.delete(student)
#     db.session.commit()
#     return jsonify({"message": "Student deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
