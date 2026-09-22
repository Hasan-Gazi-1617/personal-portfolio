import json
import os
import secrets
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import OLTDevice, ONUEvent, ONUStatus


OLT_CATALOG = {
    "cdata-epon-12": ("OLT CDATA (E-PON):12", "https://103.101.253.17:4512/"),
    "cdata-gpon-14": ("OLT CDATA (G-PON-1):14", "http://103.101.253.17:4514/"),
    "cdata-gpon-15": ("OLT CDATA (G-PON-2):15", "http://103.101.253.17:4515/"),
    "cdata-gpon-16": ("OLT CDATA (G-PON-3 POP Akhalia):16", "http://103.101.253.17:4516/"),
    "cdata-gpon-18": ("OLT CDATA (G-PON POP Akhalia):18", "http://103.101.253.17:4518/"),
    "cdata-gpon-19": ("OLT CDATA (G-PON POP Akhalia):19", "http://103.101.253.17:4519/"),
    "cdata-gpon-17": ("OLT CDATA (G-PON-4 POP Khadim):17", "http://103.101.253.17:4517/"),
    "vsol-10": ("OLT VSOL:10", "https://103.101.253.17:4510/"),
}


def home(request):
    return render(request, "home.html")


def _owner_allowed(request):
    return bool(request.session.get("owner_access"))


def _ensure_olt_catalog():
    devices = []
    for key, (name, management_url) in OLT_CATALOG.items():
        device, _ = OLTDevice.objects.update_or_create(
            key=key,
            defaults={"name": name, "management_url": management_url, "active": True},
        )
        devices.append(device)
    return devices


@require_http_methods(["GET", "POST"])
def owner_login(request):
    if request.session.get("owner_access"):
        return redirect("home")

    if request.method == "POST":
        submitted_key = request.POST.get("access_key", "")
        configured_key = os.environ.get("OWNER_ACCESS_KEY", "")

        if configured_key and secrets.compare_digest(submitted_key, configured_key):
            request.session.cycle_key()
            request.session["owner_access"] = True
            request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect("home")

        messages.error(request, "Invalid owner access key.")

    return render(request, "owner_login.html")


@require_POST
def owner_logout(request):
    request.session.pop("owner_access", None)
    request.session.cycle_key()
    return redirect("home")


@require_GET
def olt_dashboard(request):
    if not _owner_allowed(request):
        return redirect("owner_login")

    _ensure_olt_catalog()
    devices = OLTDevice.objects.annotate(
        total_count=Count("onus"),
        online_count=Count("onus", filter=Q(onus__status=ONUStatus.ONLINE)),
        offline_count=Count("onus", filter=Q(onus__status=ONUStatus.OFFLINE)),
    )
    pon_rows = list(
        ONUStatus.objects.values("olt__key", "olt__name", "pon_id")
        .annotate(
            total=Count("id"),
            online=Count("id", filter=Q(status=ONUStatus.ONLINE)),
            offline=Count("id", filter=Q(status=ONUStatus.OFFLINE)),
        )
        .order_by("olt__name", "pon_id")
    )
    cutoff = timezone.now() - timedelta(minutes=15)
    newly_down = (
        ONUStatus.objects.select_related("olt")
        .filter(status=ONUStatus.OFFLINE, last_change__gte=cutoff)
        .order_by("-last_change")
    )
    all_onus = ONUStatus.objects.select_related("olt").order_by(
        "olt__name", "pon_id", "onu_id"
    )
    recent_events = ONUEvent.objects.select_related("onu", "onu__olt")[:100]

    totals = ONUStatus.objects.aggregate(
        total=Count("id"),
        online=Count("id", filter=Q(status=ONUStatus.ONLINE)),
        offline=Count("id", filter=Q(status=ONUStatus.OFFLINE)),
    )

    return render(
        request,
        "olt_dashboard.html",
        {
            "devices": devices,
            "pon_rows": pon_rows,
            "newly_down": newly_down,
            "all_onus": all_onus,
            "recent_events": recent_events,
            "totals": totals,
        },
    )


@require_GET
def olt_status_api(request):
    if not _owner_allowed(request):
        return JsonResponse({"detail": "Owner login required."}, status=403)

    rows = ONUStatus.objects.select_related("olt").order_by("olt__name", "pon_id", "onu_id")
    return JsonResponse(
        {
            "generated_at": timezone.now().isoformat(),
            "onus": [
                {
                    "olt_key": row.olt.key,
                    "olt_name": row.olt.name,
                    "pon_id": row.pon_id,
                    "onu_id": row.onu_id,
                    "serial": row.serial,
                    "description": row.description,
                    "status": row.status,
                    "down_reason": row.down_reason,
                    "last_change": row.last_change.isoformat(),
                    "last_down": row.last_down.isoformat() if row.last_down else None,
                    "last_up": row.last_up.isoformat() if row.last_up else None,
                }
                for row in rows
            ],
        }
    )


def _authorized_ingest(request):
    configured = os.environ.get("OLT_INGEST_TOKEN", "")
    header = request.headers.get("Authorization", "")
    submitted = header.removeprefix("Bearer ").strip()
    return bool(configured and submitted and secrets.compare_digest(configured, submitted))


def _event_time(value):
    parsed = parse_datetime(value) if isinstance(value, str) else None
    if parsed is None:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


@csrf_exempt
@require_POST
def olt_ingest(request):
    if not _authorized_ingest(request):
        return JsonResponse({"detail": "Invalid ingest token."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"detail": "Invalid JSON body."}, status=400)

    olt_key = str(payload.get("olt_key", "")).strip()
    units = payload.get("onus")
    if olt_key not in OLT_CATALOG:
        return JsonResponse({"detail": "Unknown olt_key."}, status=400)
    if not isinstance(units, list) or len(units) > 10000:
        return JsonResponse({"detail": "onus must be a list with at most 10000 items."}, status=400)

    name, management_url = OLT_CATALOG[olt_key]
    observed_at = _event_time(payload.get("observed_at"))
    processed = 0
    changed = 0
    newly_down = []
    seen = set()

    with transaction.atomic():
        olt, _ = OLTDevice.objects.update_or_create(
            key=olt_key,
            defaults={
                "name": name,
                "management_url": management_url,
                "active": True,
                "last_seen": observed_at,
            },
        )

        for item in units:
            if not isinstance(item, dict):
                continue
            pon_id = str(item.get("pon_id", "")).strip()
            onu_id = str(item.get("onu_id", "")).strip()
            if not pon_id or not onu_id:
                continue

            raw_status = str(item.get("status", "")).strip().lower()
            status = ONUStatus.ONLINE if raw_status in {"online", "up", "active", "1"} else ONUStatus.OFFLINE
            serial = str(item.get("serial", ""))[:64].strip()
            description = str(item.get("description", ""))[:255].strip()
            reason = str(item.get("down_reason", ""))[:120].strip()
            seen.add((pon_id, onu_id))

            onu, created = ONUStatus.objects.get_or_create(
                olt=olt,
                pon_id=pon_id,
                onu_id=onu_id,
                defaults={
                    "serial": serial,
                    "description": description,
                    "status": status,
                    "down_reason": reason if status == ONUStatus.OFFLINE else "",
                    "last_change": observed_at,
                    "last_seen": observed_at,
                    "last_up": observed_at if status == ONUStatus.ONLINE else None,
                    "last_down": observed_at if status == ONUStatus.OFFLINE else None,
                },
            )

            previous = onu.status
            if not created:
                onu.serial = serial or onu.serial
                onu.description = description or onu.description
                onu.last_seen = observed_at
                onu.down_reason = reason if status == ONUStatus.OFFLINE else ""
                if previous != status:
                    changed += 1
                    onu.status = status
                    onu.last_change = observed_at
                    if status == ONUStatus.OFFLINE:
                        onu.last_down = observed_at
                    else:
                        onu.last_up = observed_at
                    ONUEvent.objects.create(
                        onu=onu,
                        event_type=ONUEvent.DOWN if status == ONUStatus.OFFLINE else ONUEvent.UP,
                        occurred_at=observed_at,
                        previous_status=previous,
                        status=status,
                        reason=reason,
                    )
                onu.save()
            elif status == ONUStatus.OFFLINE:
                ONUEvent.objects.create(
                    onu=onu,
                    event_type=ONUEvent.DOWN,
                    occurred_at=observed_at,
                    previous_status="",
                    status=status,
                    reason=reason,
                )

            if status == ONUStatus.OFFLINE and (created or previous != status):
                newly_down.append(
                    {
                        "pon_id": pon_id,
                        "onu_id": onu_id,
                        "serial": onu.serial,
                        "description": onu.description or onu.serial or f"ONU {onu_id}",
                        "down_reason": reason,
                    }
                )
            processed += 1

        if payload.get("full_snapshot") is True:
            # Compare exact (PON, ONU) keys; separate __in filters would create a cross-product.
            for onu in list(olt.onus.filter(status=ONUStatus.ONLINE)):
                if (onu.pon_id, onu.onu_id) in seen:
                    continue
                onu.status = ONUStatus.OFFLINE
                onu.down_reason = "Missing from full snapshot"
                onu.last_change = observed_at
                onu.last_down = observed_at
                onu.last_seen = observed_at
                onu.save(update_fields=("status", "down_reason", "last_change", "last_down", "last_seen"))
                ONUEvent.objects.create(
                    onu=onu,
                    event_type=ONUEvent.DOWN,
                    occurred_at=observed_at,
                    previous_status=ONUStatus.ONLINE,
                    status=ONUStatus.OFFLINE,
                    reason=onu.down_reason,
                )
                newly_down.append(
                    {
                        "pon_id": onu.pon_id,
                        "onu_id": onu.onu_id,
                        "serial": onu.serial,
                        "description": onu.client_label,
                        "down_reason": onu.down_reason,
                    }
                )
                changed += 1

    return JsonResponse(
        {
            "ok": True,
            "olt_key": olt_key,
            "processed": processed,
            "changed": changed,
            "newly_down": newly_down,
            "observed_at": observed_at.isoformat(),
        }
    )
