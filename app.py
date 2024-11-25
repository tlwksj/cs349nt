from flask import Flask, request, url_for, redirect, render_template, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.fields.numeric import FloatField
from wtforms.validators import NumberRange, Email, DataRequired

#StringField, Email, NumberRange, Length
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

user_credentials = {
    'test@example.com': 'password'
}
user_meals = {}
user_goals = {}

# this is to assign the variables of the email and password
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# This assigns the variables of the food names, their quantities and the type of meal they coordinate
class MealLogForm(FlaskForm):
    food_name = StringField('Food Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ])
    #we submit the log mean of the characteristics towards our options
    submit = SubmitField('Log Meal')

#Below is our API Routes
#login endpoint for the API
@app.route('/api/login', methods=['POST'])
def login_api():
    email = request.form.get('email')
    password = request.form.get('password')
    #check to see if the email and password are provided
    if not email or not password:
        #return an error message indicating that this is a bad request based on the information provided
        return {'status': 'error', 'message': 'Email and password are required'}, 400
    #if the email and password are valid then we return a successful message.
    if email == 'test@example.com' and password == 'password':
        return {'status': 'success', 'user_id': 1}, 200
    else:
        #otherwise return an unauthorized message that the information that was inputted is invalid
        return {'status': 'error', 'message': 'Invalid credentials'}, 401

#endpoint for the API on getting the list of foods
@app.route('/api/foods')
def get_foods():
    #list of food options
    return [
        {'name': 'Rice', 'id': 1},
        {'name': 'Banana', 'id': 2},
        {'name': 'Chicken Breast', 'id': 3},
        {'name': 'Broccoli', 'id': 4}
    ]

#endpoint for the API of logging the users meal
@app.route('/api/log_meal', methods=['POST'])
def log_meal_api():
    user = session.get('user')
    #error check for invalid user
    if not user:
        return {'status': 'error', 'message': 'User does not exist'}, 401
    # Simulate logging a meal
    food_name = request.form.get('food_name')
    quantity = request.form.get('quantity')
    meal_type = request.form.get('meal_type')
    #error check for no food name, quantity and meal type
    if not (food_name and quantity and meal_type):
        return {'status': 'error', 'message': 'Food name, quantity and meal type are required'}, 400
    if user not in user_meals:
        user_meals[user] = []
    user_meals[user].append({'food_name': food_name, 'quantity': quantity, 'meal_type': meal_type})
    return {'status': 'success', 'message': f'Logged {quantity} {food_name} for {meal_type}'}

# running the process of each task including login, interface, logging meal and progress
# this validates the process of the user logging into their account
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    #obtains the information from the email and password
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # checks the users credentials and password and stores it to that users session
        if email in user_credentials and user_credentials[email] == password:
            session['user'] = email  # Store user session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else: # error message or invalid email or password
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


#  This is how the dashboard would be displayed once the user is successfully logged in.
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

# this is the process of logging the users meal
@app.route('/log_meal', methods=['GET', 'POST'])
def log_meal():
    if 'user' not in session:
        flash('Please log in to log meals.', 'warning')
        return redirect(url_for('login'))
    form = MealLogForm()
    if form.validate_on_submit():
        user = session['user']
        if user not in user_meals:
            user_meals[user] = []
        user_meals[user].append({'food_name': form.food_name.data, 'quantity': form.quantity.data, 'meal_type': form.meal_type.data})
        # Simulate logging the meal
        flash(f"Logged {form.quantity.data} {form.food_name.data} for {form.meal_type.data}.", "success")
        return redirect(url_for('dashboard'))
    return render_template('log_meal.html', form=form)

# this will display the progress the user has made throughout their weekly training
@app.route('/progress')
def progress():
    if 'user' not in session:
        flash('Please log in to access the progress page.', 'warning')
        return redirect(url_for('login'))
    user = session['user']
    # this gets all information towards the users progress
    meals = user_meals.get(user, [])
    goals = user_goals.get(user, {})
    target_weight = goals.get('target_weight')
    target_weeks = goals.get('weeks')
    return render_template('progress.html', meals=meals, target_weight=target_weight, target_weeks=target_weeks)

# This is the process for obtaining the admin management of the tracking app.
@app.route('/admin')
def admin_management():
    # gets the admins logged in data. the plan is to fetch it from a database
    users = [
        {'id': 1, 'name': 'User A', 'email': 'usera@example.com'},
        {'id': 2, 'name': 'User B', 'email': 'userb@example.com'}
    ]
    return render_template('admin.html', users=users)

# makes the variables for the goals section
class GoalForm(FlaskForm):
    target_weight = FloatField('Target Weight', validators=[DataRequired(), NumberRange(min=50)])
    weeks = IntegerField('weeks to achieve goal', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('set goal')
# New Goals Route
@app.route('/goals', methods=['GET', 'POST'])
def goals():
    if 'user' not in session:
        flash('Please log in to set your goals.', 'warning')
        return redirect(url_for('login'))

    form = GoalForm()
    # allow the user to submit their new goals
    if form.validate_on_submit():
        user = session['user']
        target_weight = form.target_weight.data
        weeks = form.weeks.data
        # Stores the goals into the system
        user_goals[user] = {'target_weight': target_weight, 'weeks': weeks}
        flash(f"Goal set! Target Weight: {target_weight} lbs in {weeks} weeks.", "success")
        return redirect(url_for('dashboard'))

    return render_template('goals.html', form=form)

# API to retrieve user's goals
@app.route('/api/goals', methods=['GET'])
def get_goals_api():
    user = session.get('user')
    if not user:
        return {'status': 'error', 'message': 'User not logged in'}, 401

    goals = user_goals.get(user, None)
    if goals:
        return {'status': 'success', 'goals': goals}, 200
    else:
        return {'status': 'error', 'message': 'No goals set'}, 404

#allows the user to log out the system
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
