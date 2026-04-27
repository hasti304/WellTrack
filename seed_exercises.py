"""
Bulk-create Exercise rows. Run after Django is configured and migrated.

Idempotent only if you clear exercises first; this script does not check duplicates.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "welltrack.settings")

import django  # noqa: E402

django.setup()

from fitness.models import Exercise  # noqa: E402


SAMPLES = [
    ("Brisk walk", Exercise.CAT_CARDIO, 30, "Easy cardio to start the day."),
    ("Jump rope", Exercise.CAT_CARDIO, 15, "Short bursts with rest as needed."),
    ("Stationary bike", Exercise.CAT_CARDIO, 25, "Moderate resistance."),
    ("Squats", Exercise.CAT_STRENGTH, 12, "Keep chest up, knees track toes."),
    ("Push-ups", Exercise.CAT_STRENGTH, 10, "Modify on knees if needed."),
    ("Dumbbell rows", Exercise.CAT_STRENGTH, 15, "Hinge at hips, neutral spine."),
    ("Sun salutation", Exercise.CAT_YOGA, 20, "Flow slowly with breath."),
    ("Downward dog hold", Exercise.CAT_YOGA, 5, "Pedal feet to open calves."),
    ("Hamstring stretch", Exercise.CAT_STRETCHING, 8, "Hold without bouncing."),
    ("Hip flexor stretch", Exercise.CAT_STRETCHING, 8, "Tuck pelvis slightly."),
    ("Plank", Exercise.CAT_STRENGTH, 5, "Ribs down, squeeze glutes."),
    ("Burpees", Exercise.CAT_CARDIO, 10, "Step back if impact is too much."),
    ("Yin forward fold", Exercise.CAT_YOGA, 12, "Support knees if tight."),
    ("Shoulder rolls", Exercise.CAT_STRETCHING, 5, "Gentle mobility."),
    ("Walking lunges", Exercise.CAT_STRENGTH, 12, "Short steps, tall torso."),
    ("Breathwork box breathing", Exercise.CAT_OTHER, 6, "4-4-4-4 pattern."),
]


def main():
    for name, cat, minutes, desc in SAMPLES:
        Exercise.objects.create(
            name=name,
            category=cat,
            duration_minutes=minutes,
            description=desc,
        )
    print(f"Created {len(SAMPLES)} exercises.")


if __name__ == "__main__":
    main()
