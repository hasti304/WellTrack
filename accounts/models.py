from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="kg")
    height = models.PositiveSmallIntegerField(null=True, blank=True, help_text="cm")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    waist = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="cm")
    neck = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="cm")
    hip = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="cm")
    fitness_goals = models.TextField(blank=True)
    goal_calories = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional daily calorie target (used for 7-day plan scoring).",
    )
    goal_protein_g = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Optional daily protein target in grams (plan scoring).",
    )
    goal_workouts_per_week = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Optional training days per week, 1–7 (plan scoring).",
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
