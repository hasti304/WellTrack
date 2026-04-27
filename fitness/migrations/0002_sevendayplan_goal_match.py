# Generated manually for goal-match scoring

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fitness", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sevendayplan",
            name="goal_match_breakdown",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="sevendayplan",
            name="goal_match_score",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
