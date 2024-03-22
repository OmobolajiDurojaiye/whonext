from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
import random
from pkg import app
from pkg.models import db, Participants
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta, timezone

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pwd'] 
        
        user = Participants.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                session['username'] = username
                flash('Login successful!')
                return redirect(url_for('index'))
            else:
                flash('Incorrect username or password. Please try again.', 'error')
        else:
            flash('Incorrect username or password. Please try again.', 'error')
    
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pwd']
        
        # Check if the username already exists in the database
        existing_participant = Participants.query.filter_by(username=username).first()
        if existing_participant:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('signup'))  # Redirect back to the signup page
        
        hashed_password = generate_password_hash(password)
        
        new_participant = Participants(username=username, password=hashed_password)
        
        db.session.add(new_participant)
        db.session.commit()
        
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')



@app.route('/generate_number', methods=['GET'])
def generate_number():
    numbers = list(range(1, 11))
    if 'picked_numbers' not in session:
        session['picked_numbers'] = []
    picked_numbers = session['picked_numbers']

    # Get the current user
    current_user = Participants.query.filter_by(username=session['username']).first()

    # Check if the user has won in the past months
    if current_user.last_winning_date:
        last_winning_datetime = datetime.combine(current_user.last_winning_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last_winning_datetime < timedelta(days=30):
            return "You can't play, you have already won this month!"
    
    remaining_numbers = [num for num in numbers if num not in picked_numbers]
    
    if len(remaining_numbers) == 0:
        return "All numbers have been picked!"

    random_number = random.choice(remaining_numbers)
    picked_numbers.append(random_number)
    session['picked_numbers'] = picked_numbers 

    # Update last winning date if the user wins
    if random_number == 1:
        current_user.last_winning_date = datetime.now(timezone.utc).date()
        db.session.commit()

    return str(random_number)




@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))