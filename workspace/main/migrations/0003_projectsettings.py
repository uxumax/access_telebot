# Generated by Django 5.0.1 on 2024-01-22 15:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_customer_added_to_attachment_menu_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("telegram_webhook_url", models.URLField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
