# Manual migration: structured goal targets for plan matching

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="goal_calories",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Optional daily calorie target (used for 7-day plan scoring).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="goal_protein_g",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="Optional daily protein target in grams (plan scoring).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="goal_workouts_per_week",
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text="Optional training days per week, 1–7 (plan scoring).",
                null=True,
            ),
        ),
    ]
