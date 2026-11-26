from datetime import datetime
from django import forms
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import AttendanceRecord, COURSE_MODULES, StudentCourse, StudentProfile


class ClockForm(forms.Form):
    student_id = forms.IntegerField()
    course = forms.CharField(max_length=40)
    module = forms.CharField(max_length=120)
    period = forms.ChoiceField(choices=AttendanceRecord.Period.choices)
    time_value = forms.TimeField(input_formats=["%H:%M"])


def student_attendance(request):
    if not request.user.is_authenticated:
        return redirect("student_login")
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first()
    if not profile:
        return redirect("student_login")
    enrollments = StudentCourse.objects.filter(student=profile, is_active=True)
    if not enrollments.exists():
        enrollments = [StudentCourse(student=profile, course=profile.course, modules=profile.modules or [])]
    if request.method == "POST":
        form = ClockForm(request.POST)
        action = request.POST.get("action")
        if form.is_valid() and action in {"sign_in", "sign_out"}:
            with transaction.atomic():
                student = get_object_or_404(StudentProfile.objects.select_for_update(), pk=profile.pk, is_active=True)
                course = form.cleaned_data["course"]
                module = form.cleaned_data["module"]
                period = form.cleaned_data["period"]
                enrollment = next((item for item in enrollments if item.course == course), None)
                active = AttendanceRecord.objects.select_for_update().filter(
                    student=student, sign_in__isnull=False, sign_out__isnull=True
                ).order_by("-class_date", "-created_at").first()
                if not enrollment or module not in (enrollment.modules or []):
                    messages.error(request, "The selected course or module is not assigned to your account.")
                elif action == "sign_in":
                    if active:
                        messages.error(request, "You are already signed in. Please sign out before starting a new session.")
                    else:
                        AttendanceRecord.objects.create(
                            class_date=timezone.localdate(), student=student, period=period,
                            course_name=course, module_name=module, sign_in=form.cleaned_data["time_value"],
                        )
                        messages.success(request, f"Sign In saved for {student.name}.")
                elif not active:
                    messages.error(request, "No active Sign In session was found. Please Sign In first.")
                elif active.period != period or active.module_name != module or active.course_name != course:
                    messages.error(request, "Your active session details are locked until Sign Out.")
                else:
                    active.sign_out = form.cleaned_data["time_value"]
                    active.save(update_fields=["sign_out", "updated_at"])
                    messages.success(request, f"Sign Out saved for {student.name}.")
        else:
            messages.error(request, "Please select your assigned course, module, AM/PM and a valid time.")
        return redirect("student_attendance")
    return render(request, "attendance/portal.html", {
        "student": profile,
        "course_enrollments": enrollments,
        "today": timezone.localdate(),
        "now_time": timezone.localtime().strftime("%H:%M"),
        "attendance_records": AttendanceRecord.objects.filter(student=profile).order_by("-class_date", "period")[:150],
    })

@require_http_methods(["GET", "POST"])
def attendance_admin(request):
    if not request.session.get("owner_access"):
        return redirect("owner_login")
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_student":
            name = request.POST.get("name", "").strip()[:120]
            roll = request.POST.get("roll", "").strip()[:40]
            course = request.POST.get("course", "")
            modules = [m.strip() for m in request.POST.getlist("modules") if m.strip()]
            if not name or course not in COURSE_MODULES or not modules or any(m not in COURSE_MODULES[course] for m in modules):
                messages.error(request, "Enter a student name, valid course and at least one valid assigned module.")
            else:
                StudentProfile.objects.update_or_create(name=name, roll=roll, course=course, defaults={"modules": modules, "is_active": True})
                messages.success(request, f"Student profile saved: {name}.")
        elif action == "manual_attendance":
            try:
                student = get_object_or_404(StudentProfile, pk=int(request.POST.get("student_id")), is_active=True)
                class_date = datetime.strptime(request.POST.get("class_date", ""), "%Y-%m-%d").date()
                period = request.POST.get("period")
                module = request.POST.get("module", "")
                if period not in AttendanceRecord.Period.values or module not in student.modules:
                    raise ValueError
                AttendanceRecord.objects.create(
                    class_date=class_date, student=student, period=period,
                    course_name=student.course, module_name=module,
                    sign_in=datetime.strptime(request.POST["sign_in"], "%H:%M").time() if request.POST.get("sign_in") else None,
                    sign_out=datetime.strptime(request.POST["sign_out"], "%H:%M").time() if request.POST.get("sign_out") else None,
                )
                messages.success(request, f"Attendance saved for {student.name}.")
            except (ValueError, KeyError, TypeError):
                messages.error(request, "Check the date, student, module and time values.")
        elif action == "toggle_student":
            student = get_object_or_404(StudentProfile, pk=request.POST.get("student_id"))
            student.is_active = not student.is_active
            student.save(update_fields=["is_active"])
            messages.success(request, f"Student {'activated' if student.is_active else 'deactivated'}.")
        return redirect("attendance_admin")
    records = AttendanceRecord.objects.select_related("student")[:300]
    return render(request, "attendance/admin.html", {
        "students": StudentProfile.objects.all(), "active_students": StudentProfile.objects.filter(is_active=True),
        "records": records, "course_modules": COURSE_MODULES, "today": timezone.localdate(),
    })
