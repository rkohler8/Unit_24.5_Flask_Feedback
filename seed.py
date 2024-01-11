from app import app
from models import db, User


db.drop_all()
db.create_all()

user1 = User(
    username="russ",
    password="123",
    email='email@email.com',
    first_name='Russell',
    last_name='Kohler'
)

db.session.add_all([user1])
db.session.commit()