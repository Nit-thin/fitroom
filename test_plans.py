from app import app, db, WorkoutPlan

with app.app_context():
    print('Checking workout plans...')
    
    plans = WorkoutPlan.query.all()
    print(f'Total workout plans: {len(plans)}')
    
    for plan in plans:
        print(f'Plan {plan.id}: {plan.name} (Duration: {plan.duration_days} days)') 