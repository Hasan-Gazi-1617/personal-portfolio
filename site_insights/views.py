from datetime import timedelta
import re
import uuid
from urllib.parse import urlparse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import DailyVisitor, PageView, SiteEvent, ModuleUsage

MODULE_RE = re.compile(r'^[a-z0-9][a-z0-9_-]{0,79}$')


@require_POST
def track_module(request):
    raw_id = request.COOKIES.get('portfolio_visitor_id', '')
    try:
        visitor_id = uuid.UUID(raw_id)
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({'ok': False, 'error': 'visitor cookie missing'}, status=400)
    module = request.POST.get('module', '').strip().lower()
    if not MODULE_RE.fullmatch(module) or module in {'maincontent', 'newsletter'}:
        return JsonResponse({'ok': False}, status=400)
    ModuleUsage.objects.get_or_create(visitor_key=visitor_id, visit_date=timezone.localdate(), module=module)
    return JsonResponse({'ok': True})


@require_POST
def track_event(request):
    event = request.POST.get('event', '')
    if event not in {'cv_download', 'project_click'}:
        return JsonResponse({'ok': False}, status=400)
    path = urlparse(request.POST.get('path', '')).path[:300]
    SiteEvent.objects.create(event=event, path=path)
    return JsonResponse({'ok': True})


@staff_member_required
def dashboard(request):
    today = timezone.localdate()
    start = today - timedelta(days=29)
    date_range = {'visit_date__range': (start, today)}
    visitors = DailyVisitor.objects.filter(**date_range).values('visit_date').annotate(total=Count('id')).order_by('visit_date')
    pageviews = PageView.objects.filter(**date_range).values('visit_date').annotate(total=Count('id')).order_by('visit_date')
    top_pages = PageView.objects.filter(**date_range).values('path').annotate(total=Count('id')).order_by('-total')[:10]
    module_totals = ModuleUsage.objects.filter(**date_range).values('module').annotate(total=Count('id')).order_by('-total')
    daily_modules = ModuleUsage.objects.filter(**date_range).values('visit_date', 'module').annotate(total=Count('id')).order_by('-visit_date', 'module')
    events = SiteEvent.objects.filter(created_at__date__gte=start).values('event').annotate(total=Count('id'))
    return render(request, 'admin/site_insights/dashboard.html', {
        'title': 'Portfolio Analytics', 'today': today, 'start': start,
        'visitors': visitors, 'pageviews': pageviews, 'top_pages': top_pages,
        'module_totals': module_totals, 'daily_modules': daily_modules, 'events': events,
        'total_visitors': DailyVisitor.objects.filter(**date_range).count(),
        'total_pageviews': PageView.objects.filter(**date_range).count(),
    })
