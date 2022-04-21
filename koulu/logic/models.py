from datetime import datetime
from koulu import db
from flask_login import UserMixin

#decorator to get current user

    
class Members(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    neckname = db.Column(db.String(20))
    email = db.Column(db.String(200))
    password = db.Column(db.String(255))
    image_file = db.Column(db.String(255), nullable=False, default='avatar.jpg')
    gender = db.Column(db.String(10))
    location = db.Column(db.String(50))
    description = db.Column(db.String(100))
    age = db.Column(db.Integer, nullable=False, default=18)
    level = db.Column(db.Integer, nullable=False, default=180)
    activation_code = db.Column(db.Integer, nullable=False, default=1)
    viestit = db.relationship('Viesti', backref='author', lazy=True)

    def __repr__(self):
       return f"<username={self.username}, image_file={self.image_file}>"



class Viesti(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author