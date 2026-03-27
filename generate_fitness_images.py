import os
from PIL import Image, ImageDraw, ImageFont
import sqlite3
import re

# Font paths (update if needed)
MODERN_FONT_PATH = "Montserrat-Bold.ttf"  # Try to use a modern font
FALLBACK_FONT_PATH = "arial.ttf"

# Output directory
OUTPUT_DIR = os.path.join("static", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Image settings
IMG_SIZE = (500, 500)
BG_COLOR = (91, 124, 255)  # #5b7cff

# Subtitle logic (same as before)
def get_subtitle(name, is_workout):
    if is_workout:
        if "yoga" in name.lower():
            return "FLEXIBILITY & BALANCE."
        elif "hiit" in name.lower():
            return "FULL-BODY WORKOUT."
        elif "cardio" in name.lower():
            return "HIGH-ENERGY SESSION."
        elif "core" in name.lower():
            return "CORE WORKOUT."
        elif "strength" in name.lower():
            return "STRENGTH TRAINING."
        elif "mobility" in name.lower():
            return "MOBILITY FLOW."
        elif "tabata" in name.lower():
            return "INTERVAL TRAINING."
        elif "recovery" in name.lower():
            return "RECOVERY FLOW."
        else:
            return "WORKOUT SESSION."
    else:
        if "press" in name.lower() or "curl" in name.lower() or "pull" in name.lower() or "push" in name.lower():
            return "UPPER BODY."
        elif "squat" in name.lower() or "lunge" in name.lower() or "calf" in name.lower() or "leg" in name.lower():
            return "LOWER BODY."
        elif "plank" in name.lower() or "crunch" in name.lower() or "core" in name.lower() or "twist" in name.lower():
            return "CORE EXERCISE."
        elif "stretch" in name.lower() or "mobility" in name.lower():
            return "FLEXIBILITY."
        elif "breath" in name.lower():
            return "BREATHING EXERCISE."
        else:
            return "EXERCISE."

def draw_dumbbell_icon(draw, x, y, scale=1.0):
    """Draw a minimal dumbbell icon at (x, y)."""
    # Bar
    draw.rectangle([x+10*scale, y+18*scale, x+40*scale, y+22*scale], fill=(40,40,60))
    # Left weight
    draw.rectangle([x, y+12*scale, x+10*scale, y+28*scale], fill=(200,200,255))
    # Right weight
    draw.rectangle([x+40*scale, y+12*scale, x+50*scale, y+28*scale], fill=(200,200,255))

def draw_image(main_text, sub_text, filename):
    img = Image.new("RGB", IMG_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(img)
    # Try modern font, fallback to Arial
    try:
        main_font = ImageFont.truetype(MODERN_FONT_PATH, 54)
    except:
        main_font = ImageFont.truetype(FALLBACK_FONT_PATH, 54)
    try:
        sub_font = ImageFont.truetype(FALLBACK_FONT_PATH, 22)
    except:
        sub_font = ImageFont.load_default()
    # Center main text, add soft shadow
    bbox = draw.textbbox((0, 0), main_text, font=main_font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (IMG_SIZE[0] - w) // 2
    y = 170
    # Soft shadow
    for dx, dy in [(-2,2), (2,2), (2,-2), (-2,-2), (0,3), (3,0), (0,-3), (-3,0)]:
        draw.text((x+dx, y+dy), main_text, font=main_font, fill=(0,0,0,90))
    # Main text
    draw.text((x, y), main_text, font=main_font, fill=(255,255,255))
    # Subtitle
    bbox2 = draw.textbbox((0, 0), sub_text, font=sub_font)
    w2 = bbox2[2] - bbox2[0]
    h2 = bbox2[3] - bbox2[1]
    x2 = (IMG_SIZE[0] - w2) // 2
    y2 = y + h + 30
    draw.text((x2, y2), sub_text, font=sub_font, fill=(30,30,60))
    # Dumbbell icon in bottom right
    draw_dumbbell_icon(draw, IMG_SIZE[0]-70, IMG_SIZE[1]-70, scale=1.2)
    # Save
    img.save(os.path.join(OUTPUT_DIR, filename))

def sanitize_filename(name):
    # Lowercase, strip, remove special chars except spaces and hyphens, then collapse multiple spaces
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\- ]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name + ".jpg"

# Connect to DB and get names
conn = sqlite3.connect("fitroom_fresh.db")
c = conn.cursor()
workouts = [row[0] for row in c.execute("SELECT name FROM workout")]
exercises = [row[0] for row in c.execute("SELECT name FROM exercise")]
diet_plans = [row[0] for row in c.execute("SELECT name FROM diet_plan")]
workout_plans = [row[0] for row in c.execute("SELECT name FROM workout_plan")]
conn.close()

# Generate images for workouts
for name in workouts:
    filename = sanitize_filename(name)
    subtitle = get_subtitle(name, is_workout=True)
    draw_image(name, subtitle, filename)

# Generate images for exercises
for name in exercises:
    filename = sanitize_filename(name)
    subtitle = get_subtitle(name, is_workout=False)
    draw_image(name, subtitle, filename)

# Generate images for diet plans
for name in diet_plans:
    filename = sanitize_filename(name)
    subtitle = "DIET PLAN."
    print(f"Diet plan: '{name}' -> '{filename}'")
    draw_image(name, subtitle, filename)

# Generate images for workout plans
for name in workout_plans:
    filename = sanitize_filename(name)
    subtitle = "WORKOUT PLAN."
    print(f"Workout plan: '{name}' -> '{filename}'")
    draw_image(name, subtitle, filename)

print(f"Generated {len(workouts) + len(exercises) + len(diet_plans) + len(workout_plans)} images in {OUTPUT_DIR}") 