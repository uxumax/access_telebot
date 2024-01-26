import re
from django.http import HttpResponseForbidden
from access_telebot.settings import ALLOWED_HOSTS_REGEX


class AllowedHostsRegexMiddleware:
    # Определяем паттерны как список строк
    patterns = ALLOWED_HOSTS_REGEX

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]

        # Проверяем соответствие хоста каждому паттерну
        if not any(re.compile(pattern).match(host) for pattern in self.patterns):
            return HttpResponseForbidden("Access Denied")

        response = self.get_response(request)
        return response
