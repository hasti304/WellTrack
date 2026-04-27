from django.conf import settings
from django.db import models


class FoodLog(models.Model):
    MEAL_BREAKFAST = "breakfast"
    MEAL_LUNCH = "lunch"
    MEAL_DINNER = "dinner"
    MEAL_SNACK = "snack"
    MEAL_CHOICES = [
        (MEAL_BREAKFAST, "Breakfast"),
        (MEAL_LUNCH, "Lunch"),
        (MEAL_DINNER, "Dinner"),
        (MEAL_SNACK, "Snack"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_logs")
    food_item = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, default=MEAL_SNACK)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} — {self.food_item}"


class Exercise(models.Model):
    CAT_CARDIO = "cardio"
    CAT_STRENGTH = "strength"
    CAT_YOGA = "yoga"
    CAT_STRETCHING = "stretching"
    CAT_OTHER = "other"
    CATEGORY_CHOICES = [
        (CAT_CARDIO, "Cardio"),
        (CAT_STRENGTH, "Strength"),
        (CAT_YOGA, "Yoga"),
        (CAT_STRETCHING, "Stretching"),
        (CAT_OTHER, "Other"),
    ]

    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="exercises/images/", blank=True, null=True)
    instruction_gif = models.ImageField(upload_to="exercises/gifs/", blank=True, null=True)
    duration_minutes = models.PositiveSmallIntegerField(default=10)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CAT_OTHER)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CompletedExercise(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="completed_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="completions")
    completed_at = models.DateTimeField(auto_now_add=True)
    repeat_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.user} completed {self.exercise.name}"


class ChatMessage(models.Model):
    SENDER_USER = "user"
    SENDER_AI = "ai"
    SENDER_CHOICES = [(SENDER_USER, "User"), (SENDER_AI, "AI")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class SmartCoachChat(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES = [(ROLE_USER, "User"), (ROLE_ASSISTANT, "Assistant")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="smart_coach_chats")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class SevenDayPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seven_day_plans")
    plan_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Plan for {self.user} @ {self.created_at}"
