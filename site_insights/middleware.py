import re
import uuid
from urllib.parse import urlparse
from django.db import IntegrityError
from django.utils import timezone
from .models import DailyVisitor, PageView

BOT_RE = re.compile(r'bot|crawler|spider|preview|uptime|monitor', re.I)


def _device(user_agent):
    ua = (user_agent or '').lower()
    if any(x in ua for x in ('ipad','tablet')): return 'tablet'
    if any(x in ua for x in ('mobile','android','iphone')): return 'mobile'
    if ua: return 'desktop'
    return 'other'


class PublicPageAnalyticsMiddleware:
    """Counts public HTML GETs without storing IP addresses or full user agents."""
    cookie_name = 'portfolio_visitor_id'

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)
        if (request.method != 'GET' or request.path.startswith(('/admin/','/static/','/media/','/analytics/'))
                or getattr(request.user, 'is_staff', False)
                or request.session.get('owner_access')):
            return response
        content_type = response.get('Content-Type','')
        ua = request.META.get('HTTP_USER_AGENT','')
        if response.status_code >= 400 or 'text/html' not in content_type or BOT_RE.search(ua):
            return response
        raw_cookie = request.COOKIES.get(self.cookie_name)
        try:
            visitor_id = uuid.UUID(raw_cookie) if raw_cookie else uuid.uuid4()
            valid_cookie = bool(raw_cookie)
        except (ValueError, TypeError, AttributeError):
            visitor_id = uuid.uuid4()
            valid_cookie = False
        referer = request.META.get('HTTP_REFERER','')
        host = urlparse(referer).hostname or ''
        source = host[:120] if host and host != request.get_host().split(':')[0] else ('Direct' if not host else '')
        day = timezone.localdate()
        device = _device(ua)
        try:
            DailyVisitor.objects.get_or_create(visitor_key=visitor_id, visit_date=day, defaults={
                'first_path': request.path[:300], 'source': source, 'device': device,
            })
            PageView.objects.create(visit_date=day, path=request.path[:300], source=source, device=device)
        except Exception:
            # Analytics must never make the public portfolio unavailable.
            pass
        if not valid_cookie:
            response.set_cookie(self.cookie_name, str(visitor_id), max_age=31536000,
                httponly=True, secure=request.is_secure(), samesite='Lax')
        return response
