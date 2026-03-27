# Fitroom Clone - Comprehensive Fitness & Nutrition Platform

A full-featured, modern fitness and nutrition web application built with Flask that provides a complete solution for workout planning, exercise tracking, diet management, and progress monitoring. This platform combines structured workout plans, interactive exercise sessions, personalized diet plans, and comprehensive progress tracking in one unified system.

## 🎯 Project Overview

Fitroom Clone is a comprehensive fitness platform designed to help users achieve their health and fitness goals through structured workout plans, detailed exercise guidance, personalized nutrition plans, and real-time progress tracking. The platform features both user-facing functionality and a complete administrative interface for content management.

## 🚀 Key Features

### 🔐 Authentication & User Management
- **Dual Authentication System**: Separate login flows for regular users and administrators
- **User Registration**: Account creation with email validation and profile setup
- **Secure Password Handling**: Password hashing using Werkzeug
- **User Profiles**: Customizable profiles with bio, profile pictures, and personal information
- **Role-Based Access Control**: Admin and regular user roles with appropriate permissions
- **Profile Editing**: Update username, email, bio, and profile picture

### 💪 Workout Management System

#### Workout Library
- **Browse Workouts**: Explore workouts by category (Cardio, Strength, HIIT, Flexibility, Yoga)
- **Workout Details**: View comprehensive workout information including duration, difficulty, category, and description
- **Workout-Exercise Relationships**: Many-to-many relationship allowing workouts to contain multiple exercises
- **Exercise Instructions**: Step-by-step instructions and key points for each exercise
- **Media Support**: Image and video URLs for exercises and workouts

#### Interactive Workout Sessions
- **Exercise-by-Exercise Flow**: Guided workout sessions that walk users through each exercise
- **Workout Completion Tracking**: Mark workouts as completed and log completion data
- **Single Workout Mode**: Ability to complete individual workouts outside of plans
- **Progress Indicators**: Visual feedback showing current exercise position in workout sequence

### 📅 Workout Plans System

#### Structured Programs
- **Multi-Day Plans**: Create workout plans with configurable duration (e.g., 30-day, 84-day programs)
- **Daily Workout Scheduling**: Assign specific workouts to each day of the plan
- **Goal-Based Plans**: Plans categorized by fitness goals (Fat Loss, Strength, Fitness, etc.)
- **Public & Private Plans**: Share plans with community or keep them private
- **Plan Following**: Users can follow plans created by admins or other users

#### Plan Progress Tracking
- **Start Date Tracking**: Record when users begin following a plan
- **Current Day Calculation**: Automatically determines which day of the plan the user is on
- **Daily Completion**: Track daily workout completion status
- **Progress Visualization**: Visual progress indicators and completion status
- **Plan Cycling**: Plans automatically cycle when duration is completed

### 🥗 Diet Plan Management

#### Nutritional Planning
- **Diet Plan Creation**: Build comprehensive diet plans with multiple meals
- **Meal Organization**: Organize meals by type (Breakfast, Lunch, Dinner, Snacks)
- **Nutritional Tracking**: Track calories, foods, and meal notes for each meal
- **Goal-Oriented Plans**: Plans categorized by dietary goals (Weight Loss, Muscle Gain, Maintenance)
- **Public Sharing**: Share diet plans with the community or keep them private

#### Meal Logging & Tracking
- **Daily Meal Logging**: Log meals for each day of following a diet plan
- **Meal Completion Tracking**: Mark individual meals as completed throughout the day
- **Day Completion**: Automatic detection when all meals for a day are completed
- **Nutritional History**: View logged meals and dietary history
- **Progress Badges**: Visual indicators for completed diet days

### 📊 Progress Tracking & Analytics

#### User Statistics
- **Workout Statistics**: Total workouts completed, total hours trained
- **Weekly Progress Charts**: Visual representation of workout activity over the past 7 days
- **Recent Activity**: Display of recently completed workouts
- **Streak Tracking**: Track consecutive days of activity (for diet and workout plans)
- **Progress Bars**: Visual progress indicators for active plans

#### Profile Dashboard
- **My Plans Page**: Centralized view of active diet and workout plans
- **Today's Workout**: Quick access to today's scheduled workout from active plan
- **Recent Logs**: Display of recent meal and workout logs
- **Plan Progress**: Individual progress tracking for each followed plan

### 👨‍💼 Administrative Features

#### Admin Dashboard
- **Platform Overview**: Total workouts, exercises, users, and plans statistics
- **Recent Activity Feed**: Unified feed showing latest platform activities
- **Category Management**: View all workout categories, exercise types, and plan goals
- **Quick Access**: Fast navigation to all management sections

#### Content Management

**Workout Management:**
- Create, edit, and delete workouts
- Assign exercises to workouts
- Manage workout categories, difficulty levels, and durations
- Upload workout images

**Exercise Management:**
- Create, edit, and delete exercises
- Add detailed instructions (JSON-formatted step-by-step guides)
- Add key points and safety tips
- Manage muscle groups and equipment types
- Link exercises to workouts

**Diet Plan Administration:**
- Create multi-meal diet plans
- Manage meal types, calories, and food lists
- Organize plans by dietary goals
- Set plan visibility (public/private)
- Edit existing diet plans and meals

**Workout Plan Administration:**
- Create structured multi-day workout plans
- Schedule workouts for specific days
- Set plan duration and goals
- Manage day-specific notes and workout assignments
- Control plan visibility

**User Management:**
- View all registered users
- View user credentials (for admin access)
- Reset user passwords
- Delete user accounts
- View user-created content statistics

### 🗄️ Database Architecture

The application uses a comprehensive relational database design with the following key models:

- **User**: User accounts with authentication, profiles, and role management
- **Workout**: Individual workout sessions with metadata
- **Exercise**: Exercise library with instructions, images, and details
- **DietPlan**: Structured diet plans with goals and meal organization
- **Meal**: Individual meals belonging to diet plans
- **WorkoutPlan**: Multi-day structured workout programs
- **WorkoutPlanDay**: Daily workout assignments within plans
- **UserWorkoutLog**: User workout completion tracking
- **UserDietLog**: User meal logging and tracking
- **UserDietDayLog**: Daily diet completion tracking
- **PlanStartDate**: Track when users start following plans

### 🔧 Technical Features

#### Backend Technologies
- **Flask 2.3.3**: Python web framework
- **SQLAlchemy 2.0.21**: ORM for database operations
- **Flask-Login 0.6.3**: Session management and user authentication
- **Flask-Migrate**: Database migration support
- **Werkzeug 2.3.7**: Password hashing and security utilities
- **SQLite**: Lightweight database for development and production

#### Frontend Technologies
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Icon library
- **JavaScript**: Interactive functionality and dynamic content
- **Jinja2**: Template engine for dynamic HTML generation

#### Additional Features
- **Database Seeding**: Automatic sample data population on first run
- **File Upload Handling**: Profile picture and image upload support
- **JSON Data Storage**: Flexible storage for structured data (instructions, meal lists)
- **Date/Time Management**: UTC-based timestamp handling
- **RESTful API Endpoints**: JSON API for workouts and exercises

## 📁 Project Structure

```
fitroom-clone/
├── app.py                          # Main Flask application (2,387 lines)
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── fitroom_fresh.db                # SQLite database
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom styles
│   ├── js/
│   │   └── main.js                # JavaScript functionality
│   ├── images/                    # Exercise and workout images
│   └── uploads/                   # User-uploaded profile pictures
│
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── index.html                 # Home/Landing page
│   ├── login.html                 # Login page (user/admin)
│   ├── register.html              # Registration page
│   ├── profile.html               # User profile dashboard
│   ├── workouts.html              # Workouts listing
│   ├── workout_detail.html        # Individual workout view
│   ├── workout_session.html       # Interactive workout session
│   ├── workout_exercise.html      # Exercise during workout flow
│   ├── single_workout_exercise.html # Single workout exercise view
│   ├── exercises.html             # Exercises library
│   ├── exercise_detail.html       # Individual exercise details
│   ├── diet_plan_list.html        # Browse diet plans
│   ├── diet_plan_detail.html      # View specific diet plan
│   ├── add_diet_plan.html         # Create new diet plan
│   ├── workout_plan_list.html     # Browse workout plans
│   ├── workout_plan_detail.html   # View specific workout plan
│   ├── add_workout_plan.html      # Create new workout plan
│   ├── my_plans.html              # User's active plans dashboard
│   ├── log_meal.html             # Meal logging interface
│   ├── log_workout.html           # Workout logging interface
│   ├── todays_workout.html        # Today's workout view
│   │
│   └── admin/                     # Admin panel templates
│       ├── dashboard.html         # Admin dashboard
│       ├── profile.html           # Admin profile
│       ├── workouts.html          # Manage workouts
│       ├── add_workout.html       # Create workout
│       ├── edit_workout.html      # Edit workout & exercises
│       ├── exercises.html         # Manage exercises
│       ├── add_exercise.html      # Create exercise
│       ├── edit_exercise.html     # Edit exercise details
│       ├── users.html             # User management
│       ├── diet_plans.html        # Manage diet plans
│       ├── add_diet_plan.html     # Create diet plan
│       ├── edit_diet_plan.html    # Edit diet plan
│       ├── workout_plans.html     # Manage workout plans
│       ├── add_workout_plan.html  # Create workout plan
│       └── edit_workout_plan.html # Edit workout plan
│
├── migrations/                     # Flask-Migrate database migrations
│   ├── alembic.ini                # Alembic configuration
│   ├── env.py                     # Migration environment
│   └── versions/                  # Migration scripts
│
└── database/                       # Additional database files
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd fitroom-clone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the website**
   Open your browser and go to: `http://localhost:5000`

## 🎯 Key Features Explained

### User Experience Highlights
- **Fresh Start for New Users**: New users begin with clean profiles and no workout history
- **Progressive Disclosure**: Features unlock as users explore the platform
- **Guided Workouts**: Step-by-step exercise guidance during workout sessions
- **Daily Tracking**: Track meals and workouts on a daily basis
- **Visual Progress**: Charts, progress bars, and badges for motivation

### Sample Data & Seeding
The application automatically seeds the database with sample data on first run:

**Workouts (10+):**
- Full Body HIIT, Upper Body Strength, Morning Yoga Flow
- Advanced HIIT Circuit, Core Strength Basics, Cardio Blast
- And more across different categories

**Exercises (10+):**
- Push-ups, Squats, Plank, Pull-ups, Bicep Curls
- Shoulder Press, Burpees, Mountain Climbers, Jumping Jacks, Lunges
- Each with detailed instructions, key points, and muscle group targeting

**Diet Plans (3):**
- Weight Loss Plan (3 meals/day)
- Muscle Gain Plan (3 meals/day)
- Maintenance Plan (3 meals/day)

**Workout Plans (3):**
- 30-Day Fat Loss Challenge (30-day program)
- Strength Building Program (84-day program)
- Beginner Fitness Journey (21-day program)

### Database Models Summary

**User Model:**
- Authentication: username, email, password_hash
- Profile: profile_picture, bio, created_at
- Authorization: is_admin flag for role-based access

**Workout Model:**
- Metadata: name, description, duration (minutes), difficulty, category
- Media: image_url
- Relationships: creator (User), exercises (many-to-many)

**Exercise Model:**
- Details: name, description, muscle_group, equipment
- Media: image_url, video_url
- Instructions: JSON-formatted step-by-step instructions and key points
- Relationships: workouts (many-to-many)

**DietPlan Model:**
- Plan Info: name, description, goal, image_url, is_public
- Relationships: creator (User), meals (one-to-many), followers (many-to-many)

**Meal Model:**
- Details: name, meal_type, foods, calories, notes
- Relationship: diet_plan (many-to-one)

**WorkoutPlan Model:**
- Plan Info: name, description, goal, image_url, duration_days, is_public
- Relationships: creator (User), days (one-to-many), followers (many-to-many)

**WorkoutPlanDay Model:**
- Day Info: day_number, workouts (JSON), notes
- Relationship: workout_plan (many-to-one)

**Tracking Models:**
- UserWorkoutLog: Tracks individual workout completions
- UserDietLog: Tracks meal logging
- UserDietDayLog: Tracks daily diet completion
- PlanStartDate: Records when users start following plans

## 🎨 Design Features

### Modern UI Elements
- **Gradient backgrounds** and smooth animations
- **Card-based layouts** with hover effects
- **Responsive grid system** for all screen sizes
- **Custom color scheme** with CSS variables
- **Interactive buttons** with loading states

### User Experience
- **Intuitive navigation** with clear call-to-actions
- **Search and filter functionality** for workouts/exercises
- **Progress visualization** with charts and progress bars
- **Mobile-first responsive design**

## 🔑 Key Workflows

### User Journey

**Getting Started:**
1. Register a new account or login as existing user
2. Browse available workout plans and diet plans
3. Follow a plan that matches your goals
4. System automatically tracks your start date

**Following a Workout Plan:**
1. View your active plan on "My Plans" page
2. See today's scheduled workout
3. Click "Start Today's Workout" to begin interactive session
4. Navigate through exercises one-by-one with detailed instructions
5. Complete workout and mark as done
6. System tracks progress and shows next day's workout

**Following a Diet Plan:**
1. View your active diet plan details
2. See all meals for the current day
3. Log meals throughout the day as you eat them
4. Mark meals as completed
5. System automatically detects when all meals for the day are completed
6. View progress and completion status

**Creating Content (Admin):**
1. Access admin dashboard
2. Navigate to relevant section (Workouts, Exercises, Plans, Users)
3. Create new content with comprehensive forms
4. Link exercises to workouts, meals to diet plans
5. Set visibility (public/private) and metadata
6. Manage existing content through edit/delete functions

## 🚀 Recent Features & Updates

### Comprehensive Platform Features
- **Interactive Workout Sessions**: Exercise-by-exercise guided workout flow
- **Plan Following System**: Follow multi-day workout and diet plans with automatic day tracking
- **Meal Logging System**: Complete meal tracking with calorie information
- **Progress Visualization**: Weekly progress charts, streaks, and completion tracking
- **Admin Dashboard**: Comprehensive content management interface
- **Multi-Day Plans**: Structured programs with daily workout/meal assignments
- **Plan Cycling**: Automatic plan restart when duration completes

### User Experience Enhancements
- **Today's Workout Feature**: Quick access to current day's scheduled workout
- **My Plans Dashboard**: Centralized view of all active plans
- **Completion Badges**: Visual indicators for completed days
- **Progress Tracking**: Real-time statistics and progress bars
- **Empty State Handling**: Encouraging messages for new users

### Technical Improvements
- **Database Migrations**: Flask-Migrate integration for schema management
- **JSON Data Storage**: Flexible storage for structured data (instructions, meal lists)
- **UTC Timestamps**: Proper timezone handling for date/time operations
- **Many-to-Many Relationships**: Workout-Exercise associations
- **Cascading Deletes**: Proper data cleanup when plans are deleted

## 🔒 Security Features

- **Password hashing** using Werkzeug
- **Session management** with Flask-Login
- **CSRF protection** (can be enabled)
- **Secure form handling**

## 📱 Responsive Design

The website is fully responsive and works on:
- **Desktop computers** (1200px+)
- **Tablets** (768px - 1199px)
- **Mobile phones** (320px - 767px)

## 🎯 Future Enhancements

Potential features to add:
- **Workout tracking**: Log completed workouts
- **Progress photos**: Before/after tracking
- **Social features**: Share achievements
- **Workout plans**: Custom workout creation
- **Nutrition tracking**: Meal planning integration
- **Push notifications**: Workout reminders

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database issues**: Delete `fitroom.db` and restart the app
   ```bash
   rm fitroom.db
   python app.py
   ```

3. **Port already in use**: Change the port in `app.py`
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

## 📄 License

This project is for educational purposes. Feel free to modify and use as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies** 