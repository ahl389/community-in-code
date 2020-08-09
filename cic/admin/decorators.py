from functools import wraps
from flask import g, request, redirect, url_for
from flask_login import current_user


# Defining our custom decorator
def roles_required(roles):
    def roles_required2(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if current_user:
                if current_user.role and current_user.role.name not in roles:
                    return redirect(url_for('admin.whoops'))
                return func(*args, **kwargs) 
            return func(*args, **kwargs) 
        return decorated_function
    return  roles_required2
