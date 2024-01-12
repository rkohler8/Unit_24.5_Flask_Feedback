from app import app
from models import db, User, Feedback


db.drop_all()
db.create_all()

user1 = User.register(
    username="russ",
    pwd="123",
    email='email@email.com',
    first_name='Russell',
    last_name='Kohler'
)

db.session.add_all([user1])

db.session.commit()

feed1 = Feedback(
    title="test-title",
    content='feedback content example here',
    username=user1.username
)
feed2 = Feedback(
    title="test-title2",
    content='More feedback content example here',
    username=user1.username
)

db.session.add_all([feed1, feed2])

db.session.commit()