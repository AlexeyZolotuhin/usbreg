from app import db, create_app
from app.models import User, Devinfo, Department, Permit_computer


app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Devinfo': Devinfo, 'Department': Department, 'Permit_computer': Permit_computer}