from time import sleep

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from argus.quiz.constant import quiz_list
from argus.quiz.models import QuizScore, QuizSession


@shared_task
def start_timer(room_group_name, duration, session_id):
    """
    Celery task to handle a countdown timer and send the remaining time to WebSocket clients.
    """
    channel_layer = get_channel_layer()

    for remaining_time in range(duration, 0, -1):
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "timer_update",
                "remaining_time": remaining_time,
            },
        )
        sleep(1)

    # When the timer ends, send a "time up" message
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "timer_ended",
        },
    )
    try:
        quiz_session = QuizSession.objects.get(session_id=session_id)
        quiz_session.is_active = False
        quiz_session.status = "completed"
        quiz_session.save()
        quiz_scores = QuizScore.objects.filter(
            quiz_session=quiz_session,
            current_question__lte=len(quiz_list),
        ).all()
        for score in quiz_scores:
            score.current_question = len(quiz_list) + 1
            score.save()
    except QuizSession.DoesNotExist:
        pass
