from django.db import models

from argus.users.models import User


class QuizSession(models.Model):
    SESSION_STATUS = [
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("pending", "Pending"),
        ("in progress", "In Progress"),
    ]

    session_name = models.CharField()
    session_id = models.IntegerField(unique=True)
    is_active = models.BooleanField(null=False, default=True)
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS,
        default="pending",
    )


class QuizScore(models.Model):
    quiz_session = models.ForeignKey(
        to=QuizSession,
        related_name="session",
        on_delete=models.CASCADE,
    )
    username = models.CharField(blank=True, null=True)
    score = models.IntegerField(default=0, null=False)
    max_score = models.IntegerField(null=False)
    current_question = models.IntegerField(null=False, default=0)
    user = models.ForeignKey(
        to=User,
        related_name="answerer",
        null=True,
        on_delete=models.CASCADE,
    )
