from . import db
from flask_login import UserMixin
from datetime import datetime

# =======================
# USER MODEL
# =======================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)   # admin, adopter, vet

    adoptions = db.relationship('Adoption', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


# =======================
# PET MODEL
# =======================
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    species = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.Text)

    # Pet adoption status
    status = db.Column(db.String(20), default="available")  
    # available / pending / adopted

    adoptions = db.relationship('Adoption', backref='pet', lazy=True)
    medical_records = db.relationship(
        "MedicalRecord",
        cascade="all, delete-orphan",
        passive_deletes=True,
        backref="pet"
    )


    def __repr__(self):
        return f"<Pet {self.name} - {self.status}>"


# =======================
# ADOPTION MODEL
# =======================
class Adoption(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)

    adopted_on = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default="requested")
    # requested / approved / rejected

    def __repr__(self):
        return f"<Adoption User:{self.user_id} Pet:{self.pet_id} Status:{self.status}>"


# =======================
# MEDICAL RECORD MODEL
# =======================
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    record_id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id', ondelete='CASCADE'), nullable=False)

    treatment = db.Column(db.String(255), nullable=False)
    diagnosis = db.Column(db.String(255), nullable=False)

    # ❌ REMOVED: medication text column
    # medication = db.Column(db.String(255))

    visit_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)

    # ⭐ Foreign key pointing to medicines table
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.med_id', ondelete="SET NULL"))

    # Relationship to Medicine table
    medicine = db.relationship("Medicine", back_populates="medical_records")

    # Link medical record to pet
    


# =======================
# MEDICINE MODEL
# =======================
class Medicine(db.Model):
    __tablename__ = 'medicines'

    med_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    medical_records = db.relationship("MedicalRecord", back_populates="medicine")
