import os
import logging
import secrets
import time

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

logger = logging.getLogger(__name__)

from .forms import AdminTicketForm, EngineerTicketUpdateForm
from .models import ComplaintTicket, TicketActivity

def home(request):
    return render(request, "home.html")


def mikrotik_generator(request):
    """Interactive client-side RouterOS configuration generator."""
    return render(request, "mikrotik_generator.html")


def algorithm_studio(request):
    """Interactive data structure and algorithm learning studio."""
    return render(request, "algorithm_studio.html")


def tki_dashboard(request):
    tickets = ComplaintTicket.objects.select_related("assigned_engineer", "created_by")
    query = request.GET.get("q", "").strip()
    engineer = request.GET.get("engineer", "").strip()
    status = request.GET.get("status", "").strip()
    support = request.GET.get("support", "").strip()
    report_period = request.GET.get("period", "daily")
    if report_period not in {"daily", "monthly"}:
        report_period = "daily"

    if query:
        tickets = tickets.filter(Q(tki_id__icontains=query) | Q(client_id__icontains=query) | Q(complaint__icontains=query))
    if engineer in dict(ComplaintTicket.SupportEngineer.choices):
        tickets = tickets.filter(field_support_engineer=engineer)
    if status:
        tickets = tickets.filter(status=status)
    if support == "yes":
        tickets = tickets.exclude(field_support_engineer="")
    elif support == "no":
        tickets = tickets.filter(field_support_engineer="")

    from django.contrib.auth import get_user_model
    engineers = get_user_model().objects.filter(is_active=True, is_staff=False).order_by("first_name", "username")
    all_tickets = ComplaintTicket.objects.all()
    now = timezone.localtime()
    report_tickets = all_tickets.filter(opened_at__date=now.date()) if report_period == "daily" else all_tickets.filter(opened_at__year=now.year, opened_at__month=now.month)
    summary = {
        "total": report_tickets.count(),
        "pending": report_tickets.filter(status=ComplaintTicket.Status.PENDING).count(),
        "solved": report_tickets.filter(status=ComplaintTicket.Status.SOLVED).count(),
        "cancelled": report_tickets.filter(status=ComplaintTicket.Status.CANCELLED).count(),
        "dependency": report_tickets.exclude(dependency="").count(),
        "attention": report_tickets.filter(attention=True).count(),
    }
    workload = engineers.annotate(
        active_count=Count("assigned_tickets", filter=Q(assigned_tickets__status=ComplaintTicket.Status.PENDING)),
        closed_count=Count("assigned_tickets", filter=Q(assigned_tickets__status=ComplaintTicket.Status.SOLVED)),
    )
    engineer_report = []
    max_pending = 1
    for value, label in ComplaintTicket.SupportEngineer.choices:
        engineer_tickets = report_tickets.filter(field_support_engineer=value)
        pending_count = engineer_tickets.filter(status=ComplaintTicket.Status.PENDING).count()
        max_pending = max(max_pending, pending_count)
        engineer_report.append({
            "value": value, "label": label,
            "total": engineer_tickets.count(),
            "pending": pending_count,
            "solved": engineer_tickets.filter(status=ComplaintTicket.Status.SOLVED).count(),
        })
    for item in engineer_report:
        item["bar_percent"] = round(item["pending"] / max_pending * 100)

    dependency_report = []
    dependency_total = max(summary["dependency"], 1)
    dependency_colors = ["#32d399", "#55b8ff", "#f6bd47", "#a78bfa", "#fb7185", "#94a3b8"]
    gradient_stops = []
    cursor = 0
    for index, (value, label) in enumerate(ComplaintTicket.Dependency.choices):
        count = report_tickets.filter(dependency=value).count()
        percent = round(count / dependency_total * 100)
        color = dependency_colors[index]
        if count:
            gradient_stops.append(f"{color} {cursor}% {cursor + percent}%")
            cursor += percent
        dependency_report.append({"value": value, "label": label, "count": count, "percent": percent, "color": color})
    dependency_gradient = "conic-gradient(" + (", ".join(gradient_stops) if gradient_stops else "#334155 0 100%") + ")"
    return render(request, "tki/dashboard.html", {
        "tickets": tickets[:150], "engineers": engineers, "workload": workload,
        "summary": summary, "statuses": ComplaintTicket.Status.choices,
        "support_engineers": ComplaintTicket.SupportEngineer.choices,
        "report_period": report_period, "engineer_report": engineer_report,
        "dependency_report": dependency_report, "dependency_gradient": dependency_gradient,
        "is_tki_admin": True,
    })


def tki_detail(request, pk):
    ticket = get_object_or_404(ComplaintTicket.objects.select_related("assigned_engineer", "created_by"), pk=pk)
    form = EngineerTicketUpdateForm(instance=ticket)
    return render(request, "tki/detail.html", {
        "ticket": ticket, "form": form, "can_update": True,
        "is_tki_admin": True,
    })


@require_POST
def tki_update(request, pk):
    ticket = get_object_or_404(ComplaintTicket, pk=pk)
    form = EngineerTicketUpdateForm(request.POST, instance=ticket)
    if form.is_valid():
        updated = form.save(commit=False)
        if updated.status == ComplaintTicket.Status.SOLVED and not updated.resolved_at:
            updated.resolved_at = timezone.now()
        elif updated.status != ComplaintTicket.Status.SOLVED:
            updated.resolved_at = None
        updated.save()
        actor = request.user if request.user.is_authenticated else None
        TicketActivity.objects.create(ticket=ticket, actor=actor, action="TKI updated", detail=f"Status: {updated.get_status_display()}")
        messages.success(request, "TKI feedback updated.")
        return redirect("tki_detail", pk=ticket.pk)
    return render(request, "tki/detail.html", {
        "ticket": ticket, "form": form, "can_update": True,
        "is_tki_admin": True,
    }, status=400)


def tki_create(request):
    form = AdminTicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.created_by = request.user if request.user.is_authenticated else None
        if ticket.assigned_engineer_id:
            ticket.support_assigned_at = timezone.now()
            if not ticket.status:
                ticket.status = ComplaintTicket.Status.PENDING
        ticket.save()
        actor = request.user if request.user.is_authenticated else None
        TicketActivity.objects.create(ticket=ticket, actor=actor, action="TKI created")
        messages.success(request, f"{ticket.tki_id} created successfully.")
        return redirect("tki_detail", pk=ticket.pk)
    return render(request, "tki/form.html", {"form": form, "title": "Create TKI"})


def tki_admin_edit(request, pk):
    ticket = get_object_or_404(ComplaintTicket, pk=pk)
    previous_engineer_id = ticket.assigned_engineer_id
    form = AdminTicketForm(request.POST or None, instance=ticket)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        if updated.assigned_engineer_id != previous_engineer_id:
            updated.support_assigned_at = timezone.now() if updated.assigned_engineer_id else None
        if updated.status == ComplaintTicket.Status.SOLVED and not updated.resolved_at:
            updated.resolved_at = timezone.now()
        updated.save()
        actor = request.user if request.user.is_authenticated else None
        TicketActivity.objects.create(ticket=ticket, actor=actor, action="Full TKI update")
        messages.success(request, "TKI updated successfully.")
        return redirect("tki_detail", pk=ticket.pk)
    return render(request, "tki/form.html", {"form": form, "title": f"Edit {ticket.tki_id}", "ticket": ticket})


@require_http_methods(["GET", "POST"])
def owner_login(request):
    if request.session.get("owner_access"):
        return redirect("home")

    if request.method == "POST":
        now = int(time.time())
        attempts = request.session.get("owner_login_attempts", [])
        attempts = [stamp for stamp in attempts if now - stamp < 15 * 60]
        if len(attempts) >= 5:
            messages.error(request, "Too many attempts. Please wait 15 minutes and try again.")
            request.session["owner_login_attempts"] = attempts
            return render(request, "owner_login.html", status=429)

        submitted_key = request.POST.get("access_key", "")
        configured_key = os.environ.get("OWNER_ACCESS_KEY", "")

        if configured_key and secrets.compare_digest(submitted_key, configured_key):
            request.session.cycle_key()
            request.session["owner_access"] = True
            request.session.set_expiry(60 * 60 * 24 * 7)
            request.session.pop("owner_login_attempts", None)
            return redirect("home")

        attempts.append(now)
        request.session["owner_login_attempts"] = attempts
        logger.warning(
            "Rejected owner login attempt",
            extra={"client_ip": request.META.get("REMOTE_ADDR", "unknown"), "attempt_count": len(attempts)},
        )
        messages.error(request, "Invalid owner access key.")

    return render(request, "owner_login.html")


@require_POST
def owner_logout(request):
    request.session.pop("owner_access", None)
    request.session.cycle_key()
    return redirect("home")
