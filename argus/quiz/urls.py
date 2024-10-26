from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="quiz_index"),
    path("<str:session_id>/", views.room, name="room"),
    path("<str:session_id>/review/", views.review, name="review"),
    path("<str:session_id>/monitor/", views.monitor, name="monitor"),
]
