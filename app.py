from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, date, timezone
import json
from flask_migrate import Migrate
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitroom_fresh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    profile_picture = db.Column(db.String(200))
    bio = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __getattr__(self, name):
        """Handle missing attributes gracefully"""
        if name == 'is_admin':
            # If is_admin column doesn't exist, return True for admin@fitroom.com
            return self.email == 'admin@fitroom.com'
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
# Association table for many-to-many relationship between Workout and Exercise
workout_exercises = db.Table('workout_exercises',
    db.Column('workout_id', db.Integer, db.ForeignKey('workout.id'), primary_key=True),
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'), primary_key=True)
)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)  # in minutes
    difficulty = db.Column(db.String(20))
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Many-to-many relationship
    exercises = db.relationship('Exercise', secondary=workout_exercises, backref=db.backref('workouts', lazy='dynamic'))
    
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String(50))
    equipment = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    video_url = db.Column(db.String(200))
    instructions = db.Column(db.Text)  # JSON-encoded list of steps
    key_points = db.Column(db.Text)    # JSON-encoded list of points

    @property
    def instructions_list(self):
        try:
            return json.loads(self.instructions) if self.instructions else []
        except Exception:
            return []

    @instructions_list.setter
    def instructions_list(self, value):
        self.instructions = json.dumps(value)

    @property
    def key_points_list(self):
        try:
            return json.loads(self.key_points) if self.key_points else []
        except Exception:
            return []

    @key_points_list.setter
    def key_points_list(self, value):
        self.key_points = json.dumps(value)

# --- Diet Plan Models ---
class DietPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    goal = db.Column(db.String(100))  # e.g., Weight Loss, Muscle Gain
    image_url = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_public = db.Column(db.Boolean, default=True)
    meals = db.relationship('Meal', backref='diet_plan', cascade='all, delete-orphan')
    followers = db.relationship('User', secondary='user_diet_plan', backref='followed_diet_plans')

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plan.id'))
    name = db.Column(db.String(100), nullable=False)
    meal_type = db.Column(db.String(50))  # Breakfast, Lunch, etc.
    foods = db.Column(db.Text)  # JSON-encoded list of foods/ingredients
    calories = db.Column(db.Integer)
    notes = db.Column(db.Text)

class UserDietLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plan.id'))
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(50))
    foods = db.Column(db.Text)  # JSON-encoded list
    calories = db.Column(db.Integer)
    notes = db.Column(db.Text)
    # Relationship to easily access diet plan information
    diet_plan = db.relationship('DietPlan', backref='user_logs')

# Association table for users following diet plans
user_diet_plan = db.Table('user_diet_plan',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('diet_plan_id', db.Integer, db.ForeignKey('diet_plan.id'), primary_key=True)
)

# --- Workout Plan Models ---
class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    goal = db.Column(db.String(100))
    image_url = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_public = db.Column(db.Boolean, default=True)
    duration_days = db.Column(db.Integer)  # e.g., 30 for a 30-day plan
    days = db.relationship('WorkoutPlanDay', backref='workout_plan', cascade='all, delete-orphan')
    followers = db.relationship('User', secondary='user_workout_plan', backref='followed_workout_plans')

class WorkoutPlanDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'))
    day_number = db.Column(db.Integer)  # 1-based
    workouts = db.Column(db.Text)  # JSON-encoded list of workout IDs for this day
    notes = db.Column(db.Text)

class UserWorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'))
    date = db.Column(db.Date, nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    # Relationship to easily access workout information
    workout = db.relationship('Workout', backref='user_logs')

# Association table for users following workout plans
user_workout_plan = db.Table('user_workout_plan',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('workout_plan_id', db.Integer, db.ForeignKey('workout_plan.id'), primary_key=True)
)

# Model to track when users start plans
class PlanStartDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # 'diet' or 'workout'
    plan_id = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'plan_type', 'plan_id', name='unique_user_plan_start'),
    )

class UserDietDayLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plan.id'))
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        # If there's a database error (like missing column), return None
        print(f"Error loading user {user_id}: {e}")
        return None

def check_admin_access():
    """Helper function to check admin access"""
    try:
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.')
            return False
    except:
        # If is_admin column doesn't exist, allow access for admin@fitroom.com
        if current_user.email != 'admin@fitroom.com':
            flash('Access denied. Admin privileges required.')
            return False
    return True

# Routes
@app.route('/')
def index():
    """Home page - landing page with hero section"""
    return render_template('index.html')

@app.route('/workouts')
@login_required
def workouts():
    """Workouts page - browse and search workouts"""
    # Allow admins to view the workouts list, but restrict participation in the template
    workouts = Workout.query.all()
    return render_template('workouts.html', workouts=workouts)

@app.route('/workout/<int:workout_id>')
@login_required
def workout_detail(workout_id):
    """Individual workout detail page"""
    # Allow admins to view workout details, but restrict participation in the template
    workout = Workout.query.get_or_404(workout_id)
    return render_template('workout_detail.html', workout=workout)

@app.route('/exercises')
@login_required
def exercises():
    """Exercises library page"""
    exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=exercises)

@app.route('/exercise/<int:exercise_id>')
@login_required
def exercise_detail(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    return render_template('exercise_detail.html', exercise=exercise)

@app.route('/profile')
@login_required
def profile():
    # Check if user is admin and redirect to admin profile
    try:
        if current_user.is_admin or current_user.email == 'admin@fitroom.com':
            return redirect(url_for('admin_profile'))
    except:
        # If is_admin column doesn't exist, check by email
        if current_user.email == 'admin@fitroom.com':
            return redirect(url_for('admin_profile'))

    # Get all completed workout logs for this user
    logs = UserWorkoutLog.query.filter_by(user_id=current_user.id, completed=True).order_by(UserWorkoutLog.date.desc()).all()
    total_workouts = len(logs)
    # Calculate total hours (sum durations from related Workout)
    total_minutes = sum(log.workout.duration for log in logs if log.workout and log.workout.duration)
    total_hours = total_minutes / 60

    # Recent workouts (show last 3)
    recent_logs = logs[:3]
    recent_workouts = [log.workout for log in recent_logs if log.workout]

    # Weekly progress (last 7 days, group by weekday)
    week = defaultdict(lambda: {'minutes': 0, 'count': 0})
    today = date.today()
    for log in logs:
        if (today - log.date).days < 7:
            weekday = log.date.strftime('%a')
            if log.workout and log.workout.duration:
                week[weekday]['minutes'] += log.workout.duration
                week[weekday]['count'] += 1
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly_progress = [week[day] for day in week_days]

    return render_template('profile.html',
        total_workouts=total_workouts,
        total_hours=total_hours,
        recent_workouts=recent_workouts,
        weekly_progress=weekly_progress
    )

@app.route('/admin/profile')
@login_required
def admin_profile():
    """Admin profile page"""
    if not check_admin_access():
        return redirect(url_for('index'))
    
    # Get admin statistics
    total_workouts = Workout.query.count()
    total_exercises = Exercise.query.count()
    total_users = User.query.count()
    admin_created_workouts = Workout.query.filter_by(created_by=current_user.id).count()
    
    # Get recent activities
    recent_workouts = Workout.query.order_by(Workout.id.desc()).limit(5).all()
    recent_exercises = Exercise.query.order_by(Exercise.id.desc()).limit(5).all()
    
    return render_template('admin/profile.html',
                         total_workouts=total_workouts,
                         total_exercises=total_exercises,
                         total_users=total_users,
                         admin_created_workouts=admin_created_workouts,
                         recent_workouts=recent_workouts,
                         recent_exercises=recent_exercises)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        login_type = request.form.get('login_type')
        
        user = User.query.filter_by(email=email).first()
        
        if user and password and check_password_hash(user.password_hash, password):
            # Check if login type matches user type
            is_admin_user = user.is_admin or user.email == 'admin@fitroom.com'
            
            if login_type == 'admin' and not is_admin_user:
                flash('Access denied. Admin privileges required.')
                return render_template('login.html')
            elif login_type == 'user' and is_admin_user:
                flash('Please select Admin login type for admin accounts.')
                return render_template('login.html')
            
            login_user(user)
            flash(f'Welcome back, {user.username}!')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'user')  # Default to user
        terms_accepted = request.form.get('terms')
        if not terms_accepted:
            flash('You must agree to the Terms of Service and Privacy Policy.')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        if password:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            # Set admin status based on user type
            if user_type == 'admin':
                user.is_admin = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account created successfully as {user_type}!')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        bio = request.form.get('bio')
        
        # Check if username is already taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken. Please choose another one.')
            return redirect(url_for('profile'))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already taken. Please choose another one.')
            return redirect(url_for('profile'))
        
        # Update user profile
        current_user.username = username
        current_user.email = email
        current_user.bio = bio
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(app.root_path, 'static', 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # Save the file
                filename = f"profile_{current_user.id}_{file.filename}"
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Update profile picture path
                current_user.profile_picture = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    
    return redirect(url_for('profile'))

# Admin routes
@app.route('/admin/users/<int:user_id>/reset_password', methods=['POST'])
@login_required
def admin_reset_password(user_id):
    """Admin: Reset a user's password to a default value"""
    if not check_admin_access():
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    # Set a default password, e.g., 'newpassword123'
    new_password = 'newpassword123'
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash(f"Password for user '{user.username}' has been reset to '{new_password}'.")
    return redirect(url_for('admin_users'))
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not check_admin_access():
        return redirect(url_for('index'))
    
    workouts_count = Workout.query.count()
    exercises_count = Exercise.query.count()
    users_count = User.query.count()

    # Platform Overview
    workout_categories = [c[0] for c in Workout.query.with_entities(Workout.category).distinct() if c[0]]
    exercise_types = [e[0] for e in Exercise.query.with_entities(Exercise.equipment).distinct() if e[0]]
    diet_plan_goals = [g[0] for g in DietPlan.query.with_entities(DietPlan.goal).distinct() if g[0]]
    workout_plan_names = [p[0] for p in WorkoutPlan.query.with_entities(WorkoutPlan.name).distinct() if p[0]]

    # Recent Activity - Unified list of last 3 activities
    recent_activities = []
    
    # Get latest workouts
    latest_workouts = Workout.query.order_by(Workout.id.desc()).limit(3).all()
    for workout in latest_workouts:
        recent_activities.append({
            'type': 'workout',
            'title': 'New Workout Added',
            'description': f'{workout.name} (ID: {workout.id})',
            'icon': 'fas fa-plus',
            'color': 'success'
        })
    
    # Get latest users
    latest_users = User.query.order_by(User.id.desc()).limit(3).all()
    for user in latest_users:
        recent_activities.append({
            'type': 'user',
            'title': 'New User Registration',
            'description': f'{user.username} ({user.email})',
            'icon': 'fas fa-user-plus',
            'color': 'info'
        })
    
    # Get latest exercises
    latest_exercises = Exercise.query.order_by(Exercise.id.desc()).limit(3).all()
    for exercise in latest_exercises:
        recent_activities.append({
            'type': 'exercise',
            'title': 'Exercise Updated',
            'description': f'{exercise.name} (ID: {exercise.id})',
            'icon': 'fas fa-edit',
            'color': 'primary'
        })
    
    # Sort by ID (most recent first) and take only the last 3
    recent_activities.sort(key=lambda x: x['description'].split('ID: ')[-1].rstrip(')'), reverse=True)
    recent_activities = recent_activities[:3]

    return render_template('admin/dashboard.html', 
                         workouts_count=workouts_count,
                         exercises_count=exercises_count,
                         users_count=users_count,
                         workout_categories=workout_categories,
                         exercise_types=exercise_types,
                         diet_plan_goals=diet_plan_goals,
                         workout_plan_names=workout_plan_names,
                         recent_activities=recent_activities)

@app.route('/admin/workouts')
@login_required
def admin_workouts():
    """Admin workouts management"""
    if not check_admin_access():
        return redirect(url_for('index'))
    
    workouts = Workout.query.all()
    return render_template('admin/workouts.html', workouts=workouts)

@app.route('/admin/workouts/add', methods=['GET', 'POST'])
@login_required
def admin_add_workout():
    """Add new workout"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        duration = request.form.get('duration')
        difficulty = request.form.get('difficulty')
        category = request.form.get('category')
        image_url = request.form.get('image_url')
        
        if name and description and duration:
            workout = Workout(
                name=name,
                description=description,
                duration=int(duration) if duration else 30,
                difficulty=difficulty,
                category=category,
                image_url=image_url,
                created_by=current_user.id
            )
            db.session.add(workout)
            db.session.commit()
            flash('Workout added successfully!')
            return redirect(url_for('admin_workouts'))
        else:
            flash('Please fill all required fields.')
    
    return render_template('admin/add_workout.html')

@app.route('/admin/exercises')
@login_required
def admin_exercises():
    """Admin exercises management"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    exercises = Exercise.query.all()
    return render_template('admin/exercises.html', exercises=exercises)

@app.route('/admin/exercises/add', methods=['GET', 'POST'])
@login_required
def admin_add_exercise():
    """Add new exercise"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        muscle_group = request.form.get('muscle_group')
        equipment = request.form.get('equipment')
        image_url = request.form.get('image_url')
        video_url = request.form.get('video_url')
        
        if name and description and muscle_group:
            exercise = Exercise(
                name=name,
                description=description,
                muscle_group=muscle_group,
                equipment=equipment,
                image_url=image_url,
                video_url=video_url
            )
            db.session.add(exercise)
            db.session.commit()
            flash('Exercise added successfully!')
            return redirect(url_for('admin_exercises'))
        else:
            flash('Please fill all required fields.')
    
    return render_template('admin/add_exercise.html')

@app.route('/admin/workouts/<int:workout_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_workout(workout_id):
    """Edit workout and manage exercises"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    workout = Workout.query.get_or_404(workout_id)
    all_exercises = Exercise.query.all()
    
    if request.method == 'POST':
        # Remove exercise if requested
        remove_exercise_id = request.form.get('remove_exercise_id')
        if remove_exercise_id:
            exercise_to_remove = Exercise.query.get(int(remove_exercise_id))
            if exercise_to_remove in workout.exercises:
                workout.exercises.remove(exercise_to_remove)
                db.session.commit()
                flash(f'Exercise "{exercise_to_remove.name}" removed from workout!')
                return redirect(url_for('admin_edit_workout', workout_id=workout.id))

        # Update workout details
        workout.name = request.form.get('name')
        workout.description = request.form.get('description')
        duration_value = request.form.get('duration')
        workout.duration = int(duration_value) if duration_value else 30
        workout.difficulty = request.form.get('difficulty')
        workout.category = request.form.get('category')
        workout.image_url = request.form.get('image_url')

        # Update exercises: clear and repopulate from multi-select
        selected_exercise_ids = request.form.getlist('add_exercises')
        workout.exercises = [Exercise.query.get(int(ex_id)) for ex_id in selected_exercise_ids if Exercise.query.get(int(ex_id))]
        
        db.session.commit()
        flash('Workout updated successfully!')
        return redirect(url_for('admin_workouts'))
    
    return render_template('admin/edit_workout.html', workout=workout, all_exercises=all_exercises)

@app.route('/admin/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_exercise(exercise_id):
    """Edit exercise"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'POST':
        exercise.name = request.form.get('name')
        exercise.description = request.form.get('description')
        exercise.muscle_group = request.form.get('muscle_group')
        exercise.equipment = request.form.get('equipment')
        exercise.image_url = request.form.get('image_url')
        exercise.video_url = request.form.get('video_url')
        # Save instructions and key points as JSON lists
        instructions_json = request.form.get('instructions_json')
        key_points_json = request.form.get('key_points_json')
        if instructions_json is not None:
            try:
                exercise.instructions_list = json.loads(instructions_json)
            except Exception:
                exercise.instructions_list = []
        if key_points_json is not None:
            try:
                exercise.key_points_list = json.loads(key_points_json)
            except Exception:
                exercise.key_points_list = []
        db.session.commit()
        flash('Exercise updated successfully!')
        return redirect(url_for('admin_exercises'))
    
    return render_template('admin/edit_exercise.html', exercise=exercise)

@app.route('/admin/workouts/<int:workout_id>/delete', methods=['POST'])
@login_required
def admin_delete_workout(workout_id):
    """Delete workout"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    flash('Workout deleted successfully!')
    return redirect(url_for('admin_workouts'))

@app.route('/admin/exercises/<int:exercise_id>/delete', methods=['POST'])
@login_required
def admin_delete_exercise(exercise_id):
    """Delete exercise"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    flash('Exercise deleted successfully!')
    return redirect(url_for('admin_exercises'))

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin users management - view all users and credentials"""
    if not check_admin_access():
        return redirect(url_for('index'))
    
    users = User.query.all()
    # Calculate workout counts for each user
    user_workout_counts = {}
    for user in users:
        user_workout_counts[user.id] = Workout.query.filter_by(created_by=user.id).count()
    
    return render_template('admin/users.html', users=users, user_workout_counts=user_workout_counts)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete user"""
    if not check_admin_access():
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account!')
        return redirect(url_for('admin_users'))
    
    # Delete user's workouts first
    Workout.query.filter_by(created_by=user.id).delete()
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.username}" deleted successfully!')
    return redirect(url_for('admin_users'))

@app.route('/api/workouts')
def api_workouts():
    """API endpoint for workouts"""
    workouts = Workout.query.all()
    return jsonify([{
        'id': w.id,
        'name': w.name,
        'description': w.description,
        'duration': w.duration,
        'difficulty': w.difficulty,
        'category': w.category,
        'image_url': w.image_url
    } for w in workouts])

@app.route('/api/exercises')
def api_exercises():
    """API endpoint for exercises"""
    exercises = Exercise.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'description': e.description,
        'muscle_group': e.muscle_group,
        'equipment': e.equipment,
        'image_url': e.image_url
    } for e in exercises])

@app.route('/api/log_workout', methods=['POST'])
@login_required
def api_log_workout():
    """Log a completed workout for the current user"""
    if current_user.is_admin or current_user.email == 'admin@fitroom.com':
        return jsonify({'error': 'Admins cannot log workouts.'}), 403
    data = request.get_json()
    workout_id = data.get('workout_id')
    duration = data.get('duration')  # Actual duration in minutes
    
    if not workout_id:
        return jsonify({'error': 'Workout ID is required'}), 400
    
    # Create a workout completion record
    # For now, we'll just update the workout's created_by to track user completions
    # In a real app, you'd have a separate WorkoutCompletion model
    workout = Workout.query.get(workout_id)
    if workout:
        # Update the workout to show it was completed by this user
        workout.created_by = current_user.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Workout "{workout.name}" logged successfully!'
        })
    
    return jsonify({'error': 'Workout not found'}), 404

@app.route('/admin/workouts/<int:workout_id>/remove_exercise/<int:exercise_id>', methods=['POST'])
@login_required
def admin_remove_exercise_from_workout(workout_id, exercise_id):
    """Remove an exercise from a workout (dedicated route)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    workout = Workout.query.get_or_404(workout_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    if exercise in workout.exercises:
        workout.exercises.remove(exercise)
        db.session.commit()
        flash(f'Exercise "{exercise.name}" removed from workout!')
    return redirect(url_for('admin_edit_workout', workout_id=workout.id))

# Admin Diet Plan Management Routes
@app.route('/admin/diet_plans')
@login_required
def admin_diet_plans():
    """Admin view to manage all diet plans"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    plans = DietPlan.query.all()
    for plan in plans:
        plan.creator = User.query.get(plan.created_by)
        plan.meals_count = Meal.query.filter_by(diet_plan_id=plan.id).count()
    
    return render_template('admin/diet_plans.html', plans=plans)

@app.route('/admin/diet_plans/add', methods=['GET', 'POST'])
@login_required
def admin_add_diet_plan():
    """Admin route to add new diet plan"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        goal = request.form.get('goal')
        description = request.form.get('description')
        is_public = bool(request.form.get('is_public'))
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename:
            image_path = os.path.join('static', 'images', image_file.filename)
            image_file.save(image_path)
            image_url = '/' + image_path.replace('\\', '/')
        
        plan = DietPlan(
            name=name,
            goal=goal,
            description=description,
            image_url=image_url,
            created_by=current_user.id,
            is_public=is_public
        )
        db.session.add(plan)
        db.session.flush()
        
        # Parse meals from form
        meal_num = 1
        while True:
            meal_name = request.form.get(f'meal_name_{meal_num}')
            if not meal_name:
                break
            meal_type = request.form.get(f'meal_type_{meal_num}')
            meal_calories = request.form.get(f'meal_calories_{meal_num}')
            meal_foods = request.form.get(f'meal_foods_{meal_num}')
            meal_notes = request.form.get(f'meal_notes_{meal_num}')
            meal = Meal(
                diet_plan_id=plan.id,
                name=meal_name,
                meal_type=meal_type,
                calories=int(meal_calories) if meal_calories else None,
                foods=meal_foods,
                notes=meal_notes
            )
            db.session.add(meal)
            meal_num += 1
        
        db.session.commit()
        flash('Diet plan created successfully!', 'success')
        return redirect(url_for('admin_diet_plans'))
    
    return render_template('admin/add_diet_plan.html')

@app.route('/admin/diet_plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_diet_plan(plan_id):
    """Admin route to edit diet plan"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    plan = DietPlan.query.get_or_404(plan_id)
    meals = Meal.query.filter_by(diet_plan_id=plan.id).all()
    
    if request.method == 'POST':
        plan.name = request.form.get('name')
        plan.goal = request.form.get('goal')
        plan.description = request.form.get('description')
        plan.is_public = bool(request.form.get('is_public'))
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            image_path = os.path.join('static', 'images', image_file.filename)
            image_file.save(image_path)
            plan.image_url = '/' + image_path.replace('\\', '/')
        
        # Update meals
        for meal in meals:
            meal.name = request.form.get(f'meal_name_{meal.id}')
            meal.meal_type = request.form.get(f'meal_type_{meal.id}')
            meal.calories = int(request.form.get(f'meal_calories_{meal.id}')) if request.form.get(f'meal_calories_{meal.id}') else None
            meal.foods = request.form.get(f'meal_foods_{meal.id}')
            meal.notes = request.form.get(f'meal_notes_{meal.id}')
        
        db.session.commit()
        flash('Diet plan updated successfully!', 'success')
        return redirect(url_for('admin_diet_plans'))
    
    return render_template('admin/edit_diet_plan.html', plan=plan, meals=meals)

@app.route('/admin/diet_plans/<int:plan_id>/delete', methods=['POST'])
@login_required
def admin_delete_diet_plan(plan_id):
    """Admin route to delete diet plan"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    plan = DietPlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    flash('Diet plan deleted successfully!', 'success')
    return redirect(url_for('admin_diet_plans'))

# Admin Workout Plan Management Routes
@app.route('/admin/workout_plans')
@login_required
def admin_workout_plans():
    """Admin view to manage all workout plans"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    plans = WorkoutPlan.query.all()
    for plan in plans:
        plan.creator = User.query.get(plan.created_by)
        plan.days_count = WorkoutPlanDay.query.filter_by(workout_plan_id=plan.id).count()
    
    return render_template('admin/workout_plans.html', plans=plans)

@app.route('/admin/workout_plans/add', methods=['GET', 'POST'])
@login_required
def admin_add_workout_plan():
    """Admin route to add new workout plan"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        goal = request.form.get('goal')
        description = request.form.get('description')
        duration_days = request.form.get('duration_days')
        is_public = bool(request.form.get('is_public'))
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename:
            image_path = os.path.join('static', 'images', image_file.filename)
            image_file.save(image_path)
            image_url = '/' + image_path.replace('\\', '/')
        
        plan = WorkoutPlan(
            name=name,
            goal=goal,
            description=description,
            image_url=image_url,
            created_by=current_user.id,
            is_public=is_public,
            duration_days=int(duration_days) if duration_days else None
        )
        db.session.add(plan)
        db.session.flush()
        
        # Parse days from form
        day_num = 1
        while True:
            day_workouts = request.form.get(f'day_workouts_{day_num}')
            if not day_workouts:
                break
            day_notes = request.form.get(f'day_notes_{day_num}')
            day = WorkoutPlanDay(
                workout_plan_id=plan.id,
                day_number=day_num,
                workouts=day_workouts,
                notes=day_notes
            )
            db.session.add(day)
            day_num += 1
        
        db.session.commit()
        flash('Workout plan created successfully!', 'success')
        return redirect(url_for('admin_workout_plans'))
    
    return render_template('admin/add_workout_plan.html')

@app.route('/admin/workout_plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_workout_plan(plan_id):
    """Admin route to edit workout plan"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    plan = WorkoutPlan.query.get_or_404(plan_id)
    days = WorkoutPlanDay.query.filter_by(workout_plan_id=plan.id).all()
    
    if request.method == 'POST':
        plan.name = request.form.get('name')
        plan.goal = request.form.get('goal')
        plan.description = request.form.get('description')
        plan.duration_days = int(request.form.get('duration_days')) if request.form.get('duration_days') else None
        plan.is_public = bool(request.form.get('is_public'))
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            image_path = os.path.join('static', 'images', image_file.filename)
            image_file.save(image_path)
            plan.image_url = '/' + image_path.replace('\\', '/')
        
        # Update days
        for day in days:
            day.workouts = request.form.get(f'day_workouts_{day.id}')
            day.notes = request.form.get(f'day_notes_{day.id}')
        
        db.session.commit()
        flash('Workout plan updated successfully!', 'success')
        return redirect(url_for('admin_workout_plans'))
    
    return render_template('admin/edit_workout_plan.html', plan=plan, days=days)

@app.route('/admin/workout_plans/<int:plan_id>/delete', methods=['POST'])
@login_required
def admin_delete_workout_plan(plan_id):
    """Admin route to delete workout plan"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
    
    plan = WorkoutPlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    flash('Workout plan deleted successfully!', 'success')
    return redirect(url_for('admin_workout_plans'))

@app.route('/diet_plans/add', methods=['GET', 'POST'])
@login_required
def add_diet_plan():
    if request.method == 'POST':
        name = request.form.get('name')
        goal = request.form.get('goal')
        description = request.form.get('description')
        is_public = bool(request.form.get('is_public'))
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename:
            image_path = os.path.join('static', 'images', image_file.filename)
            image_file.save(image_path)
            image_url = '/' + image_path.replace('\\', '/')
        plan = DietPlan(
            name=name,
            goal=goal,
            description=description,
            image_url=image_url,
            created_by=current_user.id,
            is_public=is_public
        )
        db.session.add(plan)
        db.session.flush()  # Get plan.id before committing
        # Parse meals from form
        meal_num = 1
        while True:
            meal_name = request.form.get(f'meal_name_{meal_num}')
            if not meal_name:
                break
            meal_type = request.form.get(f'meal_type_{meal_num}')
            meal_calories = request.form.get(f'meal_calories_{meal_num}')
            meal_foods = request.form.get(f'meal_foods_{meal_num}')
            meal_notes = request.form.get(f'meal_notes_{meal_num}')
            meal = Meal(
                diet_plan_id=plan.id,
                name=meal_name,
                meal_type=meal_type,
                calories=int(meal_calories) if meal_calories else None,
                foods=meal_foods,
                notes=meal_notes
            )
            db.session.add(meal)
            meal_num += 1
        db.session.commit()
        flash('Diet plan created successfully!', 'success')
        return redirect(url_for('view_diet_plan', plan_id=plan.id))
    return render_template('add_diet_plan.html')

@app.route('/diet_plans/<int:plan_id>')
@login_required
def view_diet_plan(plan_id):
    plan = DietPlan.query.get_or_404(plan_id)
    meals = Meal.query.filter_by(diet_plan_id=plan.id).all()
    creator = User.query.get(plan.created_by)
    today = date.today()  # Ensure 'today' is always defined
    
    # Check if user is following this plan and calculate current day
    current_day = None
    start_date = None
    is_following = plan.id in [p.id for p in current_user.followed_diet_plans]
    meal_types = sorted(set(meal.meal_type for meal in meals))
    meal_completion = {meal_type: False for meal_type in meal_types}
    diet_day_completed = False
    
    if is_following:
        # Get the start date for this plan
        start_date_record = PlanStartDate.query.filter_by(
            user_id=current_user.id,
            plan_type='diet',
            plan_id=plan_id
        ).first()
        
        if start_date_record:
            start_date = start_date_record.started_at.date()
            # Calculate days since starting the plan
            today = date.today()
            days_since_start = (today - start_date).days
            # For diet plans, we'll use 30 days as default duration
            plan_duration = 30
            current_day = (days_since_start % plan_duration) + 1
            if current_day > plan_duration:
                current_day = plan_duration
            # Check meal completion for today
            todays_logs = UserDietLog.query.filter_by(
                user_id=current_user.id,
                diet_plan_id=plan_id,
                date=today
            ).all()
            logged_meal_types = {log.meal_type for log in todays_logs}
            for meal_type in meal_types:
                if meal_type in logged_meal_types:
                    meal_completion[meal_type] = True
            diet_day_completed = all(meal_completion.values())
            if diet_day_completed:
                mark_diet_day_completed(current_user.id, plan.id, today)
    
    # Check if day log exists for badge
    day_log = UserDietDayLog.query.filter_by(user_id=current_user.id, diet_plan_id=plan.id, date=today, completed=True).first()
    
    return render_template('diet_plan_detail.html', 
                         plan=plan, 
                         meals=meals, 
                         creator=creator,
                         current_day=current_day,
                         start_date=start_date,
                         is_following=is_following,
                         meal_types=meal_types,
                         meal_completion=meal_completion,
                         diet_day_completed=diet_day_completed,
                         day_log=day_log)

@app.route('/diet_plans')
@login_required
def list_diet_plans():
    # Show all public plans and plans created by the current user
    plans = DietPlan.query.filter((DietPlan.is_public == True) | (DietPlan.created_by == current_user.id)).all()
    # Add creator information to each plan
    for plan in plans:
        plan.creator = User.query.get(plan.created_by)
    return render_template('diet_plan_list.html', plans=plans)

@app.route('/workout_plans/add', methods=['GET', 'POST'])
@login_required
def add_workout_plan():
    if request.method == 'POST':
        name = request.form.get('name')
        goal = request.form.get('goal')
        description = request.form.get('description')
        duration_days = request.form.get('duration_days')
        is_public = bool(request.form.get('is_public'))
        image_file = request.files.get('image')
        image_url = None
        if image_file and image_file.filename:
            image_path = os.path.join('static', 'images', image_file.filename)
            image_file.save(image_path)
            image_url = '/' + image_path.replace('\\', '/')
        plan = WorkoutPlan(
            name=name,
            goal=goal,
            description=description,
            image_url=image_url,
            created_by=current_user.id,
            is_public=is_public,
            duration_days=int(duration_days) if duration_days else None
        )
        db.session.add(plan)
        db.session.flush()  # Get plan.id before committing
        # Parse days from form
        day_num = 1
        while True:
            day_workouts = request.form.get(f'day_workouts_{day_num}')
            if not day_workouts:
                break
            day_notes = request.form.get(f'day_notes_{day_num}')
            day = WorkoutPlanDay(
                workout_plan_id=plan.id,
                day_number=day_num,
                workouts=day_workouts,
                notes=day_notes
            )
            db.session.add(day)
            day_num += 1
        db.session.commit()
        flash('Workout plan created successfully!', 'success')
        return redirect(url_for('view_workout_plan', plan_id=plan.id))
    return render_template('add_workout_plan.html')

@app.route('/workout_plans/<int:plan_id>')
@login_required
def view_workout_plan(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    days = WorkoutPlanDay.query.filter_by(workout_plan_id=plan.id).all()
    creator = User.query.get(plan.created_by)
    
    # Check if user is following this plan and calculate current day
    current_day = None
    start_date = None
    today_completed = False
    is_following = plan.id in [p.id for p in current_user.followed_workout_plans]
    
    if is_following:
        # Get the start date for this plan
        start_date_record = PlanStartDate.query.filter_by(
            user_id=current_user.id,
            plan_type='workout',
            plan_id=plan_id
        ).first()
        
        if start_date_record:
            start_date = start_date_record.started_at.date()
            # Calculate days since starting the plan
            today = date.today()
            days_since_start = (today - start_date).days
            
            # Calculate which day of the plan we're on (1-based)
            if plan.duration_days:
                # Use modulo to cycle through the plan days
                current_day = (days_since_start % plan.duration_days) + 1
            else:
                # If no duration specified, just count days from start
                current_day = days_since_start + 1
            
            # Ensure current_day doesn't exceed plan duration
            if plan.duration_days and current_day > plan.duration_days:
                current_day = plan.duration_days
            
            # Check if today's workout is completed for this specific plan
            today_log = UserWorkoutLog.query.filter_by(
                user_id=current_user.id,
                workout_plan_id=plan_id,
                date=today
            ).first()
            
            if today_log and today_log.completed:
                today_completed = True
    
    return render_template('workout_plan_detail.html', 
                         plan=plan, 
                         days=days, 
                         creator=creator,
                         current_day=current_day,
                         start_date=start_date,
                         is_following=is_following,
                         today_completed=today_completed)

@app.route('/workout_plans')
@login_required
def list_workout_plans():
    # Show all public plans and plans created by the current user
    plans = WorkoutPlan.query.filter((WorkoutPlan.is_public == True) | (WorkoutPlan.created_by == current_user.id)).all()
    # Add creator information to each plan
    for plan in plans:
        plan.creator = User.query.get(plan.created_by)
    return render_template('workout_plan_list.html', plans=plans)

@app.route('/my_plans')
@login_required
def my_plans():
    # Fetch user's current diet and workout plans (first followed or created, for now)
    diet_plan = (current_user.followed_diet_plans or DietPlan.query.filter_by(created_by=current_user.id).all())
    diet_plan = diet_plan[0] if diet_plan else None
    workout_plan = (current_user.followed_workout_plans or WorkoutPlan.query.filter_by(created_by=current_user.id).all())
    workout_plan = workout_plan[0] if workout_plan else None
    
    # Calculate progress and streaks
    diet_progress = 0
    diet_streak = 0
    workout_progress = 0
    workout_streak = 0
    
    if diet_plan:
        # Calculate diet progress based on logged meals
        logs = UserDietLog.query.filter_by(user_id=current_user.id, diet_plan_id=diet_plan.id).count()
        diet_progress = min(int((logs / 30) * 100), 100)  # Assume 30 days for progress calculation
        diet_streak = logs  # For now, use total logs as streak
    
    if workout_plan:
        # Calculate workout progress based on completed workouts
        logs = UserWorkoutLog.query.filter_by(user_id=current_user.id, workout_plan_id=workout_plan.id, completed=True).count()
        workout_progress = min(int((logs / (workout_plan.duration_days or 30)) * 100), 100)
        workout_streak = logs  # For now, use total completed workouts as streak
    
    # Get recent activity
    recent_meals = UserDietLog.query.filter_by(user_id=current_user.id).order_by(UserDietLog.date.desc()).limit(5).all()
    recent_workouts = UserWorkoutLog.query.filter_by(user_id=current_user.id).order_by(UserWorkoutLog.date.desc()).limit(5).all()
    
    # Add workout names to recent workouts
    for workout_log in recent_workouts:
        if workout_log.workout_id:
            workout_log.workout = Workout.query.get(workout_log.workout_id)
    
    # Get today's workout if user has an active workout plan
    todays_workout = None
    if workout_plan:
        # Get the start date for this plan
        start_date_record = PlanStartDate.query.filter_by(
            user_id=current_user.id,
            plan_type='workout',
            plan_id=workout_plan.id
        ).first()
        
        if start_date_record:
            # Calculate days since starting the plan
            today = date.today()
            start_date = start_date_record.started_at.date()
            days_since_start = (today - start_date).days
            
            # Calculate which day of the plan we're on
            day_number = (days_since_start % workout_plan.duration_days) + 1 if workout_plan.duration_days else 1
        else:
            # Fallback: start from day 1
            day_number = 1
        
        # Get today's workout day
        todays_plan_day = WorkoutPlanDay.query.filter_by(
            workout_plan_id=workout_plan.id, 
            day_number=day_number
        ).first()
        
        if todays_plan_day:
            todays_workout = todays_plan_day
    
    return render_template('my_plans.html',
        diet_plan=diet_plan,
        workout_plan=workout_plan,
        diet_progress=diet_progress,
        diet_streak=diet_streak,
        workout_progress=workout_progress,
        workout_streak=workout_streak,
        recent_meals=recent_meals,
        recent_workouts=recent_workouts,
        todays_workout=todays_workout)

@app.route('/log_meal', methods=['GET', 'POST'])
@login_required
def log_meal():
    # Get user's current diet plan
    diet_plan = (current_user.followed_diet_plans or DietPlan.query.filter_by(created_by=current_user.id).all())
    diet_plan = diet_plan[0] if diet_plan else None
    if not diet_plan:
        flash('No diet plan selected.', 'warning')
        return redirect(url_for('my_plans'))
    if request.method == 'POST':
        meal_type = request.form.get('meal_type')
        foods = request.form.get('foods')
        calories = request.form.get('calories')
        notes = request.form.get('notes')
        log = UserDietLog(
            user_id=current_user.id,
            diet_plan_id=diet_plan.id,
            date=datetime.now(timezone.utc).date(),
            meal_type=meal_type,
            foods=foods,
            calories=int(calories) if calories else None,
            notes=notes
        )
        db.session.add(log)
        db.session.commit()
        flash('Meal logged successfully!', 'success')
        return redirect(url_for('my_plans'))
    return render_template('log_meal.html', diet_plan=diet_plan)

@app.route('/follow_diet_plan/<int:plan_id>', methods=['POST'])
@login_required
def follow_diet_plan(plan_id):
    plan = DietPlan.query.get_or_404(plan_id)
    if plan.id not in [p.id for p in current_user.followed_diet_plans]:
        current_user.followed_diet_plans.append(plan)
        
        # Check if user already has a start date for this plan
        existing_start = PlanStartDate.query.filter_by(
            user_id=current_user.id,
            plan_type='diet',
            plan_id=plan_id
        ).first()
        
        if not existing_start:
            # Record the start date
            start_date = PlanStartDate(
                user_id=current_user.id,
                plan_type='diet',
                plan_id=plan_id
            )
            db.session.add(start_date)
        
        db.session.commit()
        flash(f'You are now following the "{plan.name}" diet plan!', 'success')
    else:
        flash('You are already following this plan.', 'info')
    return redirect(url_for('view_diet_plan', plan_id=plan_id))

@app.route('/unfollow_diet_plan/<int:plan_id>', methods=['POST'])
@login_required
def unfollow_diet_plan(plan_id):
    plan = DietPlan.query.get_or_404(plan_id)
    if plan.id in [p.id for p in current_user.followed_diet_plans]:
        current_user.followed_diet_plans.remove(plan)
        db.session.commit()
        flash(f'You have stopped following the "{plan.name}" diet plan.', 'info')
    return redirect(url_for('my_plans'))

@app.route('/follow_workout_plan/<int:plan_id>', methods=['POST'])
@login_required
def follow_workout_plan(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.id not in [p.id for p in current_user.followed_workout_plans]:
        current_user.followed_workout_plans.append(plan)
        
        # Check if user already has a start date for this plan
        existing_start = PlanStartDate.query.filter_by(
            user_id=current_user.id,
            plan_type='workout',
            plan_id=plan_id
        ).first()
        
        if not existing_start:
            # Record the start date
            start_date = PlanStartDate(
                user_id=current_user.id,
                plan_type='workout',
                plan_id=plan_id
            )
            db.session.add(start_date)
        
        db.session.commit()
        flash(f'You are now following the "{plan.name}" workout plan!', 'success')
    else:
        flash('You are already following this plan.', 'info')
    return redirect(url_for('view_workout_plan', plan_id=plan_id))

@app.route('/unfollow_workout_plan/<int:plan_id>', methods=['POST'])
@login_required
def unfollow_workout_plan(plan_id):
    plan = WorkoutPlan.query.get_or_404(plan_id)
    if plan.id in [p.id for p in current_user.followed_workout_plans]:
        current_user.followed_workout_plans.remove(plan)
        db.session.commit()
        flash(f'You have stopped following the "{plan.name}" workout plan.', 'info')
    return redirect(url_for('my_plans'))

@app.route('/start_todays_workout/<int:plan_id>')
@login_required
def start_todays_workout(plan_id):
    """Start today's workout from a specific plan"""
    plan = WorkoutPlan.query.get_or_404(plan_id)
    
    # Check if user is following this plan
    if plan.id not in [p.id for p in current_user.followed_workout_plans]:
        flash('You must be following this plan to start today\'s workout.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get current day
    start_date_record = PlanStartDate.query.filter_by(
        user_id=current_user.id,
        plan_type='workout',
        plan_id=plan_id
    ).first()
    
    if not start_date_record:
        flash('No start date found for this plan.', 'error')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    start_date = start_date_record.started_at.date()
    today = date.today()
    days_since_start = (today - start_date).days
    
    if plan.duration_days:
        current_day = (days_since_start % plan.duration_days) + 1
    else:
        current_day = days_since_start + 1
    
    if plan.duration_days and current_day > plan.duration_days:
        current_day = plan.duration_days
    
    # Get today's workout day
    today_workout_day = WorkoutPlanDay.query.filter_by(
        workout_plan_id=plan.id,
        day_number=current_day
    ).first()
    
    if not today_workout_day:
        flash('No workout found for today.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Check if already completed today
    today_log = UserWorkoutLog.query.filter_by(
        user_id=current_user.id,
        workout_plan_id=plan.id,
        date=today
    ).first()
    
    if today_log and today_log.completed:
        flash(f'Day {current_day} already completed! Come back tomorrow for Day {current_day + 1 if current_day < plan.duration_days else 1}.', 'info')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get the workout for today (assuming first workout in the list)
    try:
        workout_ids = json.loads(today_workout_day.workouts)
        if workout_ids:
            workout = Workout.query.get(workout_ids[0])
        else:
            workout = None
    except:
        workout = None
    
    # Redirect to the interactive workout session
    if workout:
        return redirect(url_for('workout_session', plan_id=plan_id, workout_id=workout.id))
    else:
        flash('No workout found for today.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))

@app.route('/complete_todays_workout/<int:plan_id>', methods=['POST'])
@login_required
def complete_todays_workout(plan_id):
    """Mark today's workout as completed"""
    plan = WorkoutPlan.query.get_or_404(plan_id)
    
    # Check if user is following this plan
    if plan.id not in [p.id for p in current_user.followed_workout_plans]:
        flash('You must be following this plan to complete today\'s workout.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get current day
    start_date_record = PlanStartDate.query.filter_by(
        user_id=current_user.id,
        plan_type='workout',
        plan_id=plan_id
    ).first()
    
    if not start_date_record:
        flash('No start date found for this plan.', 'error')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    start_date = start_date_record.started_at.date()
    today = date.today()
    days_since_start = (today - start_date).days
    
    if plan.duration_days:
        current_day = (days_since_start % plan.duration_days) + 1
    else:
        current_day = days_since_start + 1
    
    if plan.duration_days and current_day > plan.duration_days:
        current_day = plan.duration_days
    
    # Check if already completed today
    today_log = UserWorkoutLog.query.filter_by(
        user_id=current_user.id,
        workout_plan_id=plan.id,
        date=today
    ).first()
    
    if today_log and today_log.completed:
        flash(f'Day {current_day} already completed! Come back tomorrow for Day {current_day + 1 if current_day < plan.duration_days else 1}.', 'info')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get today's workout day
    today_workout_day = WorkoutPlanDay.query.filter_by(
        workout_plan_id=plan.id,
        day_number=current_day
    ).first()
    
    if not today_workout_day:
        flash('No workout found for today.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get the workout for today
    try:
        workout_ids = json.loads(today_workout_day.workouts)
        workout_id = workout_ids[0] if workout_ids else None
    except:
        workout_id = None
    
    # Create or update workout log
    if today_log:
        today_log.completed = True
        today_log.workout_id = workout_id
        today_log.notes = request.form.get('notes', '')
    else:
        log = UserWorkoutLog(
            user_id=current_user.id,
            workout_plan_id=plan.id,
            date=today,
            workout_id=workout_id,
            completed=True,
            notes=request.form.get('notes', '')
        )
        db.session.add(log)
    
    db.session.commit()
    
    # Determine next day message
    if current_day < plan.duration_days:
        next_day = current_day + 1
        flash(f'🎉 Day {current_day} completed! Come back tomorrow for Day {next_day}.', 'success')
    else:
        flash(f'🎉 Day {current_day} completed! You\'ve finished the plan! Start over for Day 1.', 'success')
    
    return redirect(url_for('view_workout_plan', plan_id=plan_id))

@app.route('/workout_session/<int:plan_id>/<int:workout_id>')
@login_required
def workout_session(plan_id, workout_id):
    """Interactive workout session with exercise-by-exercise flow"""
    plan = WorkoutPlan.query.get_or_404(plan_id)
    workout = Workout.query.get_or_404(workout_id)
    
    # Check if user is following this plan
    if plan.id not in [p.id for p in current_user.followed_workout_plans]:
        flash('You must be following this plan to start today\'s workout.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get current day
    start_date_record = PlanStartDate.query.filter_by(
        user_id=current_user.id,
        plan_type='workout',
        plan_id=plan_id
    ).first()
    
    if not start_date_record:
        flash('No start date found for this plan.', 'error')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    start_date = start_date_record.started_at.date()
    today = date.today()
    days_since_start = (today - start_date).days
    
    if plan.duration_days:
        current_day = (days_since_start % plan.duration_days) + 1
    else:
        current_day = days_since_start + 1
    
    if plan.duration_days and current_day > plan.duration_days:
        current_day = plan.duration_days
    
    # Check if already completed today
    today_log = UserWorkoutLog.query.filter_by(
        user_id=current_user.id,
        workout_plan_id=plan.id,
        date=today
    ).first()
    
    if today_log and today_log.completed:
        flash(f'Day {current_day} already completed! Come back tomorrow for Day {current_day + 1 if current_day < plan.duration_days else 1}.', 'info')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get exercises for this workout
    exercises = workout.exercises
    if not exercises:
        flash('No exercises found for this workout.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    return render_template('workout_session.html',
                         plan=plan,
                         workout=workout,
                         exercises=exercises,
                         current_day=current_day,
                         total_exercises=len(exercises))

@app.route('/workout_exercise/<int:plan_id>/<int:workout_id>/<int:exercise_index>')
@login_required
def workout_exercise(plan_id, workout_id, exercise_index):
    """Show individual exercise during workout session"""
    if plan_id == 0:
        plan = None
        workout = Workout.query.get_or_404(workout_id)
        exercises = workout.exercises
        if not exercises or exercise_index >= len(exercises):
            flash('Exercise not found.', 'error')
            return redirect(url_for('workout_detail', workout_id=workout_id))
        exercise = exercises[exercise_index]
        is_last_exercise = exercise_index == len(exercises) - 1
        return render_template('workout_exercise.html',
                             plan=plan,
                             workout=workout,
                             exercise=exercise,
                             exercise_index=exercise_index,
                             total_exercises=len(exercises),
                             is_last_exercise=is_last_exercise)
    else:
        plan = WorkoutPlan.query.get_or_404(plan_id)
        workout = Workout.query.get_or_404(workout_id)
        # Check if user is following this plan
        if plan.id not in [p.id for p in current_user.followed_workout_plans]:
            flash('You must be following this plan to continue the workout.', 'warning')
            return redirect(url_for('view_workout_plan', plan_id=plan_id))
        # Get exercises for this workout
        exercises = workout.exercises
        if not exercises or exercise_index >= len(exercises):
            flash('Exercise not found.', 'error')
            return redirect(url_for('workout_session', plan_id=plan_id, workout_id=workout_id))
        exercise = exercises[exercise_index]
        is_last_exercise = exercise_index == len(exercises) - 1
        return render_template('workout_exercise.html',
                             plan=plan,
                             workout=workout,
                             exercise=exercise,
                             exercise_index=exercise_index,
                             total_exercises=len(exercises),
                             is_last_exercise=is_last_exercise)

@app.route('/complete_workout/<int:plan_id>/<int:workout_id>', methods=['POST'])
@login_required
def complete_workout(plan_id, workout_id):
    """Mark the entire workout as completed"""
    plan = WorkoutPlan.query.get_or_404(plan_id)
    workout = Workout.query.get_or_404(workout_id)
    
    # Check if user is following this plan
    if plan.id not in [p.id for p in current_user.followed_workout_plans]:
        flash('You must be following this plan to complete the workout.', 'warning')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Get current day
    start_date_record = PlanStartDate.query.filter_by(
        user_id=current_user.id,
        plan_type='workout',
        plan_id=plan_id
    ).first()
    
    if not start_date_record:
        flash('No start date found for this plan.', 'error')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    start_date = start_date_record.started_at.date()
    today = date.today()
    days_since_start = (today - start_date).days
    
    if plan.duration_days:
        current_day = (days_since_start % plan.duration_days) + 1
    else:
        current_day = days_since_start + 1
    
    if plan.duration_days and current_day > plan.duration_days:
        current_day = plan.duration_days
    
    # Check if already completed today
    today_log = UserWorkoutLog.query.filter_by(
        user_id=current_user.id,
        workout_plan_id=plan.id,
        date=today
    ).first()
    
    if today_log and today_log.completed:
        flash(f'Day {current_day} already completed! Come back tomorrow for Day {current_day + 1 if current_day < plan.duration_days else 1}.', 'info')
        return redirect(url_for('view_workout_plan', plan_id=plan_id))
    
    # Create or update workout log
    if today_log:
        today_log.completed = True
        today_log.workout_id = workout_id
        today_log.notes = request.form.get('notes', '')
    else:
        log = UserWorkoutLog(
            user_id=current_user.id,
            workout_plan_id=plan.id,
            date=today,
            workout_id=workout_id,
            completed=True,
            notes=request.form.get('notes', '')
        )
        db.session.add(log)
    
    db.session.commit()
    
    # Determine next day message
    if current_day < plan.duration_days:
        next_day = current_day + 1
        flash(f'🎉 Day {current_day} completed! Come back tomorrow for Day {next_day}.', 'success')
    else:
        flash(f'🎉 Day {current_day} completed! You\'ve finished the plan! Start over for Day 1.', 'success')
    
    return redirect(url_for('view_workout_plan', plan_id=plan_id))

@app.route('/log_workout', methods=['GET', 'POST'])
@login_required
def log_workout():
    # Get user's current workout plan
    workout_plan = (current_user.followed_workout_plans or WorkoutPlan.query.filter_by(created_by=current_user.id).all())
    workout_plan = workout_plan[0] if workout_plan else None
    if not workout_plan:
        flash('No workout plan selected.', 'warning')
        return redirect(url_for('my_plans'))
    if request.method == 'POST':
        workout_id = request.form.get('workout_id')
        completed = bool(request.form.get('completed'))
        notes = request.form.get('notes')
        log = UserWorkoutLog(
            user_id=current_user.id,
            workout_plan_id=workout_plan.id,
            date=datetime.now(timezone.utc).date(),
            workout_id=int(workout_id) if workout_id else None,
            completed=completed,
            notes=notes
        )
        db.session.add(log)
        db.session.commit()
        flash('Workout logged successfully!', 'success')
        return redirect(url_for('my_plans'))
    # For now, show all workouts for selection
    workouts = Workout.query.all()
    return render_template('log_workout.html', workout_plan=workout_plan, workouts=workouts)

@app.route('/mark_meal_completed/<int:plan_id>/<meal_type>', methods=['POST'])
@login_required
def mark_meal_completed(plan_id, meal_type):
    """Mark a specific meal type as completed for today"""
    plan = DietPlan.query.get_or_404(plan_id)
    
    # Check if user is following this plan
    if plan.id not in [p.id for p in current_user.followed_diet_plans]:
        flash('You must be following this plan to mark meals as completed.', 'warning')
        return redirect(url_for('view_diet_plan', plan_id=plan_id))
    
    today = date.today()
    
    # Check if meal is already logged for today
    existing_log = UserDietLog.query.filter_by(
        user_id=current_user.id,
        diet_plan_id=plan_id,
        date=today,
        meal_type=meal_type
    ).first()
    
    if existing_log:
        flash(f'{meal_type} is already logged for today!', 'info')
    else:
        # Create a new meal log entry
        log = UserDietLog(
            user_id=current_user.id,
            diet_plan_id=plan_id,
            date=today,
            meal_type=meal_type,
            foods=f'{meal_type} completed',
            calories=None,
            notes=f'Marked as completed on {today}'
        )
        db.session.add(log)
        db.session.commit()
        flash(f'{meal_type} marked as completed!', 'success')
    
    return redirect(url_for('view_diet_plan', plan_id=plan_id))

def seed_database():
    """Seed the database with sample workouts and exercises"""
    # Create admin user if not exists
    admin_user = User.query.filter_by(email='admin@fitroom.com').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@fitroom.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully!")
    
    # Check if data already exists
    if Workout.query.first() is None:
        # Add sample workouts
        sample_workouts = [
            Workout(
                name="Full Body HIIT",
                description="High-intensity interval training to burn calories and build endurance.",
                duration=30,
                difficulty="Beginner",
                category="Cardio",
                image_url="https://via.placeholder.com/400x250/6366f1/ffffff?text=HIIT+Workout",
                created_by=admin_user.id
            ),
            Workout(
                name="Upper Body Strength",
                description="Build muscle and strength with this comprehensive upper body workout.",
                duration=45,
                difficulty="Intermediate",
                category="Strength",
                image_url="https://via.placeholder.com/400x250/f59e0b/ffffff?text=Strength+Training",
                created_by=admin_user.id
            ),
            Workout(
                name="Morning Yoga Flow",
                description="Start your day with this energizing yoga sequence for flexibility and mindfulness.",
                duration=20,
                difficulty="Beginner",
                category="Flexibility",
                image_url="https://via.placeholder.com/400x250/10b981/ffffff?text=Yoga+Flow",
                created_by=admin_user.id
            ),
            Workout(
                name="Advanced HIIT Circuit",
                description="Intense circuit training for experienced fitness enthusiasts.",
                duration=40,
                difficulty="Advanced",
                category="HIIT",
                image_url="https://via.placeholder.com/400x250/ef4444/ffffff?text=Advanced+HIIT",
                created_by=admin_user.id
            ),
            Workout(
                name="Core Strength Basics",
                description="Build a strong foundation with these core-strengthening exercises.",
                duration=25,
                difficulty="Beginner",
                category="Strength",
                image_url="https://via.placeholder.com/400x250/8b5cf6/ffffff?text=Core+Strength",
                created_by=admin_user.id
            ),
            Workout(
                name="Cardio Blast",
                description="Boost your cardiovascular fitness with this dynamic cardio session.",
                duration=35,
                difficulty="Intermediate",
                category="Cardio",
                image_url="https://via.placeholder.com/400x250/06b6d4/ffffff?text=Cardio+Blast",
                created_by=admin_user.id
            )
        ]
        
        for workout in sample_workouts:
            db.session.add(workout)
        db.session.commit()
    
    if Exercise.query.first() is None:
        # Add sample exercises
        sample_exercises = [
            Exercise(
                name="Push-ups",
                description="Classic bodyweight exercise that targets chest, shoulders, and triceps.",
                muscle_group="Chest",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/6366f1/ffffff?text=Push-ups",
                instructions=json.dumps([
                    "Start in a plank position with hands shoulder-width apart",
                    "Lower your body until chest nearly touches the floor",
                    "Push back up to starting position",
                    "Keep your core tight throughout the movement"
                ]),
                key_points=json.dumps([
                    "Maintain straight body alignment",
                    "Breathe steadily throughout",
                    "Keep elbows close to body"
                ])
            ),
            Exercise(
                name="Squats",
                description="Fundamental lower body exercise that builds strength and stability.",
                muscle_group="Legs",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/f59e0b/ffffff?text=Squats",
                instructions=json.dumps([
                    "Stand with feet shoulder-width apart",
                    "Lower your body as if sitting back into a chair",
                    "Keep knees behind toes",
                    "Return to standing position"
                ]),
                key_points=json.dumps([
                    "Keep chest up",
                    "Weight in heels",
                    "Knees track over toes"
                ])
            ),
            Exercise(
                name="Plank",
                description="Isometric core exercise that improves stability and posture.",
                muscle_group="Core",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/10b981/ffffff?text=Plank",
                instructions=json.dumps([
                    "Start in forearm plank position",
                    "Keep body in straight line from head to heels",
                    "Engage core muscles",
                    "Hold position for specified time"
                ]),
                key_points=json.dumps([
                    "Don't let hips sag",
                    "Breathe steadily",
                    "Keep neck neutral"
                ])
            ),
            Exercise(
                name="Pull-ups",
                description="Upper body pulling exercise that targets back and biceps.",
                muscle_group="Back",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/8b5cf6/ffffff?text=Pull-ups",
                instructions=json.dumps([
                    "Hang from pull-up bar with hands shoulder-width apart",
                    "Pull your body up until chin clears the bar",
                    "Lower back down with control",
                    "Repeat for specified reps"
                ]),
                key_points=json.dumps([
                    "Engage back muscles",
                    "Avoid swinging",
                    "Full range of motion"
                ])
            ),
            Exercise(
                name="Bicep Curls",
                description="Isolation exercise for building bicep strength and size.",
                muscle_group="Arms",
                equipment="Dumbbells",
                image_url="https://via.placeholder.com/300x200/ef4444/ffffff?text=Bicep+Curls",
                instructions=json.dumps([
                    "Stand with dumbbells at sides",
                    "Curl weights up toward shoulders",
                    "Lower back down with control",
                    "Keep elbows stationary"
                ]),
                key_points=json.dumps([
                    "Control the movement",
                    "Don't swing weights",
                    "Squeeze at top of movement"
                ])
            ),
            Exercise(
                name="Shoulder Press",
                description="Compound movement for building shoulder strength and stability.",
                muscle_group="Shoulders",
                equipment="Dumbbells",
                image_url="https://via.placeholder.com/300x200/06b6d4/ffffff?text=Shoulder+Press",
                instructions=json.dumps([
                    "Hold dumbbells at shoulder level",
                    "Press weights overhead",
                    "Lower back to starting position",
                    "Keep core engaged"
                ]),
                key_points=json.dumps([
                    "Don't arch back",
                    "Control the movement",
                    "Full extension at top"
                ])
            ),
            Exercise(
                name="Burpees",
                description="Full body exercise that combines squat, push-up, and jump.",
                muscle_group="Full Body",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/6366f1/ffffff?text=Burpees",
                instructions=json.dumps([
                    "Start standing, then squat down",
                    "Place hands on ground and jump feet back",
                    "Perform a push-up",
                    "Jump feet forward and jump up"
                ]),
                key_points=json.dumps([
                    "Maintain good form",
                    "Land softly",
                    "Keep moving continuously"
                ])
            ),
            Exercise(
                name="Mountain Climbers",
                description="Dynamic cardio exercise that targets core and improves coordination.",
                muscle_group="Core",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/f59e0b/ffffff?text=Mountain+Climbers",
                instructions=json.dumps([
                    "Start in plank position",
                    "Drive knees alternately toward chest",
                    "Keep hips level",
                    "Move at a steady pace"
                ]),
                key_points=json.dumps([
                    "Don't let hips rise",
                    "Engage core",
                    "Breathe steadily"
                ])
            ),
            Exercise(
                name="Jumping Jacks",
                description="Classic cardio exercise that gets your heart rate up.",
                muscle_group="Cardio",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/10b981/ffffff?text=Jumping+Jacks",
                instructions=json.dumps([
                    "Start standing with feet together",
                    "Jump feet apart while raising arms",
                    "Jump back to starting position",
                    "Repeat at a steady pace"
                ]),
                key_points=json.dumps([
                    "Land softly",
                    "Keep good posture",
                    "Maintain rhythm"
                ])
            ),
            Exercise(
                name="Lunges",
                description="Unilateral leg exercise that improves balance and strength.",
                muscle_group="Legs",
                equipment="Bodyweight",
                image_url="https://via.placeholder.com/300x200/8b5cf6/ffffff?text=Lunges",
                instructions=json.dumps([
                    "Step forward with one leg",
                    "Lower body until both knees are bent",
                    "Push back to starting position",
                    "Alternate legs"
                ]),
                key_points=json.dumps([
                    "Keep front knee behind toe",
                    "Maintain upright posture",
                    "Control the movement"
                ])
            )
        ]
        
        for exercise in sample_exercises:
            db.session.add(exercise)
        db.session.commit()
        
        # Assign exercises to workouts based on category
        workouts = Workout.query.all()
        exercises = Exercise.query.all()
        
        # Full Body HIIT - cardio and full body exercises
        hiit_workout = Workout.query.filter_by(name="Full Body HIIT").first()
        hiit_exercises = [e for e in exercises if e.name in ["Burpees", "Mountain Climbers", "Jumping Jacks", "Squats", "Push-ups"]]
        hiit_workout.exercises = hiit_exercises
        
        # Upper Body Strength - upper body exercises
        upper_workout = Workout.query.filter_by(name="Upper Body Strength").first()
        upper_exercises = [e for e in exercises if e.name in ["Push-ups", "Pull-ups", "Bicep Curls", "Shoulder Press"]]
        upper_workout.exercises = upper_exercises
        
        # Core Strength Basics - core exercises
        core_workout = Workout.query.filter_by(name="Core Strength Basics").first()
        core_exercises = [e for e in exercises if e.name in ["Plank", "Mountain Climbers", "Push-ups"]]
        core_workout.exercises = core_exercises
        
        # Advanced HIIT Circuit - intense exercises
        advanced_workout = Workout.query.filter_by(name="Advanced HIIT Circuit").first()
        advanced_exercises = [e for e in exercises if e.name in ["Burpees", "Pull-ups", "Mountain Climbers", "Jumping Jacks"]]
        advanced_workout.exercises = advanced_exercises
        
        # Cardio Blast - cardio exercises
        cardio_workout = Workout.query.filter_by(name="Cardio Blast").first()
        cardio_exercises = [e for e in exercises if e.name in ["Jumping Jacks", "Burpees", "Mountain Climbers"]]
        cardio_workout.exercises = cardio_exercises
        
        # Morning Yoga Flow - flexibility exercises (simplified for demo)
        yoga_workout = Workout.query.filter_by(name="Morning Yoga Flow").first()
        yoga_exercises = [e for e in exercises if e.name in ["Plank", "Squats"]]  # Simplified for demo
        yoga_workout.exercises = yoga_exercises
        
        db.session.commit()
    
    # Create sample diet plans
    if DietPlan.query.first() is None:
        diet_plans = [
            DietPlan(
                name="Weight Loss Plan",
                description="A balanced diet plan designed for healthy weight loss with proper nutrition.",
                goal="Weight Loss",
                image_url="https://via.placeholder.com/400x250/10b981/ffffff?text=Weight+Loss",
                created_by=admin_user.id,
                is_public=True
            ),
            DietPlan(
                name="Muscle Gain Plan",
                description="High-protein diet plan to support muscle growth and recovery.",
                goal="Muscle Gain",
                image_url="https://via.placeholder.com/400x250/f59e0b/ffffff?text=Muscle+Gain",
                created_by=admin_user.id,
                is_public=True
            ),
            DietPlan(
                name="Maintenance Plan",
                description="Balanced nutrition plan to maintain current weight and energy levels.",
                goal="Maintenance",
                image_url="https://via.placeholder.com/400x250/6366f1/ffffff?text=Maintenance",
                created_by=admin_user.id,
                is_public=True
            )
        ]
        
        for plan in diet_plans:
            db.session.add(plan)
        db.session.commit()
        
        # Add meals to diet plans
        weight_loss_plan = DietPlan.query.filter_by(name="Weight Loss Plan").first()
        weight_loss_meals = [
            Meal(diet_plan_id=weight_loss_plan.id, name="Breakfast", meal_type="Breakfast", foods="Oatmeal with berries, Greek yogurt, 1 banana", calories=350, notes="High fiber, protein-rich breakfast"),
            Meal(diet_plan_id=weight_loss_plan.id, name="Lunch", meal_type="Lunch", foods="Grilled chicken salad, mixed greens, olive oil dressing", calories=400, notes="Lean protein with vegetables"),
            Meal(diet_plan_id=weight_loss_plan.id, name="Dinner", meal_type="Dinner", foods="Salmon with quinoa, steamed broccoli", calories=450, notes="Omega-3 rich dinner")
        ]
        
        muscle_gain_plan = DietPlan.query.filter_by(name="Muscle Gain Plan").first()
        muscle_gain_meals = [
            Meal(diet_plan_id=muscle_gain_plan.id, name="Breakfast", meal_type="Breakfast", foods="Protein smoothie, whole grain toast, eggs", calories=500, notes="High protein breakfast"),
            Meal(diet_plan_id=muscle_gain_plan.id, name="Lunch", meal_type="Lunch", foods="Lean beef with brown rice, vegetables", calories=600, notes="Protein and complex carbs"),
            Meal(diet_plan_id=muscle_gain_plan.id, name="Dinner", meal_type="Dinner", foods="Tuna steak, sweet potato, green beans", calories=550, notes="Protein-rich dinner")
        ]
        
        maintenance_plan = DietPlan.query.filter_by(name="Maintenance Plan").first()
        maintenance_meals = [
            Meal(diet_plan_id=maintenance_plan.id, name="Breakfast", meal_type="Breakfast", foods="Whole grain cereal, milk, fruit", calories=400, notes="Balanced breakfast"),
            Meal(diet_plan_id=maintenance_plan.id, name="Lunch", meal_type="Lunch", foods="Turkey sandwich, side salad, apple", calories=450, notes="Balanced lunch"),
            Meal(diet_plan_id=maintenance_plan.id, name="Dinner", meal_type="Dinner", foods="Pasta with vegetables, lean meat sauce", calories=500, notes="Balanced dinner")
        ]
        
        for meal in weight_loss_meals + muscle_gain_meals + maintenance_meals:
            db.session.add(meal)
        db.session.commit()
    
    # Create sample workout plans
    if WorkoutPlan.query.first() is None:
        workout_plans = [
            WorkoutPlan(
                name="30-Day Fat Loss Challenge",
                description="Intensive 30-day program designed to burn fat and improve fitness.",
                goal="Fat Loss",
                image_url="https://via.placeholder.com/400x250/ef4444/ffffff?text=Fat+Loss+Challenge",
                created_by=admin_user.id,
                is_public=True,
                duration_days=30
            ),
            WorkoutPlan(
                name="Strength Building Program",
                description="12-week program focused on building muscle and increasing strength.",
                goal="Strength",
                image_url="https://via.placeholder.com/400x250/f59e0b/ffffff?text=Strength+Program",
                created_by=admin_user.id,
                is_public=True,
                duration_days=84
            ),
            WorkoutPlan(
                name="Beginner Fitness Journey",
                description="Gentle 21-day program for beginners to build fitness habits.",
                goal="Fitness",
                image_url="https://via.placeholder.com/400x250/10b981/ffffff?text=Beginner+Journey",
                created_by=admin_user.id,
                is_public=True,
                duration_days=21
            )
        ]
        
        for plan in workout_plans:
            db.session.add(plan)
        db.session.commit()
        
        # Add workout days to plans
        fat_loss_plan = WorkoutPlan.query.filter_by(name="30-Day Fat Loss Challenge").first()
        strength_plan = WorkoutPlan.query.filter_by(name="Strength Building Program").first()
        beginner_plan = WorkoutPlan.query.filter_by(name="Beginner Fitness Journey").first()
        
        # Fat Loss Plan - 30 days with different workouts
        for day in range(1, 31):
            if day % 3 == 1:
                workouts = "Full Body HIIT, Cardio Blast"
            elif day % 3 == 2:
                workouts = "Advanced HIIT Circuit, Core Strength Basics"
            else:
                workouts = "Morning Yoga Flow"  # Rest day
            day_entry = WorkoutPlanDay(
                workout_plan_id=fat_loss_plan.id,
                day_number=day,
                workouts=workouts,
                notes=f"Day {day} of fat loss challenge"
            )
            db.session.add(day_entry)
        
        # Strength Plan - 84 days (12 weeks)
        for day in range(1, 85):
            if day % 4 == 1:
                workouts = "Upper Body Strength"
            elif day % 4 == 2:
                workouts = "Core Strength Basics"
            elif day % 4 == 3:
                workouts = "Full Body HIIT"
            else:
                workouts = "Morning Yoga Flow"  # Rest day
            day_entry = WorkoutPlanDay(
                workout_plan_id=strength_plan.id,
                day_number=day,
                workouts=workouts,
                notes=f"Day {day} of strength program"
            )
            db.session.add(day_entry)
        
        # Beginner Plan - 21 days
        for day in range(1, 22):
            if day % 3 == 1:
                workouts = "Morning Yoga Flow"
            elif day % 3 == 2:
                workouts = "Core Strength Basics"
            else:
                workouts = "Full Body HIIT"
            day_entry = WorkoutPlanDay(
                workout_plan_id=beginner_plan.id,
                day_number=day,
                workouts=workouts,
                notes=f"Day {day} of beginner journey"
            )
            db.session.add(day_entry)
        
        db.session.commit()
        print("Database seeded successfully with workouts, exercises, diet plans, and workout plans!")

def mark_diet_day_completed(user_id, plan_id, today):
    existing = UserDietDayLog.query.filter_by(user_id=user_id, diet_plan_id=plan_id, date=today).first()
    if not existing:
        log = UserDietDayLog(user_id=user_id, diet_plan_id=plan_id, date=today, completed=True)
        db.session.add(log)
        db.session.commit()

@app.route('/single_workout_exercise/<int:workout_id>/<int:exercise_index>')
@login_required
def single_workout_exercise(workout_id, exercise_index):
    """Show individual exercise for a single (non-plan) workout session"""
    workout = Workout.query.get_or_404(workout_id)
    exercises = workout.exercises
    if not exercises or exercise_index >= len(exercises):
        flash('Exercise not found.', 'error')
        return redirect(url_for('workout_detail', workout_id=workout_id))
    exercise = exercises[exercise_index]
    is_last_exercise = exercise_index == len(exercises) - 1
    return render_template('single_workout_exercise.html',
                         workout=workout,
                         exercise=exercise,
                         exercise_index=exercise_index,
                         total_exercises=len(exercises),
                         is_last_exercise=is_last_exercise)

@app.route('/complete_single_workout/<int:workout_id>', methods=['POST'])
@login_required
def complete_single_workout(workout_id):
    """Mark a single (non-plan) workout as completed"""
    notes = request.form.get('notes', '')
    log = UserWorkoutLog(
        user_id=current_user.id,
        workout_plan_id=None,
        date=datetime.now(timezone.utc).date(),
        workout_id=workout_id,
        completed=True,
        notes=notes
    )
    db.session.add(log)
    db.session.commit()
    flash('Workout completed and logged!', 'success')
    return redirect(url_for('workout_detail', workout_id=workout_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()  # Seed with sample data
    app.run(debug=True, host='0.0.0.0', port=5000) 
    