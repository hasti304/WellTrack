import json
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import FoodLogForm
from .models import (
    ChatMessage,
    CompletedExercise,
    Exercise,
    FoodLog,
    SevenDayPlan,
    SmartCoachChat,
)
from .llm import chat_completion
from .plan_goal_match import compute_goal_match
from .rag import retrieve_context
from .utils import calculate_bmi, estimated_calories_burned, navy_body_fat_percent


def _openai_chat(messages):
    return chat_completion(messages)


def home(request):
    hero_url = None
    key = getattr(settings, "UNSPLASH_ACCESS_KEY", "")
    if key:
        try:
            r = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": "health", "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {key}"},
                timeout=8,
            )
            if r.ok:
                data = r.json()
                hero_url = data.get("urls", {}).get("regular")
        except requests.RequestException:
            hero_url = None
    return render(request, "fitness/home.html", {"hero_url": hero_url})


@login_required
def dashboard(request):
    profile = request.user.profile
    bmi_value, bmi_label = calculate_bmi(profile.weight, profile.height)
    body_fat = navy_body_fat_percent(
        profile.gender,
        profile.height,
        profile.waist,
        profile.neck,
        profile.hip,
    )

    recent_meals = FoodLog.objects.filter(user=request.user).order_by("-timestamp")[:8]
    recent_completions = (
        CompletedExercise.objects.filter(user=request.user)
        .select_related("exercise")
        .order_by("-completed_at")[:10]
    )

    meal_calories = sum(m.calories for m in recent_meals)
    burn_total = sum(
        estimated_calories_burned(c.exercise.duration_minutes, c.repeat_count)
        for c in recent_completions
    )

    week_ago = timezone.now() - timedelta(days=7)
    week_meals_agg = FoodLog.objects.filter(
        user=request.user, timestamp__gte=week_ago
    ).aggregate(total=Sum("calories"), n=Count("id"))
    meals_week_calories = week_meals_agg["total"] or 0
    meals_week_count = week_meals_agg["n"] or 0

    week_completions = list(
        CompletedExercise.objects.filter(user=request.user, completed_at__gte=week_ago).select_related(
            "exercise"
        )
    )
    burn_week_total = sum(
        estimated_calories_burned(c.exercise.duration_minutes, c.repeat_count)
        for c in week_completions
    )
    workouts_week_count = len(week_completions)

    food_form = FoodLogForm()

    return render(
        request,
        "fitness/dashboard.html",
        {
            "profile": profile,
            "bmi_value": bmi_value,
            "bmi_label": bmi_label,
            "body_fat": body_fat,
            "recent_meals": recent_meals,
            "recent_completions": recent_completions,
            "meal_calories": meal_calories,
            "burn_total": burn_total,
            "meals_week_calories": meals_week_calories,
            "meals_week_count": meals_week_count,
            "burn_week_total": burn_week_total,
            "workouts_week_count": workouts_week_count,
            "food_form": food_form,
        },
    )


def exercise_list(request):
    category = request.GET.get("category", "")
    qs = Exercise.objects.all()
    if category:
        qs = qs.filter(category=category)

    completed = []
    remaining = []
    if request.user.is_authenticated:
        prefetch = Prefetch(
            "completions",
            queryset=CompletedExercise.objects.filter(user=request.user).order_by(
                "-completed_at"
            ),
            to_attr="user_completions",
        )
        qs = qs.prefetch_related(prefetch)
        exercises = list(qs)
        for ex in exercises:
            ucomps = getattr(ex, "user_completions", [])
            if ucomps:
                c = ucomps[0]
                completed.append({"exercise": ex, "repeat_count": c.repeat_count, "completion_id": c.id})
            else:
                remaining.append(ex)
    else:
        remaining = list(qs)

    ctx = {
        "completed_rows": completed,
        "remaining_exercises": remaining,
        "category": category,
        "categories": Exercise.CATEGORY_CHOICES,
    }

    if request.headers.get("X-Requested-With") == "fetch" or request.GET.get("partial"):
        return render(request, "fitness/partials/exercise_grid.html", ctx)
    return render(request, "fitness/exercise_list.html", ctx)


@login_required
@require_POST
def exercise_complete(request, pk):
    ex = get_object_or_404(Exercise, pk=pk)
    CompletedExercise.objects.create(user=request.user, exercise=ex, repeat_count=0)
    return redirect("exercise_list")


@login_required
@require_POST
def exercise_repeat(request, pk):
    ex = get_object_or_404(Exercise, pk=pk)
    latest = (
        CompletedExercise.objects.filter(user=request.user, exercise=ex)
        .order_by("-completed_at")
        .first()
    )
    if latest:
        latest.repeat_count += 1
        latest.save(update_fields=["repeat_count"])
    else:
        CompletedExercise.objects.create(user=request.user, exercise=ex, repeat_count=1)
    return redirect("exercise_list")


@login_required
def food_log_page(request):
    if request.method == "POST":
        form = FoodLogForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect("food_log")
    else:
        form = FoodLogForm()
    logs = FoodLog.objects.filter(user=request.user).order_by("-timestamp")[:50]
    return render(
        request,
        "fitness/food_log.html",
        {"form": form, "logs": logs},
    )


@login_required
def chatbot_page(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")[:200]
    return render(request, "fitness/chatbot.html", {"messages": messages})


@login_required
@require_POST
def api_chatbot(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    text = (payload.get("message") or "").strip()
    if not text:
        return JsonResponse({"error": "Empty message"}, status=400)

    ChatMessage.objects.create(user=request.user, sender=ChatMessage.SENDER_USER, content=text)
    history = list(
        ChatMessage.objects.filter(user=request.user).order_by("created_at")
    )[-20:]
    msgs = []
    for m in history:
        role = "user" if m.sender == ChatMessage.SENDER_USER else "assistant"
        msgs.append({"role": role, "content": m.content})

    reply, err = _openai_chat(msgs)
    if err:
        return JsonResponse({"error": err}, status=502)
    ChatMessage.objects.create(user=request.user, sender=ChatMessage.SENDER_AI, content=reply)
    return JsonResponse({"reply": reply})


@login_required
def smart_coach(request):
    goals = (request.user.profile.fitness_goals or "").strip()
    if not goals:
        return redirect("accounts_profile")
    return render(request, "fitness/smart_coach.html")


@login_required
@require_POST
def api_smart_coach(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    text = (payload.get("message") or "").strip()
    if not text:
        return JsonResponse({"error": "Empty message"}, status=400)

    profile = request.user.profile
    goals = profile.fitness_goals or "General wellness"
    samples = list(Exercise.objects.order_by("?")[:5].values_list("name", flat=True))
    sample_txt = ", ".join(samples) if samples else "bodyweight moves, walking, stretching"

    SmartCoachChat.objects.create(user=request.user, role=SmartCoachChat.ROLE_USER, content=text)
    context_chunks = retrieve_context(text)
    citations = [c.source_id for c in context_chunks]
    rag_context = "\n\n".join(
        f"[{idx+1}] Source {chunk.source_id}: {chunk.text}"
        for idx, chunk in enumerate(context_chunks)
    )
    rag_max = getattr(settings, "SMART_COACH_RAG_CONTEXT_MAX_CHARS", 10000)
    if len(rag_context) > rag_max:
        rag_context = rag_context[:rag_max].rstrip() + "\n\n[Reference context truncated for length.]"

    history_cap = getattr(settings, "SMART_COACH_MAX_HISTORY_MESSAGES", 16)
    system = (
        "You are a supportive fitness and nutrition coach. "
        "The user's stated goals: "
        f"{goals}. "
        f"Example exercises they might try: {sample_txt}. "
        "Give concise, practical advice. "
        "You will see their recent conversation turns below; stay consistent with prior guidance when appropriate. "
        "If reference context is provided, ground your answer in it and avoid contradicting it."
    )
    if rag_context:
        system += (
            "\n\nReference context (trusted snippets):\n"
            f"{rag_context}\n\n"
            "When these snippets are relevant, cite them inline as [source_id]."
        )
    msgs = [{"role": "system", "content": system}]
    coach_rows = list(
        SmartCoachChat.objects.filter(user=request.user).order_by("created_at")
    )[-history_cap:]
    for row in coach_rows:
        r = "user" if row.role == SmartCoachChat.ROLE_USER else "assistant"
        msgs.append({"role": r, "content": row.content})

    reply, err = _openai_chat(msgs)
    if err:
        return JsonResponse({"error": err}, status=502)
    SmartCoachChat.objects.create(
        user=request.user, role=SmartCoachChat.ROLE_ASSISTANT, content=reply
    )
    return JsonResponse({"reply": reply, "citations": citations})


@login_required
@require_GET
def api_smart_coach_history(request):
    rows = SmartCoachChat.objects.filter(user=request.user).order_by("created_at")[:200]
    data = [{"role": r.role, "content": r.content} for r in rows]
    return JsonResponse({"history": data})


@login_required
def seven_day_plan(request):
    plans = list(SevenDayPlan.objects.filter(user=request.user).order_by("-created_at")[:20])
    to_persist: list[SevenDayPlan] = []
    for p in plans:
        if p.goal_match_score is None and (p.plan_text or "").strip():
            p.refresh_goal_match()
            to_persist.append(p)
    if to_persist:
        SevenDayPlan.objects.bulk_update(to_persist, ["goal_match_score", "goal_match_breakdown"])
    profile = request.user.profile
    pdf_export = {
        "user_display_name": request.user.get_full_name() or request.user.username,
        "fitness_goals": profile.fitness_goals or "",
        "goal_calories": profile.goal_calories,
        "goal_protein_g": profile.goal_protein_g,
        "goal_workouts_per_week": profile.goal_workouts_per_week,
    }
    return render(
        request,
        "fitness/seven_day_plan.html",
        {"plans": plans, "pdf_export": pdf_export},
    )


@login_required
@require_POST
def api_seven_day_plan_generate(request):
    profile = request.user.profile
    goals = (profile.fitness_goals or "").strip()
    if not goals:
        return JsonResponse({"error": "Set fitness goals on your profile first."}, status=400)

    prompt = (
        "Create a 7-day wellness plan in Markdown with headings for each day. "
        "Include workouts, simple meal ideas, and recovery tips. "
        f"User goals: {goals}. "
        f"Age: {profile.age}, weight kg: {profile.weight}, height cm: {profile.height}."
    )
    reply, err = _openai_chat([{"role": "user", "content": prompt}])
    if err:
        return JsonResponse({"error": err}, status=502)
    gm = compute_goal_match(reply or "", profile=profile)
    return JsonResponse({"plan": reply, "goal_match": gm})


@login_required
@require_POST
def api_seven_day_plan_save(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    text = (payload.get("plan_text") or "").strip()
    if not text:
        return JsonResponse({"error": "Empty plan"}, status=400)
    plan = SevenDayPlan(user=request.user, plan_text=text)
    plan.refresh_goal_match()
    plan.save()
    gm = {"score": plan.goal_match_score, "breakdown": plan.goal_match_breakdown}
    return JsonResponse(
        {"id": plan.id, "created_at": plan.created_at.isoformat(), "goal_match": gm}
    )


@login_required
@require_POST
def dashboard_quick_food(request):
    form = FoodLogForm(request.POST)
    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
    return redirect("dashboard")
