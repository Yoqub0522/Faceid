# attendance/middleware.py (YANGI)
import time
from django.conf import settings
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}

    def __call__(self, request):
        # Faqat recognize_api uchun rate limit
        if request.path == '/attendance/api/recognize/':
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            current_time = time.time()

            # So'rovlar tarixini tozalash (60 soniyadan oldingilari)
            self.requests[ip] = [t for t in self.requests.get(ip, [])
                                 if current_time - t < 60]

            # Daqiqaiga 15 ta so'rov cheklovi
            if len(self.requests[ip]) >= 15:
                logger.warning(f"Rate limit: {ip}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Juda koʻp soʻrov. Iltimos, 1 daqiqa kuting.'
                }, status=429)

            self.requests[ip].append(current_time)

        return self.get_response(request)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Xavfsizlik headerlarini qo'shish
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # CSP header (soddalashtirilgan)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: blob:; "
            "media-src 'self' blob:;"
        )

        return response