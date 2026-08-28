import os
from werkzeug.utils import secure_filename
from flask import current_app, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Pet, Adoption, MedicalRecord, Medicine
from . import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/adopt/<int:pet_id>', methods=['POST'])
@login_required
def adopt(pet_id):
    pet = Pet.query.get_or_404(pet_id)

    # Trigger message if already adopted
    if pet.status == 'adopted':
        flash('You cannot adopt this pet because it is already adopted.', 'danger')
        return redirect(url_for('main.index'))

    # Trigger message if pending
    if pet.status == 'pending':
        flash('An adoption request for this pet is already pending.', 'warning')
        return redirect(url_for('main.index'))

    # Create adoption request
    adoption = Adoption(
        user_id=current_user.id,
        pet_id=pet.id,
        status='pending'
    )

    # Update pet status
    pet.status = "pending"

    db.session.add(adoption)
    db.session.add(pet)  # VERY IMPORTANT
    db.session.commit()

    flash('Adoption request submitted.', 'success')
    return redirect(url_for('main.dashboard'))

# ---------------------------------------------------------
# WELCOME PAGE
# ---------------------------------------------------------
@main_bp.route('/')
def home():
    return render_template('welcome.html')

@main_bp.route('/view_adoption_summary')
@login_required
def view_adoption_summary():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    # Query the SQL View
    result = db.session.execute(text("SELECT * FROM adopter_adoption_summary"))
    summary_data = result.fetchall()

    return render_template('view_adoption_summary.html', summary=summary_data)
# ---------------------------------------------------------
# PET DETAILS PAGE
# ---------------------------------------------------------
@main_bp.route('/pet/<int:pet_id>')
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('pet_detail.html', pet=pet)


# ---------------------------------------------------------
# DASHBOARD (ADMIN / ADOPTER)
# ---------------------------------------------------------
@main_bp.route('/dashboard')
@login_required
def dashboard():
    from .models import User

    if current_user.role == 'admin':
        users = User.query.all()
        pets = Pet.query.all()
        adoptions = Adoption.query.all()
        return render_template('admin_dashboard.html',
                               users=users, pets=pets, adoptions=adoptions)

    elif current_user.role == 'adopter':
        return redirect(url_for('main.index'))

    return "Unauthorized", 403


# ---------------------------------------------------------
# ADOPT PET
# ---------------------------------------------------------

# ---------------------------------------------------------
# ADD PET (ADMIN)
# ---------------------------------------------------------
@main_bp.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        try:
            name = request.form['name']
            species = request.form['species']
            age = int(request.form['age'])
            description = request.form['description']

            image = request.files['image']
            filename = secure_filename(image.filename)
            save_path = os.path.join(current_app.root_path, 'static/product_images', filename)
            image.save(save_path)

            new_pet = Pet(
                name=name,
                species=species,
                age=age,
                description=description,
                image=filename,
                status='available'
            )

            db.session.add(new_pet)
            db.session.commit()
            flash("Pet added successfully!", "success")
            return redirect(url_for('main.view_pets'))

        except SQLAlchemyError as e:
            db.session.rollback()
            msg = str(e.__cause__)

            if "The pets of age above 10 cannot be added" in msg:
                flash("The pets of age above 10 cannot be added!", "danger")
            else:
                flash("Error adding pet: " + msg, "danger")

            return redirect(url_for('main.add_pet'))

    return render_template('add_pet.html')

# ---------------------------------------------------------
# VIEW PETS (ADMIN)
# ---------------------------------------------------------
@main_bp.route('/view_pets')
@login_required
def view_pets():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    pets = Pet.query.all()
    return render_template('view_pets.html', pets=pets)
@main_bp.route('/view_pet_summary')
@login_required
def view_pet_summary():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    query = text("SELECT * FROM pet_medical_summary")
    result = db.session.execute(query)
    summary = result.fetchall()

    return render_template('view_pet_summary.html', summary=summary)

# ---------------------------------------------------------
# VIEW ADOPTIONS (ADMIN)
# ---------------------------------------------------------
@main_bp.route('/view_adoptions')
@login_required
def view_adoptions():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    adoptions = Adoption.query.all()
    return render_template('view_adoptions.html', adoptions=adoptions)


# ---------------------------------------------------------
# EDIT PET
# ---------------------------------------------------------
@main_bp.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403

    pet = Pet.query.get_or_404(pet_id)

    if request.method == 'POST':
        try:
            pet.name = request.form['name']
            pet.species = request.form['species']
            pet.age = int(request.form['age'])
            pet.description = request.form['description']

            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.root_path, 'static/product_images', filename))
                pet.image = filename

            db.session.commit()
            flash("Pet updated successfully!", "success")
            return redirect(url_for('main.view_pets'))

        except SQLAlchemyError as e:
            db.session.rollback()
            msg = str(e.__cause__)

            if "cannot be updated" in msg:
                flash("The pets of age above 10 cannot be updated!", "danger")
            else:
                flash("Error updating pet: " + msg, "danger")

            return redirect(url_for('main.edit_pet', pet_id=pet_id))

    return render_template('edit_pet.html', pet=pet)
# ---------------------------------------------------------
# DELETE PET
# ---------------------------------------------------------
@main_bp.route('/delete_pet/<int:pet_id>')
@login_required
def delete_pet(pet_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403

    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('main.view_pets'))


# ---------------------------------------------------------
# ADOPTION APPROVAL / REJECTION
# ---------------------------------------------------------
@main_bp.route('/approve_adoption/<int:adoption_id>')
@login_required
def approve_adoption(adoption_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403

    adoption = Adoption.query.get_or_404(adoption_id)
    adoption.status = "approved"

    pet = Pet.query.get(adoption.pet_id)
    pet.status = "adopted"

    db.session.commit()
    return redirect(url_for('main.view_adoptions'))


@main_bp.route('/reject_adoption/<int:adoption_id>')
@login_required
def reject_adoption(adoption_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403

    adoption = Adoption.query.get_or_404(adoption_id)
    adoption.status = "rejected"

    pet = Pet.query.get(adoption.pet_id)
    pet.status = "available"

    db.session.commit()
    return redirect(url_for('main.view_adoptions'))


# ---------------------------------------------------------
# PUBLIC PET LIST (SEARCH + FILTER + PAGINATION)
# ---------------------------------------------------------
@main_bp.route('/pets')
def index():
    search = request.args.get('search', "")
    species = request.args.get('species', "")

    pets = Pet.query

    if search:
        pets = pets.filter(Pet.name.like(f"%{search}%"))

    if species:
        pets = pets.filter_by(species=species)

    page = request.args.get('page', 1, type=int)
    pets = pets.paginate(page=page, per_page=6)

    return render_template('index.html', pets=pets)


# =======================================================
#                MEDICAL RECORDS SECTION
# =======================================================

# ADD MEDICAL RECORD
@main_bp.route('/add_medical/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_medical(pet_id):
    if current_user.role not in ['admin', 'vet']:
        return "Unauthorized", 403

    pet = Pet.query.get_or_404(pet_id)
    medicines = Medicine.query.all()  # fetch all medicines

    if request.method == 'POST':

        # ensure medicine selected
        medicine_id = request.form.get('medicine_id')
        if not medicine_id:
            flash("Please select a medicine.", "danger")
            return redirect(url_for('main.add_medical', pet_id=pet.id))

        medicine = Medicine.query.get(medicine_id)

        # ensure medicine exists
        if not medicine:
            flash("Selected medicine not found.", "danger")
            return redirect(url_for('main.add_medical', pet_id=pet.id))

        # stock check
        if medicine.stock <= 0:
            flash("This medicine is out of stock!", "danger")
            return redirect(url_for('main.add_medical', pet_id=pet.id))

        # decrease stock
        medicine.stock -= 1

        new_record = MedicalRecord(
            pet_id=pet.id,
            treatment=request.form['treatment'],
            diagnosis=request.form['diagnosis'],  
            visit_date=request.form['visit_date'],
            notes=request.form['notes'],
            medicine_id=medicine_id
        )

        db.session.add(new_record)
        db.session.commit()

        flash("Medical record added & stock updated!", "success")
        return redirect(url_for('main.view_medical', pet_id=pet.id))

    # ALWAYS return a response
    return render_template('add_medical.html', pet=pet, medicines=medicines)

@main_bp.route('/update_stock/<int:med_id>', methods=['POST'])
@login_required
def update_stock(med_id):
    if current_user.role != 'admin':
        flash("Unauthorized!", "danger")
        return redirect(url_for('main.view_medicines'))

    medicine = Medicine.query.get_or_404(med_id)

    new_stock = request.form.get("stock")

    try:
        medicine.stock = int(new_stock)
        db.session.commit()
        flash("Stock updated successfully!", "success")
    except:
        flash("Invalid stock value!", "danger")

    return redirect(url_for('main.view_medicines'))

# VIEW MEDICAL RECORDS
@main_bp.route('/view_medical/<int:pet_id>')
@login_required
def view_medical(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    medical_records = MedicalRecord.query.filter_by(pet_id=pet_id).all()

    # Everyone can view (admin, vet, adopter)
    return render_template('view_medical.html', 
                           pet=pet, 
                           medical_records=medical_records)


# EDIT MEDICAL RECORD
@main_bp.route('/edit_medical/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_medical(record_id):
    if current_user.role not in ['admin', 'vet']:
        return "Unauthorized", 403

    record = MedicalRecord.query.get_or_404(record_id)

    if request.method == 'POST':
        record.treatment = request.form['treatment']
        record.diagnosis = request.form['diagnosis']
        record.medication = request.form['medication']
        record.visit_date = request.form['visit_date']
        record.notes = request.form['notes']

        db.session.commit()
        flash("Medical record updated!", "success")
        return redirect(url_for('main.view_medical', pet_id=record.pet_id))

    return render_template('edit_medical.html', record=record)


# DELETE MEDICAL RECORD
@main_bp.route('/delete_medical/<int:record_id>')
@login_required
def delete_medical(record_id):
    if current_user.role not in ['admin', 'vet']:
        return "Unauthorized", 403

    record = MedicalRecord.query.get_or_404(record_id)
    pet_id = record.pet_id

    db.session.delete(record)
    db.session.commit()

    flash("Medical record deleted!", "danger")
    return redirect(url_for('main.view_medical', pet_id=pet_id))


# =======================================================
#                     MEDICINES
# =======================================================

@main_bp.route('/medicines')
@login_required
def view_medicines():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    medicines = Medicine.query.all()
    return render_template('view_medicines.html', medicines=medicines)


@main_bp.route('/add_medicine', methods=['GET', 'POST'])
@login_required
def add_medicine():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        med = Medicine(
            name=request.form['name'],
            stock=request.form['stock'],
            description=request.form['description']
        )
        db.session.add(med)
        db.session.commit()

        flash("Medicine added!", "success")
        return redirect(url_for('main.view_medicines'))

    return render_template('add_medicine.html')
