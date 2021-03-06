from functools import wraps
from flask import current_app as app
from flask_jwt import _jwt_required


def jwt_required(fn, realm=None):
    """
    Modified from original jwt_required to comply with `flask-rest-jsonapi` decorator conventions
    View decorator that requires a valid JWT token to be present in the request
    :param fn: function to be decorated
    :param realm: an optional realm
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        _jwt_required(realm or app.config['JWT_DEFAULT_REALM'])
        return fn(*args, **kwargs)

    return decorator
