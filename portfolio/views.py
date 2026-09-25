import os
import secrets

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST


def home(request):
    return render(request, "home.html")


def mikrotik_generator(request):
    """Interactive client-side RouterOS configuration generator."""
    return render(request, "mikrotik_generator.html")


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
