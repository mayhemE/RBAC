from functools import wraps
from flask import jsonify, session

# login required
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"Message": "Unauthorized. Please Log in!"}), 401
        
        return fn(*args, **kwargs)

    return wrapper

def login(fn):
    pass



