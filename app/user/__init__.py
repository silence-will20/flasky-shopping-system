from flask import Blueprint
from ..models import Permission

user = Blueprint('user', __name__)

@user.app_context_processor
def inject_permissions(): 
    return dict(Permission=Permission)

from . import views, forms