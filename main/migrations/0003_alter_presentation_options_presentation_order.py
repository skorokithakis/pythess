# Generated by Django 5.1.5 on 2025-02-23 01:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_alter_person_options_remove_event_presentations_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="presentation",
            options={"ordering": ["order"]},
        ),
        migrations.AddField(
            model_name="presentation",
            name="order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
