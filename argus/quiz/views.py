from random import randint

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import redirect, render
from django.urls import reverse

from argus.quiz.constant import quiz_list
from argus.quiz.models import QuizScore, QuizSession


def index(request):
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        quiz_session = QuizSession.objects.create(
            session_name=room_name, session_id=randint(10**5, (10**6) - 1)
        )

        return redirect(reverse("monitor", args=[quiz_session.session_id]))
    quiz_sessions = QuizSession.objects.filter(is_active=True).all()
    return render(request, "pages/chat/index.html", {"active_sessions": quiz_sessions})


def room(request, session_id):
    user_name = request.GET.get("user_name")
    try:
        quiz_session = QuizSession.objects.get(session_id=session_id, is_active=True)
        if (
            user_name
            and not QuizScore.objects.filter(
                quiz_session=quiz_session, username=user_name
            ).exists()
        ):
            QuizScore.objects.create(
                quiz_session=quiz_session,
                score=0,
                max_score=len(quiz_list),
                username=user_name,
            )
        print(quiz_session.status)
        if user_name and quiz_session.status == "pending":
            activity_group_name = "session_%s" % session_id
            activity_msg = {
                "type": "update_activity",
                "message": f"{user_name} joined.",
                "question_id": 0,
            }
            ranking = list(
                QuizScore.objects.filter(quiz_session=quiz_session)
                .all()
                .order_by("-score")
                .values("username", "score", "max_score", "current_question")
            )
            if ranking:
                print(ranking)
                activity_msg["ranking"] = ranking
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(activity_group_name, activity_msg)
        return render(
            request,
            "pages/chat/room.html",
            {
                "room_name": quiz_session.session_name,
                "room_id": quiz_session.session_id,
                "quiz_list": quiz_list,
                "user_name": user_name,
                "status": quiz_session.status,
            },
        )
    except QuizSession.DoesNotExist:
        return render(request, "pages/chat/room.html", {"error": "inactive"})


def monitor(request, session_id):
    user_name = request.GET.get("user_name")
    try:
        quiz_session = QuizSession.objects.get(session_id=session_id)
        if (
            user_name
            and not QuizScore.objects.filter(
                quiz_session=quiz_session, username=user_name
            ).exists()
        ):
            QuizScore.objects.create(
                quiz_session=quiz_session,
                score=0,
                max_score=len(quiz_list),
                username=user_name,
            )
        quiz_scores = (
            QuizScore.objects.filter(quiz_session=quiz_session)
            .all()
            .order_by("-score")
            .values("username", "score", "max_score", "current_question")
        )
        print(quiz_scores)
        return render(
            request,
            "pages/chat/monitor.html",
            {
                "room_name": quiz_session.session_name,
                "room_id": quiz_session.session_id,
                "quiz_list": quiz_list,
                "user_name": user_name,
                "status": quiz_session.status,
                "scores": list(quiz_scores),
            },
        )
    except QuizSession.DoesNotExist:
        return render(request, "pages/chat/monitor.html", {"error": "inactive"})


def review(request, session_id):
    try:
        user_name = request.GET.get("user_name")
        quiz_session = QuizSession.objects.get(session_id=session_id)
        quiz_scores = (
            QuizScore.objects.filter(quiz_session=quiz_session)
            .all()
            .order_by("-score")
            .values("username", "score", "max_score")
        )
        my_score = next(
            (
                personal_score.get("score")
                for personal_score in list(quiz_scores)
                if personal_score and personal_score.get("username") == user_name
            ),
            0,
        )
        max_score = next(
            (
                personal_score.get("max_score")
                for personal_score in list(quiz_scores)
                if personal_score and personal_score.get("username") == user_name
            ),
            len(quiz_list),
        )
        return render(
            request,
            "pages/chat/review.html",
            context={
                "score": my_score,
                "max_score": max_score,
                "quiz_list": quiz_list,
                "room_id": quiz_session.session_id,
                "scores": list(quiz_scores),
                "user_name": user_name,
                "status": quiz_session.status,
                "room_name": quiz_session.session_name,
            },
        )
    except QuizSession.DoesNotExist:
        return render(request, "pages/chat/room.html", {"error": "inactive"})
