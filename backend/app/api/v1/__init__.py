from flask import Blueprint

bp = Blueprint('api/v1', __name__)

from app.api.v1 import users, devices, errors, tokens, auth, departments