# Generated by Django 5.1.4 on 2024-12-07 17:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="fixture",
            name="graph",
            field=models.JSONField(
                editable=False,
                help_text="The graph of the players in the fixture.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="rank",
            name="delta",
            field=models.IntegerField(
                default=0,
                editable=False,
                help_text="The change in score for the player, computed via the fixture graph.",
            ),
        ),
    ]
