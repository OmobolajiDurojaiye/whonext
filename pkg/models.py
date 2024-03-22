from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
db=SQLAlchemy()

class Participants(db.Model):
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(225), nullable=False)
    last_winning_date = db.Column(db.Date)