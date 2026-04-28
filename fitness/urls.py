from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("exercise-log/<int:pk>/", views.exercise_complete, name="exercise_complete"),
    path("exercise/repeat/<int:pk>/", views.exercise_repeat, name="exercise_repeat"),
    path("food-log/", views.food_log_page, name="food_log"),
    path("dashboard/quick-food/", views.dashboard_quick_food, name="dashboard_quick_food"),
    path("chatbot/", views.chatbot_page, name="chatbot"),
    path("api/chatbot/", views.api_chatbot, name="api_chatbot"),
    path("smart-coach/", views.smart_coach, name="smart_coach"),
    path("api/smart-coach/", views.api_smart_coach, name="api_smart_coach"),
    path("api/smart-coach/history/", views.api_smart_coach_history, name="api_smart_coach_history"),
    path("seven-day-plan/", views.seven_day_plan, name="seven_day_plan"),
    path(
        "api/seven-day-plan/generate/",
        views.api_seven_day_plan_generate,
        name="api_seven_day_plan_generate",
    ),
    path(
        "api/seven-day-plan/save/",
        views.api_seven_day_plan_save,
        name="api_seven_day_plan_save",
    ),
]
