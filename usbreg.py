from app import app, db
from app.models import User, Devinfo, Department, Permit_computer

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Devinfo': Devinfo, 'Department': Department, 'Permit_computer': Permit_computer}