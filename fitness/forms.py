from django import forms

from .models import FoodLog


class FoodLogForm(forms.ModelForm):
    class Meta:
        model = FoodLog
        fields = ["food_item", "calories", "meal_type"]
        widgets = {
            "food_item": forms.TextInput(attrs={"class": "form-control"}),
            "calories": forms.NumberInput(attrs={"class": "form-control"}),
            "meal_type": forms.Select(attrs={"class": "form-select"}),
        }
