from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from extensions import bcrypt


# No Flask app initialization here.
# Assuming db and migrate are initialized in app.py
db = SQLAlchemy()
migrate = Migrate()


class Student(db.Model, SerializerMixin):
    # name,
    @validates('name')
    def name_is_short(self,key,student_name):
        if len(student_name) < 5:
            raise ValueError("Student Name has to be greater than 5")
        return student_name
    
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(120),nullable = False)
    role = db.Column(db.String(50), nullable=False, default='user') 

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "Password": self.password_hash
        }

    def set_password (self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
