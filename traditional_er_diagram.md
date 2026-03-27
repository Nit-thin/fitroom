# Fitness Application - Traditional ER Diagram

## Entity-Relationship Diagram

```
                    ┌─────────────┐
                    │    USER     │
                    │             │
                    └─────┬───────┘
                          │
                          │ Has
                          │
                    ┌─────▼───────┐
                    │   LOGIN     │
                    │             │
                    └─────┬───────┘
                          │
                          │ Accesses
                          │
                    ┌─────▼───────┐
                    │    HOME     │
                    │ (Dashboard) │
                    └─────┬───────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
            │             │             │
    ┌───────▼───────┐ ┌───▼────┐ ┌─────▼───────┐
    │   WORKOUT     │ │ EXERCISE│ │ DIET_PLAN   │
    │               │ │        │ │             │
    └───────┬───────┘ └───┬────┘ └─────┬───────┘
            │             │             │
            │ Contains    │             │ Contains
            │             │             │
            └─────────────┼─────────────┘
                          │
                    ┌─────▼───────┐
                    │   LOGGING   │
                    │             │
                    └─────┬───────┘
                          │
                          │ Generates
                          │
                    ┌─────▼───────┐
                    │   RESULTS   │
                    │ (Progress)  │
                    └─────────────┘
```

## Detailed Entity Descriptions

### Core Entities:

**USER**
- Attributes: id, username, email, password_hash, created_at, profile_picture, bio, is_admin
- Relationships: Has LOGIN, Creates WORKOUT/DIET_PLAN

**LOGIN** 
- Attributes: email, password_hash, session_token
- Relationships: Belongs to USER, Accesses HOME

**HOME (Dashboard)**
- Attributes: user_id, last_login, notifications
- Relationships: Central hub connecting to all main features

**WORKOUT**
- Attributes: id, name, description, duration, difficulty, category, image_url, created_by
- Relationships: Contains EXERCISES, Logged by USER

**EXERCISE**
- Attributes: id, name, description, muscle_group, equipment, instructions, key_points
- Relationships: Part of WORKOUTS, Used in LOGGING

**DIET_PLAN**
- Attributes: id, name, description, goal, image_url, created_by, is_public
- Relationships: Contains MEALS, Followed by USER

**MEAL**
- Attributes: id, name, meal_type, foods, calories, notes
- Relationships: Part of DIET_PLAN, Logged by USER

**LOGGING**
- Attributes: id, user_id, date, activity_type, completed, notes
- Relationships: Records USER activities, Generates RESULTS

**RESULTS (Progress Tracking)**
- Attributes: id, user_id, workout_count, diet_adherence, progress_metrics
- Relationships: Generated from LOGGING, Shows USER progress

## Key Relationships:

1. **USER** ──Has──> **LOGIN**
2. **LOGIN** ──Accesses──> **HOME**
3. **HOME** ──Connects to──> **WORKOUT**, **EXERCISE**, **DIET_PLAN**
4. **WORKOUT** ──Contains──> **EXERCISE**
5. **DIET_PLAN** ──Contains──> **MEAL**
6. **USER** ──Logs──> **LOGGING**
7. **LOGGING** ──Generates──> **RESULTS**

## Additional Junction Tables:

- **USER_WORKOUT_PLAN**: Links users to workout plans
- **USER_DIET_PLAN**: Links users to diet plans  
- **WORKOUT_EXERCISES**: Many-to-many between workouts and exercises
- **USER_WORKOUT_LOG**: Detailed workout session logs
- **USER_DIET_LOG**: Detailed meal consumption logs

This traditional ER diagram shows the main flow: User → Login → Dashboard → Workouts/Exercises/Diet Plans → Logging → Results/Progress Tracking.

