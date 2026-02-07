"""
Exercise recommendation engine based on BMI and fitness level.
Generates personalized workout plans based on user metrics.
"""

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi):
    """Categorize BMI into standard health categories"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def get_recommended_exercises(bmi, goal="general_fitness"):
    """
    Get personalized exercise recommendations based on BMI and fitness goal.
    Returns a weekly workout plan with exercises, reps, and frequency.
    """
    
    if bmi < 18.5:  # Underweight
        return {
            "category": "Underweight",
            "focus": "Strength Building & Weight Gain",
            "weekly_plan": [
                {
                    "day": "Monday",
                    "focus": "Upper Body Strength",
                    "exercises": [
                        {"name": "Push-ups", "sets": 3, "reps": "10-15", "duration": "rest as needed"},
                        {"name": "Dumbbell Bench Press", "sets": 3, "reps": "8-12", "duration": "rest 60-90s"},
                        {"name": "Rows", "sets": 3, "reps": "10-15", "duration": "rest 60s"},
                    ]
                },
                {
                    "day": "Tuesday",
                    "focus": "Light Cardio & Core",
                    "exercises": [
                        {"name": "Walking", "sets": 1, "reps": "N/A", "duration": "20-30 minutes"},
                        {"name": "Planks", "sets": 3, "reps": "20-30 seconds", "duration": "rest 45s"},
                    ]
                },
                {
                    "day": "Wednesday",
                    "focus": "Lower Body Strength",
                    "exercises": [
                        {"name": "Squats", "sets": 3, "reps": "12-15", "duration": "rest 60-90s"},
                        {"name": "Lunges", "sets": 3, "reps": "10 per leg", "duration": "rest 60s"},
                        {"name": "Calf Raises", "sets": 3, "reps": "15-20", "duration": "rest 45s"},
                    ]
                },
                {
                    "day": "Thursday",
                    "focus": "Rest or Active Recovery",
                    "exercises": [
                        {"name": "Stretching", "sets": 1, "reps": "N/A", "duration": "15-20 minutes"},
                    ]
                },
                {
                    "day": "Friday",
                    "focus": "Full Body Strength",
                    "exercises": [
                        {"name": "Deadlifts", "sets": 3, "reps": "6-10", "duration": "rest 2-3 min"},
                        {"name": "Push-ups", "sets": 3, "reps": "10-15", "duration": "rest 60s"},
                        {"name": "Rows", "sets": 3, "reps": "10-12", "duration": "rest 60s"},
                    ]
                },
                {
                    "day": "Saturday & Sunday",
                    "focus": "Rest Days",
                    "exercises": [
                        {"name": "Light walking or yoga", "sets": 1, "reps": "N/A", "duration": "optional"},
                    ]
                },
            ],
            "nutrition_focus": "High protein intake (1.6-2.2g per kg body weight)",
            "weekly_frequency": "4-5 sessions"
        }
    
    elif bmi < 25:  # Normal Weight
        return {
            "category": "Normal Weight",
            "focus": "Overall Fitness & Performance",
            "weekly_plan": [
                {
                    "day": "Monday",
                    "focus": "Cardio & Speed Work",
                    "exercises": [
                        {"name": "Running", "sets": 1, "reps": "N/A", "duration": "30-40 minutes"},
                        {"name": "Sprints", "sets": 5, "reps": "100m", "duration": "rest 90s"},
                    ]
                },
                {
                    "day": "Tuesday",
                    "focus": "Strength Training",
                    "exercises": [
                        {"name": "Squats", "sets": 4, "reps": "8-10", "duration": "rest 90-120s"},
                        {"name": "Bench Press", "sets": 4, "reps": "8-10", "duration": "rest 90-120s"},
                        {"name": "Rows", "sets": 4, "reps": "8-10", "duration": "rest 90-120s"},
                    ]
                },
                {
                    "day": "Wednesday",
                    "focus": "HIIT & Core",
                    "exercises": [
                        {"name": "Burpees", "sets": 5, "reps": "15", "duration": "rest 60s"},
                        {"name": "Mountain Climbers", "sets": 5, "reps": "20", "duration": "rest 45s"},
                        {"name": "Plank Variations", "sets": 3, "reps": "45 seconds", "duration": "rest 45s"},
                    ]
                },
                {
                    "day": "Thursday",
                    "focus": "Recovery & Flexibility",
                    "exercises": [
                        {"name": "Yoga", "sets": 1, "reps": "N/A", "duration": "45-60 minutes"},
                    ]
                },
                {
                    "day": "Friday",
                    "focus": "Mixed Training",
                    "exercises": [
                        {"name": "Running with intervals", "sets": 1, "reps": "N/A", "duration": "30-40 minutes"},
                        {"name": "Core strengthening", "sets": 3, "reps": "varied", "duration": "15 minutes"},
                    ]
                },
                {
                    "day": "Saturday",
                    "focus": "Long Run or Sports Activity",
                    "exercises": [
                        {"name": "Long run or recreational sports", "sets": 1, "reps": "N/A", "duration": "45-60 minutes"},
                    ]
                },
                {
                    "day": "Sunday",
                    "focus": "Rest Day",
                    "exercises": [
                        {"name": "Light stretching", "sets": 1, "reps": "N/A", "duration": "optional"},
                    ]
                },
            ],
            "nutrition_focus": "Balanced macronutrients: 40% carbs, 30% protein, 30% fats",
            "weekly_frequency": "5-6 sessions"
        }
    
    elif bmi < 30:  # Overweight
        return {
            "category": "Overweight",
            "focus": "Weight Loss & Endurance Building",
            "weekly_plan": [
                {
                    "day": "Monday",
                    "focus": "Low-Impact Cardio",
                    "exercises": [
                        {"name": "Brisk Walking", "sets": 1, "reps": "N/A", "duration": "30-45 minutes"},
                    ]
                },
                {
                    "day": "Tuesday",
                    "focus": "Strength Training (Light)",
                    "exercises": [
                        {"name": "Bodyweight Squats", "sets": 3, "reps": "15-20", "duration": "rest 60s"},
                        {"name": "Push-ups (modified)", "sets": 3, "reps": "8-12", "duration": "rest 60s"},
                        {"name": "Rows (light weights)", "sets": 3, "reps": "12-15", "duration": "rest 60s"},
                    ]
                },
                {
                    "day": "Wednesday",
                    "focus": "Moderate Cardio",
                    "exercises": [
                        {"name": "Elliptical or Cycling", "sets": 1, "reps": "N/A", "duration": "30-40 minutes"},
                    ]
                },
                {
                    "day": "Thursday",
                    "focus": "Active Recovery",
                    "exercises": [
                        {"name": "Swimming or water aerobics", "sets": 1, "reps": "N/A", "duration": "30 minutes"},
                    ]
                },
                {
                    "day": "Friday",
                    "focus": "Circuit Training",
                    "exercises": [
                        {"name": "Burpees (modified)", "sets": 4, "reps": "10", "duration": "rest 60s"},
                        {"name": "Jumping jacks", "sets": 4, "reps": "20", "duration": "rest 45s"},
                        {"name": "Step-ups", "sets": 3, "reps": "15 per leg", "duration": "rest 60s"},
                    ]
                },
                {
                    "day": "Saturday",
                    "focus": "Extended Cardio",
                    "exercises": [
                        {"name": "Jogging or brisk walking", "sets": 1, "reps": "N/A", "duration": "40-50 minutes"},
                    ]
                },
                {
                    "day": "Sunday",
                    "focus": "Rest Day",
                    "exercises": [
                        {"name": "Stretching and mobility work", "sets": 1, "reps": "N/A", "duration": "15-20 minutes"},
                    ]
                },
            ],
            "nutrition_focus": "Caloric deficit with emphasis on whole foods, reduce processed items",
            "weekly_frequency": "5-6 sessions, focus on consistency"
        }
    
    else:  # Obese (BMI >= 30)
        return {
            "category": "Obese",
            "focus": "Gradual Weight Loss & Building Fitness Habits",
            "weekly_plan": [
                {
                    "day": "Monday",
                    "focus": "Walking Foundation",
                    "exercises": [
                        {"name": "Walking", "sets": 1, "reps": "N/A", "duration": "20-30 minutes, leisurely pace"},
                    ]
                },
                {
                    "day": "Tuesday",
                    "focus": "Strength Basics",
                    "exercises": [
                        {"name": "Bodyweight Squats", "sets": 2, "reps": "10-15", "duration": "rest 90s"},
                        {"name": "Wall Push-ups", "sets": 2, "reps": "10-15", "duration": "rest 90s"},
                    ]
                },
                {
                    "day": "Wednesday",
                    "focus": "Walking",
                    "exercises": [
                        {"name": "Walking", "sets": 1, "reps": "N/A", "duration": "20-30 minutes"},
                    ]
                },
                {
                    "day": "Thursday",
                    "focus": "Flexibility & Mobility",
                    "exercises": [
                        {"name": "Gentle Stretching", "sets": 1, "reps": "N/A", "duration": "20 minutes"},
                    ]
                },
                {
                    "day": "Friday",
                    "focus": "Strength Basics",
                    "exercises": [
                        {"name": "Bodyweight Squats", "sets": 2, "reps": "10-15", "duration": "rest 90s"},
                        {"name": "Incline Push-ups (on bench)", "sets": 2, "reps": "8-12", "duration": "rest 90s"},
                        {"name": "Step-ups", "sets": 2, "reps": "10 per leg", "duration": "rest 90s"},
                    ]
                },
                {
                    "day": "Saturday",
                    "focus": "Extended Walking",
                    "exercises": [
                        {"name": "Walking (can split into two sessions)", "sets": 1, "reps": "N/A", "duration": "30-40 minutes"},
                    ]
                },
                {
                    "day": "Sunday",
                    "focus": "Rest & Recovery",
                    "exercises": [
                        {"name": "Light stretching", "sets": 1, "reps": "N/A", "duration": "optional 10-15 minutes"},
                    ]
                },
            ],
            "nutrition_focus": "Consult a nutritionist; focus on sustainable dietary changes, portion control",
            "weekly_frequency": "4-5 sessions, emphasis on building habit",
            "important_notes": [
                "Start slowly and progress gradually to avoid injury",
                "Consult a doctor before starting this program",
                "Focus on consistency over intensity",
                "Consider working with a personal trainer for form and motivation"
            ]
        }


def generate_exercise_plan(weight_kg, height_cm, goal="general_fitness"):
    """
    Generate a complete personalized exercise plan based on user metrics.
    
    Args:
        weight_kg: User weight in kilograms
        height_cm: User height in centimeters
        goal: Fitness goal (general_fitness, weight_loss, strength_building, etc.)
    
    Returns:
        Dictionary containing BMI, category, and personalized weekly plan
    """
    bmi = calculate_bmi(weight_kg, height_cm)
    category = get_bmi_category(bmi)
    plan = get_recommended_exercises(bmi, goal)
    
    return {
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "bmi": bmi,
        "category": category,
        "plan": plan,
        "disclaimer": "These recommendations are general guidelines. Consult a healthcare provider before starting any new exercise program."
    }
