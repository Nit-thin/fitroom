from app import db, Exercise
import json

instructions_dict = {
    1: [
        'Start in a plank position with your hands slightly wider than shoulder-width apart.',
        'Keep your body in a straight line from head to heels.',
        'Lower your body until your chest nearly touches the floor.',
        'Push back up to the starting position.'
    ],
    2: [
        'Stand with feet shoulder-width apart.',
        'Lower your body by bending your knees and hips.',
        'Keep your chest up and back straight.',
        'Push through your heels to return to standing.'
    ],
    3: [
        'Start in a forearm plank position.',
        'Keep your body in a straight line from head to heels.',
        'Hold the position, engaging your core.'
    ],
    4: [
        'Hang from a pull-up bar with palms facing away.',
        'Pull your chin above the bar by bending your elbows.',
        'Lower yourself back down with control.'
    ],
    5: [
        'Stand with a dumbbell in each hand, arms at your sides.',
        'Curl the weights up while keeping your elbows close to your torso.',
        'Lower the weights back down slowly.'
    ],
    6: [
        'Stand with feet shoulder-width apart.',
        'Drop into a squat position with your hands on the ground.',
        'Kick your feet back into a plank position.',
        'Do a push-up, then jump your feet forward and explosively jump up.'
    ],
    7: [
        'Stand with feet shoulder-width apart, holding dumbbells at shoulder height.',
        'Press the weights overhead until your arms are fully extended.',
        'Lower the weights back to shoulder height.'
    ],
    8: [
        'Start in a plank position.',
        'Bring one knee toward your chest, then quickly switch legs.',
        'Continue alternating legs at a fast pace.'
    ],
    9: [
        'Stand upright with feet together and arms at your sides.',
        'Jump up, spreading your legs and raising your arms overhead.',
        'Return to the starting position and repeat.'
    ],
    10: [
        'Stand upright, step forward with one leg and lower your hips.',
        'Bend both knees to about 90 degrees.',
        'Push back to the starting position and switch legs.'
    ],
    11: [
        'Sit on the edge of a chair or bench, hands next to your hips.',
        'Slide your hips off the edge and lower your body by bending your elbows.',
        'Push back up to the starting position.'
    ],
    12: [
        'Sit on the floor with knees bent, lean back slightly.',
        'Hold your hands together or a weight, twist your torso to one side, then the other.'
    ],
    13: [
        'Stand with your back against a wall, slide down until knees are at 90 degrees.',
        'Hold the position, keeping your back flat against the wall.'
    ],
    14: [
        'Stand upright, run in place while lifting your knees as high as possible.'
    ],
    15: [
        'Lie on your back with legs extended.',
        'Lift your legs a few inches off the ground and flutter them up and down.'
    ],
    16: [
        'Stand upright, extend your arms out to the sides.',
        'Make small circles with your arms, gradually increasing the size.'
    ],
    17: [
        'Stand upright, push through the balls of your feet to raise your heels.',
        'Lower back down with control.'
    ],
    18: [
        'Lie on your back with knees bent and feet flat on the floor.',
        'Lift your shoulders off the floor by contracting your abs.',
        'Lower back down with control.'
    ],
    19: [
        'Lie on your back with legs straight.',
        'Lift your legs up toward the ceiling, then lower them back down without touching the floor.'
    ],
    20: [
        'Move through a series of dynamic stretches (e.g., arm swings, leg swings, torso twists) to warm up the body.'
    ],
    21: [
        'Perform controlled movements of each joint (e.g., neck circles, shoulder rolls, hip circles) to increase mobility.'
    ],
    22: [
        'Gently stretch each major muscle group, holding each stretch for 15-30 seconds.'
    ],
    23: [
        'Perform exercises that improve range of motion (e.g., deep squats, hip openers, shoulder dislocates).'
    ],
    24: [
        'Sit or lie comfortably, inhale deeply through your nose, exhale slowly through your mouth, focusing on your breath.'
    ]
}

key_points_dict = {
    1: [
        'Engage your core throughout.',
        'Do not let your hips sag or pike up.',
        'Keep elbows at about a 45-degree angle.'
    ],
    2: [
        'Keep your knees in line with your toes.',
        'Do not let your heels lift off the ground.',
        'Keep your chest up.'
    ],
    3: [
        'Do not let your hips drop.',
        'Keep your neck neutral.',
        'Breathe steadily.'
    ],
    4: [
        'Avoid swinging your body.',
        'Use a full range of motion.',
        'Engage your back and biceps.'
    ],
    5: [
        'Keep your elbows stationary.',
        'Do not use momentum.',
        'Squeeze at the top of the curl.'
    ],
    6: [
        'Land softly on your feet.',
        'Keep your core engaged.',
        'Move quickly but with control.'
    ],
    7: [
        'Do not arch your back.',
        'Press straight up, not forward.',
        'Lower weights with control.'
    ],
    8: [
        'Keep your hips low.',
        'Move quickly for cardio benefit.',
        'Maintain a strong plank position.'
    ],
    9: [
        'Land softly on your feet.',
        'Keep your arms straight.',
        'Maintain a steady rhythm.'
    ],
    10: [
        'Keep your front knee over your ankle.',
        'Do not let your back knee touch the floor.',
        'Keep your torso upright.'
    ],
    11: [
        'Keep your back close to the bench.',
        'Do not lock your elbows at the top.',
        'Lower yourself slowly.'
    ],
    12: [
        'Keep your back straight.',
        'Twist from your torso, not just your arms.',
        'Engage your core.'
    ],
    13: [
        'Keep your knees at 90 degrees.',
        'Do not let your back arch.',
        'Hold as long as possible.'
    ],
    14: [
        'Pump your arms for momentum.',
        'Land softly on your feet.',
        'Keep your core engaged.'
    ],
    15: [
        'Keep your lower back pressed to the floor.',
        'Move legs quickly but with control.',
        'Breathe steadily.'
    ],
    16: [
        'Keep your arms straight.',
        'Do not shrug your shoulders.',
        'Reverse direction halfway through.'
    ],
    17: [
        'Do not bounce at the top.',
        'Lower your heels slowly.',
        'Hold onto a support if needed.'
    ],
    18: [
        'Do not pull on your neck.',
        'Exhale as you crunch up.',
        'Keep your lower back on the floor.'
    ],
    19: [
        'Do not use momentum.',
        'Keep your legs straight.',
        'Lower legs slowly.'
    ],
    20: [
        'Move smoothly through each stretch.',
        'Do not force any movement.',
        'Focus on warming up.'
    ],
    21: [
        'Move joints through full range of motion.',
        'Do not rush.',
        'Focus on control.'
    ],
    22: [
        'Do not bounce in the stretch.',
        'Breathe deeply.',
        'Stretch both sides equally.'
    ],
    23: [
        'Move slowly and with control.',
        'Do not push into pain.',
        'Focus on increasing range of motion.'
    ],
    24: [
        'Relax your shoulders.',
        'Breathe slowly and deeply.',
        'Focus on each breath.'
    ]
}

for e in Exercise.query.all():
    e.instructions = json.dumps(instructions_dict.get(e.id, ['No instructions available.']))
    e.key_points = json.dumps(key_points_dict.get(e.id, ['No key points available.']))
db.session.commit()
print('Updated instructions and key points for all exercises.') 