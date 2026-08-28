
from pcmams import create_app, db
from pcmams.models import User, Pet
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    # sample users
    u1 = User(username='alice', password=generate_password_hash('pass'), role='adopter')
    u2 = User(username='bob', password=generate_password_hash('pass'), role='vet')
    u3 = User(username='admin', password=generate_password_hash('admin'), role='admin')
    db.session.add_all([u1,u2,u3])
    # sample pets
    p1 = Pet(name='Milo', species='Dog', age=3, image=None, description='Friendly dog.')
    p2 = Pet(name='Luna', species='Cat', age=2, image=None, description='Playful cat.')
    db.session.add_all([p1,p2])
    db.session.commit()
    print('Initialized DB with sample data.')
