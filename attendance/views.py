from datetime import datetime
from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import AttendanceRecord, COURSE_MODULES, StudentProfile


class ClockForm(forms.Form):
    student_id = forms.IntegerField()
    module = forms.CharField(max_length=120)
    period = forms.ChoiceField(choices=AttendanceRecord.Period.choices)
    time_value = forms.TimeField(input_formats=["%H:%M"])


def student_attendance(request):
    students = StudentProfile.objects.filter(is_active=True)
    if request.method == "POST":
        form = ClockForm(request.POST)
        action = request.POST.get("action")
        if form.is_valid() and action in {"sign_in", "sign_out"}:
            student = get_object_or_404(students, pk=form.cleaned_data["student_id"])
            module = form.cleaned_data["module"]
            if module not in (student.modules or []) or student.course not in COURSE_MODULES:
                messages.error(request, "The selected module is not assigned to this student.")
            else:
                record, _ = AttendanceRecord.objects.get_or_create(
                    class_date=timezone.localdate(), student=student, period=form.cleaned_data["period"],
                    defaults={"course_name": student.course, "module_name": module},
                )
                if record.module_name != module:
                    messages.error(request, "This attendance session already has a different module selected.")
                else:
                    setattr(record, "sign_in" if action == "sign_in" else "sign_out", form.cleaned_data["time_value"])
                    record.save()
                    messages.success(request, f"{action.replace('_', ' ').title()} time saved for {student.name}.")
        else:
            messages.error(request, "Please select your name, assigned module, AM/PM and a valid time.")
        return redirect("student_attendance")
    return render(request, "attendance/portal.html", {
        "students": students,
        "course_modules": COURSE_MODULES,
        "today": timezone.localdate(),
        "now_time": timezone.localtime().strftime("%H:%M"),
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
                record, _ = AttendanceRecord.objects.update_or_create(
                    class_date=class_date, student=student, period=period,
                    defaults={"course_name": student.course, "module_name": module,
                              "sign_in": datetime.strptime(request.POST["sign_in"], "%H:%M").time() if request.POST.get("sign_in") else None,
                              "sign_out": datetime.strptime(request.POST["sign_out"], "%H:%M").time() if request.POST.get("sign_out") else None},
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
