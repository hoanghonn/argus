# Create your views here.
from random import randint

from django.http import QueryDict
from django.shortcuts import redirect, render
from django.urls import reverse

from argus.chat.constant import quiz_list
from argus.chat.models import QuizScore, QuizSession


def index(request):
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        quiz_session = QuizSession.objects.create(
            session_name=room_name, session_id=randint(10**5, (10**6) - 1)
        )
        base_url = reverse(
            "room", args=[quiz_session.session_id]
        )  # Assuming 'room' is the name of the URL pattern

        # Define your query parameters
        query_params = QueryDict(mutable=True)
        query_params["is_admin"] = True

        url = f"{base_url}?{query_params.urlencode()}"
        return redirect(url)
    quiz_sessions = QuizSession.objects.filter(is_active=True).all()
    return render(request, "pages/chat/index.html", {"active_sessions": quiz_sessions})


def room(request, session_id):
    is_admin = request.GET.get("is_admin")
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
        return render(
            request,
            "pages/chat/room.html",
            {
                "room_name": quiz_session.session_name,
                "room_id": quiz_session.session_id,
                "quiz_list": quiz_list,
                "is_admin": is_admin,
                "user_name": user_name,
                "status": quiz_session.status,
            },
        )
    except QuizSession.DoesNotExist:
        return render(request, "pages/chat/room.html", {"error": "inactive"})


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
            },
        )
    except QuizSession.DoesNotExist:
        return render(request, "pages/chat/room.html", {"error": "inactive"})
