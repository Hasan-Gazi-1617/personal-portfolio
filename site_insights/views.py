from datetime import date, datetime, timedelta
import re
import uuid
from urllib.parse import urlparse
from django.db.models import Count
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
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
    """Private analytics with selectable day, month, or year reporting periods."""
    if not request.session.get('owner_access'):
        return redirect('owner_login')

    today = timezone.localdate()
    period = request.GET.get('period', 'month').lower()
    if period not in {'day', 'month', 'year'}:
        period = 'month'

    selected_day = today
    selected_month = today.strftime('%Y-%m')
    selected_year = str(today.year)
    try:
        if period == 'day':
            selected_day = date.fromisoformat(request.GET.get('date', ''))
        elif period == 'month':
            raw_month = request.GET.get('month', selected_month)
            parsed_month = datetime.strptime(raw_month, '%Y-%m').date()
            selected_month = parsed_month.strftime('%Y-%m')
        else:
            raw_year = request.GET.get('year', selected_year)
            if not re.fullmatch(r'\\d{4}', raw_year):
                raise ValueError
            selected_year = raw_year
            if int(selected_year) < 2000 or int(selected_year) > today.year + 1:
                raise ValueError
    except (ValueError, TypeError):
        period = 'month'
        selected_month = today.strftime('%Y-%m')

    if period == 'day':
        start = end = selected_day
        chart_title = selected_day.strftime('%d %B %Y')
        chart_mode = 'hour'
        labels = [f'{hour:02d}:00' for hour in range(24)]
        visitor_qs = DailyVisitor.objects.filter(visit_date=selected_day)
        page_qs = PageView.objects.filter(visit_date=selected_day)
        module_qs = ModuleUsage.objects.filter(visit_date=selected_day)
        visitor_groups = visitor_qs.annotate(bucket=TruncHour('created_at', tzinfo=timezone.get_current_timezone())).values('bucket').annotate(total=Count('id')).order_by('bucket')
        page_groups = page_qs.annotate(bucket=TruncHour('viewed_at', tzinfo=timezone.get_current_timezone())).values('bucket').annotate(total=Count('id')).order_by('bucket')
        module_groups = module_qs.annotate(bucket=TruncHour('created_at', tzinfo=timezone.get_current_timezone())).values('bucket').annotate(total=Count('id')).order_by('bucket')
        def hour_key(bucket):
            return timezone.localtime(bucket).hour if bucket else None
        visitors_map = {hour_key(r['bucket']): r['total'] for r in visitor_groups}
        pages_map = {hour_key(r['bucket']): r['total'] for r in page_groups}
        modules_map = {hour_key(r['bucket']): r['total'] for r in module_groups}
        series = [{'label': labels[i], 'visitors': visitors_map.get(i, 0), 'views': pages_map.get(i, 0), 'modules': modules_map.get(i, 0)} for i in range(24)]
    elif period == 'month':
        parsed = datetime.strptime(selected_month, '%Y-%m').date()
        start = parsed.replace(day=1)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        chart_title = parsed.strftime('%B %Y')
        chart_mode = 'day'
        labels = [str(day).zfill(2) for day in range(1, end.day + 1)]
        visitor_qs = DailyVisitor.objects.filter(visit_date__range=(start, end))
        page_qs = PageView.objects.filter(visit_date__range=(start, end))
        module_qs = ModuleUsage.objects.filter(visit_date__range=(start, end))
        def grouped(qs, field):
            return qs.values(field).annotate(total=Count('id')).order_by(field)
        visitors_map = {r['visit_date'].day: r['total'] for r in grouped(visitor_qs, 'visit_date')}
        pages_map = {r['visit_date'].day: r['total'] for r in grouped(page_qs, 'visit_date')}
        modules_map = {r['visit_date'].day: r['total'] for r in grouped(module_qs, 'visit_date')}
        series = [{'label': labels[i-1], 'visitors': visitors_map.get(i, 0), 'views': pages_map.get(i, 0), 'modules': modules_map.get(i, 0)} for i in range(1, end.day+1)]
    else:
        start = date(int(selected_year), 1, 1)
        end = date(int(selected_year), 12, 31)
        if int(selected_year) == today.year:
            end = today
        chart_title = selected_year
        chart_mode = 'month'
        labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        visitor_qs = DailyVisitor.objects.filter(visit_date__range=(start, end))
        page_qs = PageView.objects.filter(visit_date__range=(start, end))
        module_qs = ModuleUsage.objects.filter(visit_date__range=(start, end))
        visitors_map = {r['visit_date'].month: r['total'] for r in visitor_qs.annotate(bucket=TruncMonth('visit_date')).values('bucket').annotate(total=Count('id'))}
        pages_map = {r['visit_date'].month: r['total'] for r in page_qs.annotate(bucket=TruncMonth('visit_date')).values('bucket').annotate(total=Count('id'))}
        modules_map = {r['visit_date'].month: r['total'] for r in module_qs.annotate(bucket=TruncMonth('visit_date')).values('bucket').annotate(total=Count('id'))}
        # TruncMonth returns bucket; use its month component.
        visitors_map = {r['bucket'].month: r['total'] for r in visitor_qs.annotate(bucket=TruncMonth('visit_date')).values('bucket').annotate(total=Count('id'))}
        pages_map = {r['bucket'].month: r['total'] for r in page_qs.annotate(bucket=TruncMonth('visit_date')).values('bucket').annotate(total=Count('id'))}
        modules_map = {r['bucket'].month: r['total'] for r in module_qs.annotate(bucket=TruncMonth('visit_date')).values('bucket').annotate(total=Count('id'))}
        series = [{'label': labels[i-1], 'visitors': visitors_map.get(i, 0), 'views': pages_map.get(i, 0), 'modules': modules_map.get(i, 0)} for i in range(1, 13)]

    modules = list(module_qs.values('module').annotate(total=Count('id')).order_by('-total')[:10])
    top_pages = page_qs.values('path').annotate(total=Count('id')).order_by('-total')[:8]
    visitors_total = visitor_qs.count()
    pageviews_total = page_qs.count()
    module_total = module_qs.count()
    return render(request, 'site_insights/owner_dashboard.html', {
        'today': today, 'start': start, 'end': end, 'period': period,
        'selected_day': selected_day, 'selected_month': selected_month,
        'selected_year': selected_year, 'chart_title': chart_title,
        'chart_mode': chart_mode, 'series': series,
        'modules': modules, 'top_pages': top_pages,
        'visitors_total': visitors_total, 'visitors_today': visitors_total,
        'pageviews_total': pageviews_total, 'module_total': module_total,
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
