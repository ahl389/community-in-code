from functools import wraps
from flask import g, request, redirect, url_for
from flask_login import current_user


# Defining our custom decorator
def roles_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'admin' in current_user.roles:
            return function(*args, **kwargs)
        return redirect(url_for('admin.whoops'))
            
    return wrapper
