import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from argus.quiz import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

websocket_application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # Handle traditional HTTP requests
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
