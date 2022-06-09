from app import db, create_app
from app.models import User, Devinfo, Department, Permit_computer

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Devinfo': Devinfo, 'Department': Department, 'Permit_computer': Permit_computer}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
