# Fitness Application ER Diagram

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string password_hash
        datetime created_at
        string profile_picture
        string bio
        boolean is_admin
    }
    
    EXERCISE {
        int id PK
        string name
        string description
        string muscle_group
        string equipment
        string image_url
        string video_url
        string instructions
        string key_points
    }
    
    WORKOUT {
        int id PK
        string name
        string description
        int duration
        string difficulty
        string category
        string image_url
        int created_by FK
    }
    
    DIET_PLAN {
        int id PK
        string name
        string description
        string goal
        string image_url
        int created_by FK
        boolean is_public
    }
    
    WORKOUT_PLAN {
        int id PK
        string name
        string description
        string goal
        string image_url
        int created_by FK
        boolean is_public
        int duration_days
    }
    
    MEAL {
        int id PK
        int diet_plan_id FK
        string name
        string meal_type
        string foods
        int calories
        string notes
    }
    
    WORKOUT_PLAN_DAY {
        int id PK
        int workout_plan_id FK
        int day_number
        string workouts
        string notes
    }
    
    PLAN_START_DATE {
        int id PK
        int user_id FK
        string plan_type
        int plan_id
        datetime started_at
    }
    
    USER_WORKOUT_LOG {
        int id PK
        int user_id FK
        int workout_plan_id FK
        date date
        int workout_id FK
        boolean completed
        string notes
    }
    
    USER_DIET_LOG {
        int id PK
        int user_id FK
        int diet_plan_id FK
        date date
        string meal_type
        string foods
        int calories
        string notes
    }
    
    USER_DIET_DAY_LOG {
        int id PK
        int user_id FK
        int diet_plan_id FK
        date date
        boolean completed
    }
    
    USER_WORKOUT_PLAN {
        int user_id FK
        int workout_plan_id FK
    }
    
    USER_DIET_PLAN {
        int user_id FK
        int diet_plan_id FK
    }
    
    WORKOUT_EXERCISES {
        int workout_id FK
        int exercise_id FK
    }

    %% Relationships
    USER ||--o{ WORKOUT : "creates"
    USER ||--o{ DIET_PLAN : "creates"
    USER ||--o{ WORKOUT_PLAN : "creates"
    
    USER ||--o{ USER_WORKOUT_PLAN : "subscribes to"
    USER ||--o{ USER_DIET_PLAN : "subscribes to"
    USER ||--o{ USER_WORKOUT_LOG : "logs"
    USER ||--o{ USER_DIET_LOG : "logs"
    USER ||--o{ USER_DIET_DAY_LOG : "logs daily"
    USER ||--o{ PLAN_START_DATE : "starts"
    
    WORKOUT ||--o{ WORKOUT_EXERCISES : "contains"
    EXERCISE ||--o{ WORKOUT_EXERCISES : "included in"
    
    WORKOUT_PLAN ||--o{ WORKOUT_PLAN_DAY : "has days"
    WORKOUT_PLAN ||--o{ USER_WORKOUT_PLAN : "assigned to users"
    WORKOUT_PLAN ||--o{ USER_WORKOUT_LOG : "tracked in logs"
    
    DIET_PLAN ||--o{ MEAL : "contains"
    DIET_PLAN ||--o{ USER_DIET_PLAN : "assigned to users"
    DIET_PLAN ||--o{ USER_DIET_LOG : "tracked in logs"
    DIET_PLAN ||--o{ USER_DIET_DAY_LOG : "tracked daily"
    
    WORKOUT ||--o{ USER_WORKOUT_LOG : "logged in"
```

## Key Relationships:

1. **User Management**: Users can create workouts, diet plans, and workout plans
2. **Plan Subscriptions**: Users can subscribe to workout plans and diet plans
3. **Exercise Integration**: Workouts contain multiple exercises through the junction table
4. **Logging System**: Users can log their workout sessions and meal consumption
5. **Plan Structure**: Workout plans have multiple days, diet plans have multiple meals
6. **Progress Tracking**: Daily logs track completion status and detailed activity logs

## Notes:
- `WORKOUT_EXERCISES` is a many-to-many junction table between workouts and exercises
- `USER_WORKOUT_PLAN` and `USER_DIET_PLAN` are subscription tables
- `PLAN_START_DATE` tracks when users start following specific plans
- All user activities are logged with timestamps for progress tracking
