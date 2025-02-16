from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.utils.timezone import now

class VisitorTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.session_key:
            request.session.save()
        request.session['visited'] = True
