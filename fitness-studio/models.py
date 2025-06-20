from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FitnessClass(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.String(20), nullable=False)  # stored in IST
    instructor = db.Column(db.String(50), nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    class_name = db.Column(db.String(50),db.ForeignKey('classes.name'))
    client_name = db.Column(db.String(50))
    client_email = db.Column(db.String(100))
