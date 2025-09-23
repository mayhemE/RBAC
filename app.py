from flask import Flask, request, jsonify, session,  make_response
from flask_restful import Api,Resource
from flask_cors import CORS
from models import Student, db, migrate, User # Import db and migrate from models.py
import os



def create_app():
    app = Flask(__name__)

    #database
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    
    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()



    return app

# if __name__ == '__main__':
#     app.run(debug=True)

app = create_app()
