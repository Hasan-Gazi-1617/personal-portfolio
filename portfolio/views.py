import os
import logging
import secrets
import time

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


def mikrotik_generator(request):
    """Interactive client-side RouterOS configuration generator."""
    return render(request, "mikrotik_generator.html")


def algorithm_studio(request):
    """Interactive data structure and algorithm learning studio."""
    return render(request, "algorithm_studio.html")


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
