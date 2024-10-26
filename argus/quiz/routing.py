from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/quiz/(?P<room_name>\w+)/timer/$", consumers.TimerConsumer.as_asgi()),
    re_path(r"ws/quiz/(?P<room_name>\w+)/user/$", consumers.UserConsumer.as_asgi()),
    re_path(
        r"ws/quiz/(?P<room_name>\w+)/activity/$", consumers.ActivityConsumer.as_asgi()
    ),
]
