from datetime import timedelta
import re
import uuid
from urllib.parse import urlparse
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import DailyVisitor, PageView, SiteEvent, ModuleUsage

MODULE_RE = re.compile(r'^[a-z0-9][a-z0-9_-]{0,79}$')


def public_dashboard(request):
    """Analytics is private and available only inside the owner's Admin View."""
    if request.session.get('owner_access'):
        return redirect('site_insights:owner_dashboard')
    return redirect('owner_login')


def owner_dashboard(request):
    """Private owner analytics dashboard, protected by the Admin View session."""
    if not request.session.get('owner_access'):
        return redirect('owner_login')

    today = timezone.localdate()
    start = today - timedelta(days=29)
    date_range = {'visit_date__range': (start, today)}
    daily_rows = DailyVisitor.objects.filter(**date_range).values('visit_date').annotate(
        total=Count('id')
    ).order_by('visit_date')
    daily_map = {row['visit_date']: row['total'] for row in daily_rows}
    daily = [
        {'visit_date': start + timedelta(days=offset),
         'total': daily_map.get(start + timedelta(days=offset), 0)}
        for offset in range(30)
    ]
    modules = list(ModuleUsage.objects.filter(**date_range).values('module').annotate(
        total=Count('id')
    ).order_by('-total')[:10])
    top_pages = PageView.objects.filter(**date_range).values('path').annotate(
        total=Count('id')
    ).order_by('-total')[:8]
    visitors_total = DailyVisitor.objects.filter(**date_range).count()
    visitors_today = DailyVisitor.objects.filter(visit_date=today).count()
    pageviews_total = PageView.objects.filter(**date_range).count()
    module_total = ModuleUsage.objects.filter(**date_range).count()
    max_module = max([row['total'] for row in modules], default=0)
    return render(request, 'site_insights/owner_dashboard.html', {
        'today': today, 'start': start, 'daily': daily, 'modules': modules,
        'top_pages': top_pages, 'visitors_total': visitors_total,
        'visitors_today': visitors_today, 'pageviews_total': pageviews_total,
        'module_total': module_total, 'max_module': max_module,
    })


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


