from django.contrib.auth.models import User
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
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
