# Detailed Fitness Application ER Diagram

## Traditional ER Diagram with All Shapes

```
                    ┌─────────────────┐
                    │      USER       │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │     id      │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │  username   │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │    email    │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │is_admin     │ │
                    │ └─────────────┘ │
                    └─────────┬───────┘
                              │
                              │ Has
                              │
                    ┌─────────▼───────┐
                    │     LOGIN       │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │session_id   │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │login_time   │ │
                    │ └─────────────┘ │
                    └─────────┬───────┘
                              │
                              │ Accesses
                              │
                    ┌─────────▼───────┐
                    │      HOME       │
                    │   (Dashboard)   │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │user_id      │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │last_visit   │ │
                    │ └─────────────┘ │
                    └─────────┬───────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            │                 │                 │
    ┌───────▼───────┐ ┌───────▼───────┐ ┌─────▼───────┐
    │   WORKOUT     │ │   EXERCISE    │ │  DIET_PLAN  │
    │               │ │               │ │             │
    │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │
    │ │    id     │ │ │ │    id     │ │ │ │   id    │ │
    │ └───────────┘ │ │ └───────────┘ │ │ └─────────┘ │
    │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │
    │ │   name    │ │ │ │   name    │ │ │ │  name   │ │
    │ └───────────┘ │ │ └───────────┘ │ │ └─────────┘ │
    │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │
    │ │duration   │ │ │ │muscle_grp │ │ │ │  goal   │ │
    │ └───────────┘ │ │ └───────────┘ │ │ └─────────┘ │
    │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │
    │ │difficulty │ │ │ │equipment  │ │ │ │is_public│ │
    │ └───────────┘ │ │ └───────────┘ │ │ └─────────┘ │
    └───────┬───────┘ └───────┬───────┘ └─────┬───────┘
            │                 │                 │
            │ Contains        │                 │ Contains
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                    ┌─────────▼───────┐
                    │      MEAL       │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │    id       │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │   name      │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │meal_type    │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │  calories   │ │
                    │ └─────────────┘ │
                    └─────────┬───────┘
                              │
                              │ Logged
                              │
                    ┌─────────▼───────┐
                    │    LOGGING      │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │    id       │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │   date      │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │activity_type│ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │ completed   │ │
                    │ └─────────────┘ │
                    └─────────┬───────┘
                              │
                              │ Generates
                              │
                    ┌─────────▼───────┐
                    │    RESULTS      │
                    │  (Progress)     │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │    id       │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │workout_count│ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │diet_adherence│ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │progress_%   │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

## Shape Types Used:

- **Rectangles** = Entities (USER, WORKOUT, EXERCISE, etc.)
- **Ovals** = Attributes (id, name, email, etc.)
- **Diamonds** = Relationships (Has, Contains, Logged, Generates)
- **Lines** = Connections between entities and relationships

## Additional Junction Tables (Many-to-Many):

```
    ┌─────────────────┐         ┌─────────────────┐
    │   WORKOUT       │         │   EXERCISE      │
    │                 │         │                 │
    └─────────┬───────┘         └───────┬─────────┘
              │                         │
              │ Contains                │ Part of
              │                         │
              └─────────┬───────────────┘
                        │
                ┌───────▼───────┐
                │WORKOUT_EXERCISES│
                │   (Junction)   │
                │                │
                │ ┌─────────────┐│
                │ │workout_id   ││
                │ └─────────────┘│
                │ ┌─────────────┐│
                │ │exercise_id  ││
                │ └─────────────┘│
                └────────────────┘
```

## Code for Drawing Tools:

### For Draw.io / Lucidchart:
```xml
<mxfile>
  <diagram>
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- USER Entity -->
        <mxCell id="user" value="USER" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="200" y="100" width="120" height="80" as="geometry"/>
        </mxCell>
        
        <!-- USER Attributes -->
        <mxCell id="user_id" value="id" style="ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="180" y="200" width="60" height="30" as="geometry"/>
        </mxCell>
        
        <mxCell id="user_username" value="username" style="ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="250" y="200" width="60" height="30" as="geometry"/>
        </mxCell>
        
        <mxCell id="user_email" value="email" style="ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="320" y="200" width="60" height="30" as="geometry"/>
        </mxCell>
        
        <!-- WORKOUT Entity -->
        <mxCell id="workout" value="WORKOUT" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="500" y="100" width="120" height="80" as="geometry"/>
        </mxCell>
        
        <!-- Relationship -->
        <mxCell id="has" value="Has" style="rhombus;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
          <mxGeometry x="350" y="120" width="80" height="40" as="geometry"/>
        </mxCell>
        
        <!-- Connections -->
        <mxCell id="user_to_has" value="" style="endArrow=classic;html=1;rounded=0;" edge="1" parent="1" source="user" target="has">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="320" y="140" as="sourcePoint"/>
            <mxPoint x="350" y="140" as="targetPoint"/>
          </mxGeometry>
        </mxCell>
        
        <mxCell id="has_to_workout" value="" style="endArrow=classic;html=1;rounded=0;" edge="1" parent="1" source="has" target="workout">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="430" y="140" as="sourcePoint"/>
            <mxPoint x="500" y="140" as="targetPoint"/>
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### For Microsoft Word / PowerPoint:
1. Insert → Shapes
2. Use **Rectangle** for entities
3. Use **Oval** for attributes  
4. Use **Diamond** for relationships
5. Use **Lines** to connect them

### For Visio:
1. File → New → Software and Database → Database Model Diagram
2. Drag Entity shapes from stencil
3. Add attributes as text boxes
4. Connect with relationship lines

## Complete Entity List with All Attributes:

**USER**: id, username, email, password_hash, created_at, profile_picture, bio, is_admin
**LOGIN**: session_id, login_time, logout_time, ip_address
**HOME**: user_id, last_visit, notifications_count, theme_preference
**WORKOUT**: id, name, description, duration, difficulty, category, image_url, created_by
**EXERCISE**: id, name, description, muscle_group, equipment, image_url, video_url, instructions, key_points
**DIET_PLAN**: id, name, description, goal, image_url, created_by, is_public, duration_days
**MEAL**: id, diet_plan_id, name, meal_type, foods, calories, notes, prep_time
**LOGGING**: id, user_id, date, activity_type, completed, notes, duration, calories_burned
**RESULTS**: id, user_id, workout_count, diet_adherence, progress_percentage, last_updated

This gives you a complete traditional ER diagram with all the proper shapes and detailed attributes!

