import time
from datetime import datetime
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        with open("requests.log", "a") as log_file:
            log_file.write(log_entry)
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if 18 < current_hour < 21:
            return self.get_response(request)
        return HttpResponseForbidden(
            "Access denied. Chat is available between 6PM and 9PM."
        )

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_times = {}

    def __call__(self, request):
        if request.method == "POST":
            ip = self.get_client_ip(request)
            now = time.time()
            self.message_times.setdefault(ip, [])
            self.message_times[ip] = [t for t in self.message_times[ip] if now - t < 60]

            if len(self.message_times[ip]) >= 5:
                return HttpResponseForbidden("Rate limit exceeded. Try again later.")

            self.message_times[ip].append(now)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return (
            x_forwarded_for.split(",")[0]
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/chats/protected/"):
            user = request.user
            if not user.is_authenticated or not (
                user.is_staff or user.groups.filter(name__in=["moderator"]).exists()
            ):
                return HttpResponseForbidden(
                    "You do not have permission to access this resource."
                )
        return self.get_response(request)
