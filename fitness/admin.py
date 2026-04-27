from django.contrib import admin

from .models import (
    ChatMessage,
    CompletedExercise,
    Exercise,
    SevenDayPlan,
    SmartCoachChat,
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "duration_minutes")
    list_filter = ("category",)


@admin.register(CompletedExercise)
class CompletedExerciseAdmin(admin.ModelAdmin):
    list_display = ("user", "exercise", "completed_at", "repeat_count")
    list_filter = ("completed_at",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "sender", "created_at")
    list_filter = ("sender", "created_at")


@admin.register(SmartCoachChat)
class SmartCoachChatAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at")
    list_filter = ("role", "created_at")


@admin.register(SevenDayPlan)
class SevenDayPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    list_filter = ("created_at",)
