import os
import json
import hmac
import logging
import secrets
import time
from calendar import monthrange
from datetime import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

logger = logging.getLogger(__name__)

from .forms import AdminTicketForm, EngineerTicketUpdateForm
from .models import ComplaintTicket, TicketActivity, OLTDevice, ONUStatus, OLTEvent, IELTSNotice, IELTSMaterial, IELTSLesson, IELTSPracticeSet, IELTSPracticeAttempt, IELTSAttendance, IELTSAssignment, IELTSAssignmentSubmission
from attendance.models import AttendanceRecord, COURSE_MODULES, StudentCourse, StudentProfile
from .tki_import import decode_tki_upload, import_solved_tsv


def _month_bounds(raw_month):
    try:
        selected = datetime.strptime(raw_month, "%Y-%m")
    except (TypeError, ValueError):
        selected = timezone.localtime().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = timezone.make_aware(selected) if timezone.is_naive(selected) else selected
    last_day = monthrange(start.year, start.month)[1]
    end = start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _owner_can_manage_tki(request):
    return bool(request.session.get("owner_access"))

def home(request):
    return render(request, "home.html")


def _student_clock_in_dhaka(request):
    """Convert a browser-local ISO timestamp to the project's Asia/Dhaka timezone."""
    raw_timestamp = request.POST.get("timestamp_local", "").strip()
    parsed = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
    if timezone.is_naive(parsed):
        raise ValueError("A timezone-aware student timestamp is required.")
    return timezone.localtime(parsed)


def student_learning_house(request):
    """Public overview of available subjects; only aggregate enrollment counts are shown."""
    subjects = [
        {"slug": "ielts", "title": "IELTS", "courses": ["IELTS", "Language Testing"], "description": "English skills and IELTS preparation."},
        {"slug": "bcs", "title": "BCS", "courses": ["BCS"], "description": "BCS preliminary and subject-wise preparation."},
        {"slug": "computer-science", "title": "Computer Science", "courses": ["Programming", "CSE Course", "Undergraduate Courses"], "description": "Programming and core computer science learning."},
    ]
    for subject in subjects:
        subject["student_count"] = StudentCourse.objects.filter(is_active=True, student__is_active=True, course__in=subject["courses"]).values("student_id").distinct().count()
    return render(request, "students/learning_house.html", {"subjects": subjects})


def student_course(request, slug):
    """Require an active student account assigned to the selected subject."""
    subject_map = {
        "ielts": {"title": "IELTS", "courses": ["IELTS", "Language Testing"], "modules": ["Listening", "Reading", "Writing", "Speaking", "Lexical Resources", "Grammatical Theory"]},
        "language-testing": {"title": "Language Testing", "courses": ["Language Testing"], "modules": COURSE_MODULES["Language Testing"]},
        "school-courses": {"title": "School Courses", "courses": ["School Academy"], "modules": COURSE_MODULES["School Academy"]},
        "college-courses": {"title": "College Courses", "courses": ["College Academy"], "modules": COURSE_MODULES["College Academy"]},
        "bcs": {"title": "BCS", "courses": ["BCS"], "modules": COURSE_MODULES["BCS"]},
        "computer-science": {"title": "Computer Science", "courses": ["Programming", "CSE Course", "Undergraduate Courses"], "modules": sorted({m for c in ["Programming", "CSE Course", "Undergraduate Courses"] for m in COURSE_MODULES[c]})},
    }
    subject = subject_map.get(slug)
    if not subject:
        return redirect("student_learning_house")
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first() if request.user.is_authenticated else None
    if not profile:
        return render(request, "students/course_access.html", {"subject": subject, "authorized": False}, status=403)
    enrollments = [item for item in _student_course_enrollments(profile) if item.course in subject["courses"]]
    if not enrollments:
        return render(request, "students/course_access.html", {"subject": subject, "authorized": False}, status=403)
    return render(request, "students/course_access.html", {"subject": subject, "authorized": True, "student": profile, "course_enrollments": enrollments})


def ielts_learning(request):
    """Open the IELTS portal only for currently enrolled student accounts."""
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first() if request.user.is_authenticated else None
    enrollments = _student_course_enrollments(profile) if profile else []
    enrolled_courses = {item.course for item in enrollments}
    if not profile or not enrolled_courses:
        return render(request, "students/course_access.html", {"subject": {"title": "Student Portal"}, "authorized": False}, status=403)
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "attendance_clock":
            try:
                clock_action = request.POST.get("clock_action", "")
                local_clock = _student_clock_in_dhaka(request)
                clock_time = local_clock.time().replace(tzinfo=None)
                if clock_action not in {"sign_in", "sign_out"}:
                    raise ValueError
                with transaction.atomic():
                    student = get_object_or_404(
                        StudentProfile.objects.select_for_update(), pk=profile.pk, is_active=True
                    )
                    active = AttendanceRecord.objects.select_for_update().filter(
                        student=student, sign_in__isnull=False, sign_out__isnull=True
                    ).order_by("-class_date", "-created_at").first()
                    if clock_action == "sign_in":
                        module = request.POST.get("module", "")
                        period = request.POST.get("period", "")
                        course_name = request.POST.get("course", "").strip() or student.course
                        course_enrollment = next((item for item in _student_course_enrollments(student) if item.course == course_name), None)
                        if not course_enrollment or module not in (course_enrollment.modules or []) or period not in AttendanceRecord.Period.values:
                            raise ValueError
                        if active:
                            messages.error(request, "You are already signed in. Please sign out before starting a new session.")
                        else:
                            AttendanceRecord.objects.create(
                                class_date=local_clock.date(), student=student, period=period,
                                course_name=course_name, module_name=module, sign_in=clock_time,
                            )
                            messages.success(request, f"Sign In saved for {student.name}. Your local time was converted to Bangladesh time.")
                    else:
                        if not active:
                            messages.error(request, "No active Sign In session was found. Please Sign In first.")
                        elif active.period != request.POST.get("period") or active.module_name != request.POST.get("module"):
                            raise ValueError
                        else:
                            sign_in_at = datetime.combine(active.class_date, active.sign_in)
                            if local_clock.replace(tzinfo=None) < sign_in_at:
                                raise ValueError
                            active.sign_out = clock_time
                            active.sign_out_date = local_clock.date()
                            active.save(update_fields=["sign_out", "sign_out_date", "updated_at"])
                            messages.success(request, f"Sign Out saved for {student.name}. You can now start a new session.")
            except (ValueError, TypeError):
                messages.error(request, "Please select a valid student, assigned module, session and time.")
            selected_id = request.POST.get("student_id", "")
            return redirect(f"/students/ielts/?attendance_student={selected_id}#attendance")
        if action == "start_assignment":
            assignment = get_object_or_404(IELTSAssignment, pk=request.POST.get("assignment_id"), is_published=True)
            linked_profile = StudentProfile.objects.filter(user=request.user, is_active=True).first() if request.user.is_authenticated else None
            if not linked_profile or assignment.course not in {item.course for item in _student_course_enrollments(linked_profile)}:
                return JsonResponse({"ok": False, "message": "This assignment is not available in your enrolled courses."}, status=403)
            student_name = request.POST.get("student_name", "").strip()[:100]
            student_roll = request.POST.get("student_roll", "").strip()[:40]
            if linked_profile:
                student_name, student_roll = linked_profile.name, linked_profile.roll
            if not student_name:
                return JsonResponse({"ok": False, "message": "Enter your name before starting the timed assignment."}, status=400)
            receipts = request.session.get("ielts_submission_receipts", [])
            reopened = IELTSAssignmentSubmission.objects.filter(
                assignment=assignment, status="in_progress", started_at__isnull=True,
                receipt_code__in=receipts,
            ).order_by("-submitted_at").first()
            if reopened:
                submission = reopened
                submission.student_name = student_name
                submission.student_roll = student_roll
                if linked_profile:
                    submission.student_profile = linked_profile
                submission.started_at = timezone.now()
                submission.save(update_fields=["student_name", "student_roll", "started_at", "student_profile"])
            else:
                submission = IELTSAssignmentSubmission.objects.create(
                    assignment=assignment, student_name=student_name, student_roll=student_roll,
                    student_profile=linked_profile, status="in_progress", started_at=timezone.now(),
                )
            receipts.insert(0, str(submission.receipt_code))
            request.session["ielts_submission_receipts"] = list(dict.fromkeys(receipts))[:30]
            request.session.modified = True
            return JsonResponse({"ok": True, "submission_id": submission.pk, "started_at": submission.started_at.isoformat(), "duration": assignment.time_minutes * 60, "answer_text": submission.answer_text})
        if action == "track_assignment_paste":
            allowed_codes = request.session.get("ielts_submission_receipts", [])
            submission = get_object_or_404(IELTSAssignmentSubmission, pk=request.POST.get("submission_id"), receipt_code__in=allowed_codes)
            if submission.status != "in_progress":
                return JsonResponse({"ok": False, "locked": True, "message": submission.failed_reason or "This attempt is no longer active."}, status=409)
            submission.paste_attempts = min(3, submission.paste_attempts + 1)
            if submission.paste_attempts >= 3:
                submission.status = "failed"
                submission.failed_reason = "Assignment failed: copy/paste was attempted 3 times. The writing box has been locked. Ask your teacher/admin to reopen this attempt to start again."
                submission.save(update_fields=["paste_attempts", "status", "failed_reason"])
                return JsonResponse({"ok": False, "locked": True, "attempts": 3, "message": submission.failed_reason}, status=403)
            submission.save(update_fields=["paste_attempts"])
            return JsonResponse({"ok": True, "attempts": submission.paste_attempts, "remaining": 3-submission.paste_attempts, "message": f"Paste is disabled. Warning {submission.paste_attempts} of 3. Type your answer directly."})
        if action == "submit_assignment":
            allowed_codes = request.session.get("ielts_submission_receipts", [])
            submission = get_object_or_404(IELTSAssignmentSubmission, pk=request.POST.get("submission_id"), receipt_code__in=allowed_codes)
            assignment = submission.assignment
            answer_text = request.POST.get("answer_text", "").strip()
            words = len(answer_text.split())
            uploaded = request.FILES.get("submission_file")
            if submission.status == "failed":
                messages.error(request, submission.failed_reason or "This attempt is locked. Ask the teacher to reopen it.")
            elif submission.status != "in_progress" or not submission.started_at:
                messages.error(request, "Please click Start Assignment first.")
            elif (timezone.now()-submission.started_at).total_seconds() > assignment.time_minutes*60+10:
                submission.status="failed"
                submission.failed_reason="Assignment failed: the allotted writing time expired before submission."
                submission.answer_text=answer_text
                submission.word_count=words
                submission.save(update_fields=["status","failed_reason","answer_text","word_count"])
                messages.error(request, submission.failed_reason)
            elif not answer_text and not uploaded:
                messages.error(request, "Write your answer in the box before submitting.")
            elif words < assignment.min_words:
                messages.error(request, f"This task requires at least {assignment.min_words} words. Your answer has {words}.")
            elif words > assignment.max_words:
                messages.error(request, f"The maximum word count is {assignment.max_words}. Your answer has {words}.")
            elif uploaded and uploaded.size > 10 * 1024 * 1024:
                messages.error(request, "The attachment must be 10 MB or smaller.")
            elif uploaded and os.path.splitext(uploaded.name)[1].lower() not in (".pdf", ".docx", ".png", ".jpg", ".jpeg"):
                messages.error(request, "Please upload a PDF, Word document or image file.")
            else:
                submission.answer_text=answer_text
                submission.word_count=words
                submission.elapsed_seconds=max(0,int((timezone.now()-submission.started_at).total_seconds()))
                submission.file=uploaded or submission.file
                submission.status="submitted"
                submission.failed_reason=""
                submission.save()
                return redirect("ielts_submission_receipt", receipt_code=submission.receipt_code)
            return redirect("ielts_submission_receipt", receipt_code=submission.receipt_code)

    context = {
        "course_enrollments": enrollments,
        "notices": IELTSNotice.objects.filter(course__in=enrolled_courses, is_published=True).filter(Q(student__isnull=True) | Q(student=profile)),
        "materials": IELTSMaterial.objects.filter(course__in=enrolled_courses, is_published=True),
        "lessons": IELTSLesson.objects.filter(course__in=enrolled_courses, is_published=True),
        "practice_sets": IELTSPracticeSet.objects.filter(course__in=enrolled_courses, is_published=True),
        "attendance_records": AttendanceRecord.objects.filter(student=profile).select_related("student")[:300],
        "attendance_students": StudentProfile.objects.filter(pk=profile.pk, is_active=True),
        "open_attendance": [
            {
                "student_id": row.student_id, "class_date": row.class_date.isoformat(),
                "course_name": row.course_name, "module_name": row.module_name,
                "period": row.period, "sign_in": row.sign_in.strftime("%H:%M"),
            }
            for row in AttendanceRecord.objects.filter(student=profile, sign_in__isnull=False, sign_out__isnull=True).select_related("student")
        ],
        "today": timezone.localdate(),
        "now_time": timezone.localtime().strftime("%H:%M"),
        "assignments": IELTSAssignment.objects.filter(course__in=enrolled_courses, is_published=True),
        "my_submissions": IELTSAssignmentSubmission.objects.filter(receipt_code__in=request.session.get("ielts_submission_receipts", [])).select_related("assignment").order_by("-submitted_at"),
    }
    return render(request, "students/ielts.html", context)



def student_assignment_submission(request):
    """Student-only assignment workspace inside the personal student account."""
    if not request.user.is_authenticated:
        return redirect("student_access")
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first()
    if not profile:
        logout(request)
        messages.error(request, "No active student profile is linked to this account. Please contact your teacher.")
        return redirect("student_access")
    if request.method == "POST":
        # Reuse the existing, validated assignment workflow so timers, paste limits,
        # submission checks and receipt handling remain consistent.
        return ielts_learning(request)
    enrollments = _student_course_enrollments(profile)
    courses = [item.course for item in enrollments]
    return render(request, "students/student_assignment_submission.html", {
        "student": profile,
        "student_first_name": profile.name.strip().split()[0] if profile.name.strip() else "Student",
        "assignments": IELTSAssignment.objects.filter(course__in=courses, is_published=True).order_by("course", "title"),
        "submissions": IELTSAssignmentSubmission.objects.filter(student_profile=profile).select_related("assignment").order_by("-submitted_at")[:100],
    })


def ielts_practice(request, pk):
    practice = get_object_or_404(IELTSPracticeSet, pk=pk, is_published=True)
    linked_profile = StudentProfile.objects.filter(user=request.user, is_active=True).first() if request.user.is_authenticated else None
    if not linked_profile or practice.course not in {item.course for item in _student_course_enrollments(linked_profile)}:
        return HttpResponse("This practice is not available in your enrolled courses.", status=403)
    result = None
    if request.method == "POST":
        name = request.POST.get("student_name", "").strip()[:100]
        roll = request.POST.get("student_roll", "").strip()[:40]
        if linked_profile:
            name, roll = linked_profile.name, linked_profile.roll
        if not name:
            messages.error(request, "Please enter your name before starting the practice.")
        else:
            answers = {}
            for key, value in request.POST.items():
                if key.startswith("answer_"):
                    answers[key[7:]] = value.strip()[:5000]
            objective_total = 0
            objective_score = 0
            subjective_response = ""
            subjective_prompt = ""
            for index, question in enumerate(practice.questions or []):
                qtype = str(question.get("type", "objective")).lower()
                answer = answers.get(str(index), "")
                if qtype in {"objective", "choice", "short"} and question.get("answer") is not None:
                    objective_total += 1
                    expected = str(question.get("answer", "")).strip().casefold()
                    if answer.strip().casefold() == expected:
                        objective_score += 1
                elif answer:
                    subjective_response += f"\nQuestion: {question.get('prompt', '')}\nResponse: {answer}\n"
                    subjective_prompt += str(question.get("prompt", "")) + "\n"
            ai_score = None
            feedback = "Objective answers were checked automatically. Subjective responses await teacher review."
            if practice.skill in {"writing", "speaking"} and subjective_response:
                from .ielts_services import score_subjective
                ai_score, feedback = score_subjective(practice.skill, subjective_prompt, subjective_response)
            result = IELTSPracticeAttempt.objects.create(
                practice=practice, student_profile=linked_profile, student_name=name, student_roll=roll,
                answers=answers, objective_score=objective_score,
                total_objective=objective_total, ai_score=ai_score, ai_feedback=feedback,
            )
            return render(request, "students/ielts_practice_result.html", {
                "practice": practice, "attempt": result,
            })
    return render(request, "students/ielts_practice.html", {"practice": practice})


def ielts_submission_receipt(request, receipt_code):
    submission = get_object_or_404(IELTSAssignmentSubmission.objects.select_related("assignment"), receipt_code=receipt_code)
    if request.session.get("owner_access"):
        pass
    elif request.user.is_authenticated:
        profile = StudentProfile.objects.filter(user=request.user, is_active=True).first()
        if not profile or submission.student_profile_id != profile.pk:
            return HttpResponse("This submission belongs to another student account.", status=403)
    elif str(receipt_code) not in request.session.get("ielts_submission_receipts", []):
        return HttpResponse("This private submission link is not available in this browser session.", status=403)
    return render(request, "students/ielts_submission_receipt.html", {"submission": submission})


def ielts_submission_file(request, pk):
    denied = _owner_required(request)
    if denied:
        return denied
    submission = get_object_or_404(IELTSAssignmentSubmission, pk=pk)
    if not submission.file:
        return redirect("ielts_admin_panel")
    return FileResponse(submission.file.open("rb"), as_attachment=True, filename=submission.file.name.rsplit("/", 1)[-1])

def ielts_student_submission_file(request, receipt_code):
    allowed_codes = request.session.get("ielts_submission_receipts", [])
    if str(receipt_code) not in allowed_codes:
        return HttpResponse("This private submission link is not available in this browser session.", status=403)
    submission = get_object_or_404(IELTSAssignmentSubmission, receipt_code=receipt_code)
    if not submission.file:
        return redirect("ielts_submission_receipt", receipt_code=receipt_code)
    return FileResponse(submission.file.open("rb"), as_attachment=True, filename=submission.file.name.rsplit("/", 1)[-1])

def student_csrf_failure(request, reason=""):
    """Recover student login from stale cached CSRF pages without disabling protection."""
    if request.path == "/students/access/" and request.method == "POST":
        return redirect("student_access" + "?csrf_refresh=1")
    return HttpResponse("Security verification failed. Please reload the page and try again.", status=403)


@never_cache
@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def student_access(request):
    """Student access using the roll number and private code issued by an admin."""
    if request.user.is_authenticated and StudentProfile.objects.filter(user=request.user, is_active=True).exists():
        return redirect("student_dashboard")
    if request.GET.get("csrf_refresh") == "1":
        messages.info(request, "Your secure login session was refreshed. Please enter your Roll Number and Access Code again.")
    if request.method == "POST":
        roll = request.POST.get("roll", "").strip()
        access_code = request.POST.get("access_code", "").strip().upper()
        candidates = StudentProfile.objects.filter(roll__iexact=roll, is_active=True).select_related("user")
        profile = next(
            (item for item in candidates if item.access_code and hmac.compare_digest(item.access_code, access_code)),
            None,
        )
        if profile:
            User = get_user_model()
            account = profile.user
            if account is None:
                account = User(username=f"student-{profile.pk}-{secrets.token_hex(5)}", is_active=True)
                account.set_unusable_password()
                account.save()
                profile.user = account
                profile.save(update_fields=["user"])
            elif not account.is_active:
                account.is_active = True
                account.save(update_fields=["is_active"])
            login(request, account, backend="django.contrib.auth.backends.ModelBackend")
            request.session.cycle_key()
            return redirect("student_dashboard")
        messages.error(request, "Roll number or access code is incorrect, or the student profile is inactive.")
    return render(request, "students/student_access.html")


def student_logout(request):
    if request.user.is_authenticated and not request.session.get("owner_access"):
        logout(request)
    return redirect("student_access")


def _student_course_enrollments(profile):
    enrollments = list(StudentCourse.objects.filter(student=profile, is_active=True).order_by("course"))
    if not enrollments:
        enrollments = [StudentCourse(student=profile, course=profile.course, modules=profile.modules or [],
                                     joining_date=profile.joining_date, course_finish_date=profile.course_finish_date)]
    return enrollments


def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("student_access")
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first()
    if not profile:
        logout(request)
        messages.error(request, "No active student profile is linked to this account. Please contact your teacher.")
        return redirect("student_access")
    if request.method == "POST" and request.POST.get("action") == "update_student_information":
        profile.email = request.POST.get("email", "").strip()[:254]
        profile.address = request.POST.get("address", "").strip()
        profile.country = request.POST.get("country", "").strip()[:100]
        profile.city = request.POST.get("city", "").strip()[:100]
        profile.cell_phone = request.POST.get("cell_phone", "").strip()[:30]
        raw_dob = request.POST.get("date_of_birth", "").strip()
        try:
            profile.date_of_birth = datetime.strptime(raw_dob, "%Y-%m-%d").date() if raw_dob else None
        except ValueError:
            messages.error(request, "Enter a valid date of birth.")
            return redirect("student_dashboard")
        profile.save(update_fields=["email", "address", "country", "city", "cell_phone", "date_of_birth"])
        if profile.user_id and profile.email and profile.user.email != profile.email:
            profile.user.email = profile.email
            profile.user.save(update_fields=["email"])
        messages.success(request, "Your information has been updated.")
        return redirect("student_dashboard")
    enrollments = _student_course_enrollments(profile)
    courses = [item.course for item in enrollments]
    first_sign_in = AttendanceRecord.objects.filter(student=profile, sign_in__isnull=False).order_by("class_date", "created_at").first()
    if first_sign_in and not profile.joining_date:
        profile.joining_date = first_sign_in.class_date
        profile.save(update_fields=["joining_date"])
    return render(request, "students/student_dashboard.html", {
        "student": profile,
        "student_first_name": profile.name.strip().split()[0] if profile.name.strip() else "Student",
        "course_enrollments": enrollments,
        "attendance_records": AttendanceRecord.objects.filter(student=profile).order_by("-class_date", "-created_at")[:200],
        "submissions": IELTSAssignmentSubmission.objects.filter(student_profile=profile).select_related("assignment")[:100],
        "practice_attempts": IELTSPracticeAttempt.objects.filter(student_profile=profile).select_related("practice")[:100],
        "notices": IELTSNotice.objects.filter(course__in=courses, is_published=True).filter(Q(student__isnull=True) | Q(student=profile))[:100],
        "materials": IELTSMaterial.objects.filter(course__in=courses, is_published=True)[:100],
        "lessons": IELTSLesson.objects.filter(course__in=courses, is_published=True)[:100],
        "assignments": IELTSAssignment.objects.filter(course__in=courses, is_published=True)[:100],
        "practice_sets": IELTSPracticeSet.objects.filter(course__in=courses, is_published=True)[:100],
        "countries": ["Afghanistan", "Australia", "Bangladesh", "Canada", "China", "France", "Germany", "India", "Italy", "Japan", "Malaysia", "Nepal", "Pakistan", "Saudi Arabia", "Singapore", "South Korea", "United Arab Emirates", "United Kingdom", "United States"],
        "country_cities": {"Bangladesh": ["Dhaka", "Chattogram", "Sylhet", "Rajshahi", "Khulna", "Barishal", "Rangpur", "Mymensingh", "Cumilla", "Cox's Bazar"], "India": ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bengaluru", "Hyderabad"], "United States": ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco"], "United Kingdom": ["London", "Manchester", "Birmingham", "Liverpool", "Edinburgh"], "Canada": ["Toronto", "Vancouver", "Montreal", "Ottawa", "Calgary"], "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"], "Malaysia": ["Kuala Lumpur", "George Town", "Johor Bahru"], "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina"], "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah"], "Nepal": ["Kathmandu", "Pokhara", "Lalitpur"], "Pakistan": ["Karachi", "Lahore", "Islamabad"]},
    })

def ielts_admin_panel(request):
    """Teacher tools are protected by the existing private owner session."""
    denied = _owner_required(request)
    if denied:
        return denied
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "notice":
            title = request.POST.get("title", "").strip()[:180]
            message = request.POST.get("message", "").strip()
            if title and message and request.POST.get("course") in COURSE_MODULES:
                target_id = request.POST.get("student_id", "").strip()
                target_student = get_object_or_404(StudentProfile, pk=target_id, is_active=True) if target_id else None
                if target_student and not StudentCourse.objects.filter(student=target_student, course=request.POST["course"], is_active=True).exists():
                    messages.error(request, "The selected student is not enrolled in this course.")
                else:
                    IELTSNotice.objects.create(title=title, message=message, course=request.POST["course"], student=target_student, is_published=True)
                    messages.success(request, f"Notice published for {target_student.name}." if target_student else "Notice published for all students in this course.")
            else:
                messages.error(request, "Enter both a notice title and details.")
        elif action == "notice_edit":
            notice = get_object_or_404(IELTSNotice, pk=request.POST.get("notice_id"))
            title = request.POST.get("title", "").strip()[:180]
            message = request.POST.get("message", "").strip()
            if title and message:
                notice.title, notice.message = title, message
                target_id = request.POST.get("student_id", "").strip()
                target_student = get_object_or_404(StudentProfile, pk=target_id, is_active=True) if target_id else None
                if target_student and not StudentCourse.objects.filter(student=target_student, course=notice.course, is_active=True).exists():
                    messages.error(request, "The selected student is not enrolled in this notice's course.")
                else:
                    notice.student = target_student
                    notice.save(update_fields=["title", "message", "student", "updated_at"])
                messages.success(request, "Notice updated successfully.")
            else:
                messages.error(request, "Notice title and details cannot be empty.")
        elif action == "notice_delete":
            notice = get_object_or_404(IELTSNotice, pk=request.POST.get("notice_id"))
            notice.delete()
            messages.success(request, "Notice deleted successfully.")
        elif action == "assignment":
            title = request.POST.get("title", "").strip()[:180]
            instructions = request.POST.get("instructions", "").strip()
            try:
                duration = max(1, min(180, int(request.POST.get("time_minutes", 40))))
                min_words = max(1, min(5000, int(request.POST.get("min_words", 250))))
                max_words = max(min_words, min(5000, int(request.POST.get("max_words", 350))))
            except (TypeError, ValueError):
                duration, min_words, max_words = 40, 250, 350
            if title and instructions:
                course = request.POST.get("course", "")
                if course in COURSE_MODULES:
                    IELTSAssignment.objects.create(title=title, instructions=instructions, course=course, time_minutes=duration, min_words=min_words, max_words=max_words, is_published=True)
                    messages.success(request, f"{course} assignment published.")
                else:
                    messages.error(request, "Select a valid course for this assignment.")
        elif action == "material":
            title = request.POST.get("title", "").strip()[:180]
            if title and request.POST.get("course") in COURSE_MODULES:
                IELTSMaterial.objects.create(
                    title=title, course=request.POST["course"], description=request.POST.get("description", ""),
                    category=request.POST.get("category", "general"),
                    resource_url=request.POST.get("resource_url", "").strip(),
                    file=request.FILES.get("material_file"),
                )
                messages.success(request, "Course material added.")
        elif action == "lesson":
            title = request.POST.get("title", "").strip()[:180]
            content = request.POST.get("content", "").strip()
            if title and content and request.POST.get("course") in COURSE_MODULES:
                IELTSLesson.objects.create(
                    title=title, course=request.POST["course"], content=content, summary=request.POST.get("summary", "")[:280],
                    skill=request.POST.get("skill", "general"),
                    order=int(request.POST.get("order", 0) or 0),
                )
                messages.success(request, "Lesson published.")
        elif action == "practice":
            title = request.POST.get("title", "").strip()[:180]
            try:
                questions = json.loads(request.POST.get("questions_json", "[]"))
                if not isinstance(questions, list):
                    raise ValueError("Questions must be a JSON list.")
                duration = max(1, min(180, int(request.POST.get("time_minutes", 20))))
                if title and questions:
                    course = request.POST.get("course", "")
                    if course not in COURSE_MODULES:
                        raise ValueError("Select a valid course for this practice set.")
                    IELTSPracticeSet.objects.create(
                        title=title, course=course, skill=request.POST.get("skill", "reading"),
                        instructions=request.POST.get("instructions", ""),
                        time_minutes=duration, questions=questions, is_published=True,
                    )
                    messages.success(request, "Timed practice set published.")
            except (ValueError, TypeError, json.JSONDecodeError):
                messages.error(request, "Practice questions must be valid JSON in a list.")
        elif action == "student_registration":
            try:
                username = request.POST.get("username", "").strip()
                email = request.POST.get("email", "").strip().lower()
                password = request.POST.get("password", "")
                name = request.POST.get("student_name", "").strip()[:120]
                roll = request.POST.get("roll", "").strip()[:40]
                course = request.POST.get("course", "")
                all_modules = request.POST.get("all_modules") == "1"
                valid_modules = COURSE_MODULES.get(course, [])
                selected = request.POST.getlist("modules")
                modules = list(valid_modules) if all_modules else [item for item in selected if item in valid_modules]
                joining_raw = request.POST.get("joining_date", "").strip()
                finish_raw = request.POST.get("course_finish_date", "").strip()
                joining_date = datetime.strptime(joining_raw, "%Y-%m-%d").date() if joining_raw else None
                finish_date = datetime.strptime(finish_raw, "%Y-%m-%d").date() if finish_raw else None
                if not username or len(username) > 150:
                    raise ValueError("Enter a valid username (maximum 150 characters).")
                if not email or "@" not in email:
                    raise ValueError("Enter a valid email address.")
                if not name:
                    raise ValueError("Enter the student's full name.")
                if course not in COURSE_MODULES or not modules:
                    raise ValueError("Choose a course and at least one module, or select All.")
                if joining_date and finish_date and finish_date < joining_date:
                    raise ValueError("Course finish date cannot be before the joining date.")
                User = get_user_model()
                if User.objects.filter(username__iexact=username).exists():
                    raise ValueError("This username is already registered.")
                if User.objects.filter(email__iexact=email).exists():
                    raise ValueError("This email is already registered.")
                account = User(username=username, email=email, is_active=True)
                validate_password(password, account)
                account.set_password(password)
                with transaction.atomic():
                    account.save()
                    profile, created = StudentProfile.objects.get_or_create(
                        name=name, roll=roll, course=course,
                        defaults={"modules": modules, "user": account, "joining_date": joining_date, "course_finish_date": finish_date, "is_active": True},
                    )
                    if not created:
                        if profile.user_id:
                            raise ValueError("A student profile with this name/course/roll already has an account.")
                        profile.modules = modules
                        profile.user = account
                        profile.joining_date = joining_date
                        profile.course_finish_date = finish_date
                        profile.is_active = True
                        profile.save()
                    StudentCourse.objects.update_or_create(
                        student=profile, course=course,
                        defaults={"modules": modules, "joining_date": joining_date, "course_finish_date": finish_date, "is_active": True},
                    )
                messages.success(request, f"Student registration completed for {name}. Login uses {email}.")
            except ValidationError as exc:
                messages.error(request, "Password does not meet security requirements: " + " ".join(exc.messages))
            except (ValueError, TypeError) as exc:
                messages.error(request, str(exc))
        elif action == "student_course_add":
            try:
                profile = get_object_or_404(StudentProfile, pk=request.POST.get("student_profile_id"), is_active=True)
                course = request.POST.get("course", "")
                if course not in COURSE_MODULES:
                    raise ValueError("Select a valid course.")
                selected = request.POST.getlist("modules")
                all_modules = request.POST.get("all_modules") == "1"
                modules = list(COURSE_MODULES[course]) if all_modules else [item for item in selected if item in COURSE_MODULES[course]]
                if not modules:
                    raise ValueError("Select at least one module or choose All modules.")
                joining_raw = request.POST.get("joining_date", "").strip()
                finish_raw = request.POST.get("course_finish_date", "").strip()
                joining_date = datetime.strptime(joining_raw, "%Y-%m-%d").date() if joining_raw else None
                finish_date = datetime.strptime(finish_raw, "%Y-%m-%d").date() if finish_raw else None
                if joining_date and finish_date and finish_date < joining_date:
                    raise ValueError("Course finish date cannot be before the joining date.")
                StudentCourse.objects.update_or_create(
                    student=profile, course=course,
                    defaults={"modules": modules, "joining_date": joining_date, "course_finish_date": finish_date, "is_active": True},
                )
                messages.success(request, f"{course} enrolled for {profile.name}.")
            except (ValueError, TypeError) as exc:
                messages.error(request, str(exc))
        elif action == "student_account_update":
            try:
                profile = get_object_or_404(StudentProfile, pk=request.POST.get("student_profile_id"), is_active=True)
                if not profile.user_id:
                    raise ValueError("This student has no login account yet. Register the student first.")
                account = profile.user
                username = request.POST.get("username", "").strip()
                email = request.POST.get("email", "").strip().lower()
                password = request.POST.get("password", "")
                User = get_user_model()
                if not username or not email or "@" not in email:
                    raise ValueError("Enter a valid username and email address.")
                if User.objects.filter(username__iexact=username).exclude(pk=account.pk).exists():
                    raise ValueError("This username is already used by another account.")
                if User.objects.filter(email__iexact=email).exclude(pk=account.pk).exists():
                    raise ValueError("This email is already used by another account.")
                account.username, account.email = username, email
                if password:
                    validate_password(password, account)
                    account.set_password(password)
                account.save()
                messages.success(request, f"Student account updated for {profile.name}.")
            except ValidationError as exc:
                messages.error(request, "Password does not meet security requirements: " + " ".join(exc.messages))
            except ValueError as exc:
                messages.error(request, str(exc))
        elif action == "attendance_student":
            name = request.POST.get("name", "").strip()[:120]
            roll = request.POST.get("roll", "").strip()[:40]
            course = request.POST.get("course", "")
            modules = [m for m in request.POST.getlist("modules") if m in COURSE_MODULES.get(course, [])]
            if not name or course not in COURSE_MODULES or not modules:
                messages.error(request, "Enter a student name, course and at least one assigned module.")
            else:
                profile, _ = StudentProfile.objects.update_or_create(name=name, roll=roll, course=course, defaults={"modules": modules, "is_active": True})
                StudentCourse.objects.update_or_create(student=profile, course=course, defaults={"modules": modules, "is_active": True})
                messages.success(request, f"Student profile saved for {name}.")
        elif action in {"manual_attendance", "edit_attendance"}:
            try:
                student = get_object_or_404(StudentProfile, pk=int(request.POST.get("student_id")), is_active=True)
                class_date = datetime.strptime(request.POST.get("class_date", ""), "%Y-%m-%d").date()
                period = request.POST.get("period", "")
                module = request.POST.get("module", "")
                course = request.POST.get("course", "")
                enrollment = StudentCourse.objects.filter(student=student, course=course, is_active=True).first()
                if period not in AttendanceRecord.Period.values or not enrollment or module not in (enrollment.modules or []):
                    raise ValueError
                record = get_object_or_404(AttendanceRecord, pk=request.POST.get("attendance_id")) if action == "edit_attendance" else None
                if record:
                    record.student, record.class_date, record.period = student, class_date, period
                else:
                    record = AttendanceRecord.objects.create(
                        class_date=class_date, student=student, period=period,
                        course_name=student.course, module_name=module,
                    )
                record.course_name, record.module_name = course, module
                record.sign_in = datetime.strptime(request.POST["sign_in"], "%H:%M").time() if request.POST.get("sign_in") else None
                record.sign_out = datetime.strptime(request.POST["sign_out"], "%H:%M").time() if request.POST.get("sign_out") else None
                record.sign_out_date = class_date if record.sign_out else None
                record.save()
                messages.success(request, f"Attendance {'updated' if action == 'edit_attendance' else 'saved'} for {student.name}.")
            except (ValueError, KeyError, TypeError):
                messages.error(request, "Check the date, student, module and time values.")
        elif action == "delete_attendance":
            get_object_or_404(AttendanceRecord, pk=request.POST.get("attendance_id")).delete()
            messages.success(request, "Attendance entry deleted.")
        elif action == "toggle_attendance_student":
            student = get_object_or_404(StudentProfile, pk=request.POST.get("student_id"))
            student.is_active = not student.is_active
            student.save(update_fields=["is_active"])
            messages.success(request, f"Student {'activated' if student.is_active else 'deactivated'}.")
        elif action == "assignment_submission_edit":
            submission = get_object_or_404(IELTSAssignmentSubmission, pk=request.POST.get("submission_id"))
            submission.student_name = request.POST.get("student_name", "").strip()[:100] or submission.student_name
            submission.student_roll = request.POST.get("student_roll", "").strip()[:40]
            submission.answer_text = request.POST.get("answer_text", "").strip()
            submission.word_count = len(submission.answer_text.split())
            submission.save(update_fields=["student_name", "student_roll", "answer_text", "word_count"])
            messages.success(request, "Assignment attempt edited.")
        elif action == "assignment_submission_delete":
            get_object_or_404(IELTSAssignmentSubmission, pk=request.POST.get("submission_id")).delete()
            messages.success(request, "Assignment attempt deleted.")
        elif action == "assignment_submission_reopen":
            submission = get_object_or_404(IELTSAssignmentSubmission, pk=request.POST.get("submission_id"))
            submission.status = "in_progress"
            submission.paste_attempts = 0
            submission.failed_reason = ""
            submission.started_at = None
            submission.elapsed_seconds = None
            # Keep the student's existing draft so they can continue from where they stopped.
            submission.reviewed_at = None
            submission.save(update_fields=["status", "paste_attempts", "failed_reason", "started_at", "elapsed_seconds", "reviewed_at"])
            messages.success(request, f"Reopened for {submission.student_name}. The saved draft is preserved and the student can continue from their private submission link.")
        elif action == "review_submission":
            submission = get_object_or_404(IELTSAssignmentSubmission, pk=request.POST.get("submission_id"))
            try:
                raw_score = request.POST.get("score", "").strip()
                score_value = float(raw_score) if raw_score else None
                if score_value is not None and not 0 <= score_value <= 100:
                    raise ValueError("Overall score must be between 0 and 100.")
                submission.score = score_value
                for field in ("task_response_band", "coherence_cohesion_band", "lexical_resource_band", "grammatical_range_band"):
                    raw_band = request.POST.get(field, "").strip()
                    band_value = float(raw_band) if raw_band else None
                    if band_value is not None and (band_value < 0 or band_value > 9 or band_value * 2 != int(band_value * 2)):
                        raise ValueError("IELTS criterion bands must be between 0 and 9 in 0.5 steps.")
                    setattr(submission, field, band_value)
                submission.teacher_feedback = request.POST.get("teacher_feedback", "").strip()
                submission.teacher_strengths = request.POST.get("teacher_strengths", "").strip()
                submission.teacher_improvements = request.POST.get("teacher_improvements", "").strip()
                submission.corrected_sentences = request.POST.get("corrected_sentences", "").strip()
                submission.reviewed_at = timezone.now()
                submission.save()
                messages.success(request, "Teacher review published to the student portal.")
            except (ValueError, TypeError):
                messages.error(request, "Please check the overall score and IELTS band scores. Bands must use 0.5 steps.")
        return redirect("ielts_admin_panel")

    return render(request, "students/ielts_admin.html", {
        "notices": IELTSNotice.objects.all()[:12],
        "assignments": IELTSAssignment.objects.all()[:20],
        "submissions": IELTSAssignmentSubmission.objects.select_related("assignment")[:30],
        "materials": IELTSMaterial.objects.all()[:20],
        "lessons": IELTSLesson.objects.all()[:20],
        "practice_sets": IELTSPracticeSet.objects.all()[:20],
        "attendance_students": StudentProfile.objects.all(),
        "active_attendance_students": StudentProfile.objects.filter(is_active=True),
        "attendance_enrollment_data": [{"student_id": row.student_id, "course": row.course, "modules": row.modules or []} for row in StudentCourse.objects.filter(student__is_active=True, is_active=True)],
        "attendance_records": AttendanceRecord.objects.select_related("student").all()[:300],
        "course_modules": COURSE_MODULES,
        "today": timezone.localdate(),
        "attempts": IELTSPracticeAttempt.objects.select_related("practice")[:20],
        "student_profiles": StudentProfile.objects.filter(is_active=True).select_related("user"),
        "student_admin_data": [{
            "id": profile.pk, "name": profile.name, "roll": profile.roll, "access_code": profile.access_code, "course": profile.course,
            "courses": [{"course": item.course, "modules": item.modules or [], "joining_date": item.joining_date.strftime("%d %b %Y") if item.joining_date else "—", "course_finish_date": item.course_finish_date.strftime("%d %b %Y") if item.course_finish_date else "—"} for item in _student_course_enrollments(profile)],
            "modules": profile.modules or [], "username": profile.user.username if profile.user_id else "",
            "email": profile.email or (profile.user.email if profile.user_id else ""), "address": profile.address, "country": profile.country, "city": profile.city, "cell_phone": profile.cell_phone, "date_of_birth": profile.date_of_birth.strftime("%d %b %Y") if profile.date_of_birth else "—", "has_account": bool(profile.user_id),
            "joining_date": profile.joining_date.strftime("%d %b %Y") if profile.joining_date else "—",
            "course_finish_date": profile.course_finish_date.strftime("%d %b %Y") if profile.course_finish_date else "—",
            "attendance": [{"date": row.class_date.strftime("%d %b %Y"), "module": row.module_name, "period": row.period, "in": row.sign_in.strftime("%I:%M %p") if row.sign_in else "—", "out": row.sign_out.strftime("%I:%M %p") if row.sign_out else "—", "duration": row.total_duration} for row in profile.attendance_records.all()[:100]],
            "assignments": [{"title": row.assignment.title, "status": row.get_status_display(), "date": timezone.localtime(row.submitted_at).strftime("%d %b %Y"), "answer": row.answer_text, "feedback": row.teacher_feedback, "receipt": f"/students/ielts/submission/{row.receipt_code}/", "file": f"/owner/ielts/submission/{row.pk}/file/" if row.file else ""} for row in IELTSAssignmentSubmission.objects.filter(Q(student_profile=profile) | Q(student_profile__isnull=True, student_name__iexact=profile.name, student_roll=profile.roll)).select_related("assignment")[:100]],
            "practice": [{"title": row.practice.title, "score": f"{row.objective_score if row.objective_score is not None else '—'} / {row.total_objective if row.total_objective is not None else '—'}", "date": timezone.localtime(row.submitted_at).strftime("%d %b %Y")} for row in IELTSPracticeAttempt.objects.filter(student_name__iexact=profile.name, student_roll=profile.roll).select_related("practice")[:100]],
            "notices": [{"title": row.title, "message": row.message, "date": timezone.localtime(row.created_at).strftime("%d %b %Y")} for row in IELTSNotice.objects.filter(course__in=[item.course for item in _student_course_enrollments(profile)], is_published=True).filter(Q(student__isnull=True) | Q(student=profile))[:40]],
            "materials": [{"title": row.title, "description": row.description, "category": row.get_category_display(), "url": row.resource_url or (f"/students/ielts/material/{row.pk}/download/" if row.file else "")} for row in IELTSMaterial.objects.filter(course__in=[item.course for item in _student_course_enrollments(profile)], is_published=True)[:100]],
            "lessons": [{"title": row.title, "summary": row.summary, "skill": row.get_skill_display()} for row in IELTSLesson.objects.filter(course__in=[item.course for item in _student_course_enrollments(profile)], is_published=True)[:100]],
            "practice_sets": [{"title": row.title, "skill": row.get_skill_display(), "url": f"/students/ielts/practice/{row.pk}/"} for row in IELTSPracticeSet.objects.filter(course__in=[item.course for item in _student_course_enrollments(profile)], is_published=True)[:100]],
        } for profile in StudentProfile.objects.filter(is_active=True).select_related("user")],
    })


def ielts_material_download(request, pk):
    material = get_object_or_404(IELTSMaterial, pk=pk, is_published=True)
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first() if request.user.is_authenticated else None
    if not profile or material.course not in {item.course for item in _student_course_enrollments(profile)}:
        return HttpResponse("This material is not available in your enrolled courses.", status=403)
    if not material.file:
        return redirect(material.resource_url or "ielts_learning")
    return FileResponse(material.file.open("rb"), as_attachment=True, filename=material.file.name.rsplit("/", 1)[-1])




def mikrotik_generator(request):
    """Interactive client-side RouterOS configuration generator."""
    return render(request, "mikrotik_generator.html")


def algorithm_studio(request):
    """Interactive data structure and algorithm learning studio."""
    return render(request, "algorithm_studio.html")


def tki_fresh_dashboard(request):
    """Temporary client-side TKI dashboard. Deliberately reads/writes no persistent storage."""
    return render(request, "tki_fresh_dashboard.html")


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

    if report_period == "daily":
        solved_tickets = all_tickets.filter(status=ComplaintTicket.Status.SOLVED, resolved_at__date=now.date())
    else:
        solved_tickets = all_tickets.filter(
            status=ComplaintTicket.Status.SOLVED,
            resolved_at__year=now.year,
            resolved_at__month=now.month,
        )
    field_completion_report = []
    for value, label in ComplaintTicket.SupportEngineer.choices:
        engineer_solved = solved_tickets.filter(field_support_engineer=value)
        field_completion_report.append({
            "value": value,
            "label": label,
            "solved": engineer_solved.count(),
            "support_done": engineer_solved.filter(field_support_done=True).count(),
        })
    phone_sla_report = []
    phone_solved = solved_tickets.filter(support_type=ComplaintTicket.SupportType.PHONE)
    for value, label in ComplaintTicket.ReceivedBy.choices:
        handled = phone_solved.filter(support_by=value)
        total_handled = handled.count()
        met = sum(1 for item in handled if not item.sla_breached)
        phone_sla_report.append({
            "value": value, "label": label, "solved": total_handled,
            "met": met, "breached": total_handled - met,
            "compliance": round(met / total_handled * 100) if total_handled else 0,
        })

    field_rating_report = []
    for value, label in ComplaintTicket.SupportEngineer.choices:
        handled = solved_tickets.filter(field_support_engineer=value)
        met = sum(1 for item in handled if not item.sla_breached)
        breached = max(0, handled.count() - met)
        repeat_penalties = report_tickets.filter(
            repeat_reason=ComplaintTicket.RepeatReason.ENGINEER,
            repeat_engineer=value,
        ).count()
        field_rating_report.append({
            "value": value, "label": label, "solved": handled.count(),
            "sla_met": met, "sla_breached": breached,
            "repeat_penalties": repeat_penalties, "score": met - breached - repeat_penalties,
        })

    performance_report = []
    for value, label in ComplaintTicket.ReceivedBy.choices:
        handled = solved_tickets.filter(support_by=value)
        if value in dict(ComplaintTicket.SupportEngineer.choices):
            handled = handled | solved_tickets.filter(field_support_engineer=value)
        handled = handled.distinct()
        met = sum(1 for item in handled if not item.sla_breached)
        breached = max(0, handled.count() - met)
        repeat_penalties = report_tickets.filter(
            repeat_reason=ComplaintTicket.RepeatReason.ENGINEER,
            repeat_engineer=value,
        ).count()
        score = met - breached - repeat_penalties
        performance_report.append({
            "value": value, "label": label, "solved": handled.count(),
            "sla_met": met, "sla_breached": breached,
            "repeat_penalties": repeat_penalties, "score": score,
        })

    noc_completion_report = []
    for value, label in ComplaintTicket.NocEngineer.choices:
        engineer_solved = solved_tickets.filter(higher_level_noc=value)
        noc_completion_report.append({
            "value": value,
            "label": label,
            "solved": engineer_solved.count(),
            "field_visits": engineer_solved.filter(noc_field_visit_done=True).count(),
            "support_done": engineer_solved.filter(noc_field_visit_done=True).count(),
        })

    # This chart is an active-work view: completed/cancelled tickets must not
    # inflate the pending dependency workload.
    pending_dependency_tickets = report_tickets.filter(status=ComplaintTicket.Status.PENDING)
    dependency_report = []
    visible_dependencies = tuple(
        choice for choice in ComplaintTicket.Dependency.choices
        if choice[0] != ComplaintTicket.Dependency.ISP
    )
    dependency_total = max(pending_dependency_tickets.exclude(dependency="").exclude(dependency=ComplaintTicket.Dependency.ISP).count(), 1)
    dependency_colors = ["#32d399", "#55b8ff", "#f6bd47", "#a78bfa", "#fb7185"]
    gradient_stops = []
    cursor = 0
    for index, (value, label) in enumerate(visible_dependencies):
        count = pending_dependency_tickets.filter(dependency=value).count()
        percent = round(count / dependency_total * 100)
        color = dependency_colors[index]
        if count:
            gradient_stops.append(f"{color} {cursor}% {cursor + percent}%")
            cursor += percent
        dependency_report.append({"value": value, "label": label, "count": count, "percent": percent, "color": color})
    dependency_gradient = "conic-gradient(" + (", ".join(gradient_stops) if gradient_stops else "#334155 0 100%") + ")"
    sla_breaches = sum(1 for item in report_tickets if item.status == ComplaintTicket.Status.SOLVED and item.sla_breached)
    return render(request, "tki/dashboard.html", {
        "tickets": tickets[:150], "engineers": engineers, "workload": workload,
        "summary": summary, "statuses": (
            (ComplaintTicket.Status.PENDING, ComplaintTicket.Status.PENDING.label),
            (ComplaintTicket.Status.SOLVED, ComplaintTicket.Status.SOLVED.label),
        ),
        "support_engineers": ComplaintTicket.SupportEngineer.choices,
        "report_period": report_period, "engineer_report": engineer_report,
        "dependency_report": dependency_report, "dependency_gradient": dependency_gradient,
        "pending_dependency_total": pending_dependency_tickets.exclude(dependency="").exclude(dependency=ComplaintTicket.Dependency.ISP).count(),
        "field_completion_report": field_completion_report,
        "noc_completion_report": noc_completion_report,
        "phone_sla_report": phone_sla_report,
        "performance_report": performance_report,
        "field_rating_report": field_rating_report,
        "can_edit_tki": bool(request.session.get("owner_access")),
        "current_month": now.strftime("%Y-%m"),
        "pending_tickets": tickets.filter(status=ComplaintTicket.Status.PENDING)[:100],
        "solved_tickets": tickets.filter(status=ComplaintTicket.Status.SOLVED)[:100],
        "sla_breaches": sla_breaches,
        "sla_compliant_solved": max(0, report_tickets.filter(status=ComplaintTicket.Status.SOLVED).count() - sla_breaches),
        "repeat_issues": report_tickets.exclude(repeat_reason="").count(),
        "repeat_engineer_issues": report_tickets.filter(repeat_reason=ComplaintTicket.RepeatReason.ENGINEER).count(),
    })


def tki_export_xlsx(request):
    if not _owner_can_manage_tki(request):
        messages.error(request, "Owner access is required to export TKI data.")
        return redirect("owner_login")

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    start, end = _month_bounds(request.GET.get("month"))
    tickets = ComplaintTicket.objects.filter(opened_at__range=(start, end)).order_by("opened_at", "id")
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "TKI Report"
    dark = "102033"
    green = "35D69A"
    muted = "DCE7F2"
    thin = Side(style="thin", color="CAD6E2")

    sheet.merge_cells("A1:X1")
    sheet["A1"] = f"ISP TKI Monthly Report — {start.strftime('%B %Y')}"
    sheet["A1"].font = Font(size=18, bold=True, color="FFFFFF")
    sheet["A1"].fill = PatternFill("solid", fgColor=dark)
    sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")
    sheet.row_dimensions[1].height = 34

    counts = {
        "Total": tickets.count(),
        "Pending": tickets.filter(status=ComplaintTicket.Status.PENDING).count(),
        "Solved": tickets.filter(status=ComplaintTicket.Status.SOLVED).count(),
        "Cancelled": tickets.filter(status=ComplaintTicket.Status.CANCELLED).count(),
    }
    for column, (label, count) in enumerate(counts.items(), 1):
        cell = sheet.cell(3, column, f"{label}: {count}")
        cell.font = Font(bold=True, color=dark)
        cell.fill = PatternFill("solid", fgColor="E8F8F1")

    headers = ["Date", "Time", "TKI ID", "Client Code", "Status", "Dependency", "Higher-Level NOC", "NOC Field Visit", "Field Support Engineer", "Field Support Done", "Remarks", "Aging", "Attention", "Issue", "Received By", "Support By", "Support Type", "Visited By", "Solved At", "Status Type", "SLA Target (h)", "SLA Elapsed", "SLA Result", "Repeat Reason / Notes"]
    for column, label in enumerate(headers, 1):
        cell = sheet.cell(5, column, label)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=dark)
        cell.alignment = Alignment(horizontal="center")

    def safe_text(value):
        text = str(value or "")
        return "'" + text if text.startswith(("=", "+", "-", "@")) else text

    status_colors = {"pending": "FFF2CC", "solved": "D9EAD3", "cancelled": "F4CCCC"}
    for row_number, ticket in enumerate(tickets, 6):
        local_opened = timezone.localtime(ticket.opened_at)
        values = [
            local_opened.date(), local_opened.time().replace(microsecond=0), safe_text(ticket.tki_id),
            safe_text(ticket.client_id), ticket.get_status_display(), ticket.get_dependency_display() or "None",
            ticket.get_higher_level_noc_display() or "—", "Done" if ticket.noc_field_visit_done else "No",
            ticket.get_field_support_engineer_display() or "—", "Done" if ticket.field_support_done else "No",
            safe_text(ticket.remarks or ticket.complaint), ticket.aging,
            "Required" if ticket.attention else "Normal", ticket.get_category_display(),
            ticket.get_received_by_display() or "—", ticket.get_support_by_display() or "—",
            ticket.get_support_type_display(), ticket.get_visited_by_display() or "—",
            timezone.localtime(ticket.resolved_at).strftime("%Y-%m-%d %H:%M") if ticket.resolved_at else "—",
            ticket.get_status_type_display(), ticket.sla_hours, ticket.sla_elapsed_display,
            "Breached" if ticket.sla_breached else "Met",
            (ticket.get_repeat_reason_display() or "—") + (": " + ticket.repeat_note if ticket.repeat_note else ""),
        ]
        for column, value in enumerate(values, 1):
            cell = sheet.cell(row_number, column, value)
            cell.border = Border(bottom=thin)
            cell.alignment = Alignment(vertical="top", wrap_text=column in {11, 14})
        sheet.cell(row_number, 5).fill = PatternFill("solid", fgColor=status_colors.get(ticket.status, muted))

    widths = [13, 12, 18, 16, 13, 20, 20, 16, 23, 18, 42, 12, 14, 22, 16, 16, 16, 16, 20, 12, 14, 14, 14, 38]
    for column, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(column)].width = width
    sheet.freeze_panes = "A6"
    sheet.auto_filter.ref = f"A5:X{max(sheet.max_row, 5)}"
    sheet.sheet_view.showGridLines = False
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.fitToWidth = 1

    output = BytesIO()
    workbook.save(output)
    response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="ISP-TKI-{start.strftime("%Y-%m")}.xlsx"'
    return response


@require_POST
def tki_delete_month(request):
    if not _owner_can_manage_tki(request):
        messages.error(request, "Owner access is required to delete TKI data.")
        return redirect("owner_login")
    if request.POST.get("confirm", "").strip().upper() != "DELETE":
        messages.error(request, "Type DELETE to confirm the monthly deletion.")
        return redirect("tki_dashboard")
    start, end = _month_bounds(request.POST.get("month"))
    queryset = ComplaintTicket.objects.filter(opened_at__range=(start, end))
    count = queryset.count()
    queryset.delete()
    messages.success(request, f"{count} TKI record(s) from {start.strftime('%B %Y')} were deleted.")
    return redirect("tki_dashboard")


@require_POST
def tki_delete_range(request):
    if not _owner_can_manage_tki(request):
        messages.error(request, "Owner access is required to delete TKI data.")
        return redirect("owner_login")
    if request.POST.get("confirm", "").strip().upper() != "DELETE":
        messages.error(request, "Type DELETE to confirm the date-range deletion.")
        return redirect("tki_dashboard")
    try:
        start_date = datetime.strptime(request.POST.get("start_date", ""), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.POST.get("end_date", ""), "%Y-%m-%d").date()
        if end_date < start_date:
            raise ValueError("End date is before start date")
    except (TypeError, ValueError):
        messages.error(request, "Choose a valid start and end date.")
        return redirect("tki_dashboard")
    start = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    queryset = ComplaintTicket.objects.filter(opened_at__range=(start, end))
    count = queryset.count()
    queryset.delete()
    messages.success(request, f"{count} TKI record(s) from {start_date} to {end_date} were deleted.")
    return redirect("tki_dashboard")


@require_POST
def tki_import_solved(request):
    if not _owner_can_manage_tki(request):
        messages.error(request, "Owner access is required to import TKI data.")
        return redirect("owner_login")
    upload = request.FILES.get("tki_file")
    if not upload:
        messages.error(request, "Select a .txt or .tsv file to import.")
        return redirect("tki_dashboard")
    if upload.size > 2 * 1024 * 1024:
        messages.error(request, "The import file must be smaller than 2 MB.")
        return redirect("tki_dashboard")
    try:
        # Accept standard UTF-8/BOM and Excel's Unicode Text (UTF-16) export.
        # Unicode content, including Bangla, is preserved without transliteration.
        text = decode_tki_upload(upload.read())
    except UnicodeDecodeError:
        messages.error(request, "Fileটি UTF-8 অথবা Excel Unicode Text হিসেবে save করুন। বাংলা লেখা সম্পূর্ণভাবে supported।")
        return redirect("tki_dashboard")
    result = import_solved_tsv(text, ComplaintTicket)
    messages.success(request, f"Solved TKI import complete: {result['created']} created, {result['updated']} updated, {result['skipped']} skipped.")
    return redirect("tki_dashboard")


def tki_detail(request, pk):
    ticket = get_object_or_404(ComplaintTicket.objects.select_related("assigned_engineer", "created_by"), pk=pk)
    form = EngineerTicketUpdateForm(instance=ticket)
    return render(request, "tki/detail.html", {
        "ticket": ticket, "form": form,
        "can_update": bool(request.session.get("owner_access")),
        "can_edit_tki": bool(request.session.get("owner_access")),
    })


@require_POST
def tki_update(request, pk):
    if not request.session.get("owner_access"):
        messages.error(request, "Owner access is required to update TKI records.")
        return redirect("owner_login")
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
        "can_edit_tki": True,
    }, status=400)


def tki_create(request):
    if not request.session.get("owner_access"):
        messages.error(request, "Owner access is required to create TKI records.")
        return redirect("owner_login")
    form = AdminTicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.created_by = request.user if request.user.is_authenticated else None
        repeat_exists = ComplaintTicket.objects.filter(
            client_id__iexact=ticket.client_id,
            opened_at__year=ticket.opened_at.year,
            opened_at__month=ticket.opened_at.month,
        ).exists()
        if repeat_exists:
            ticket.status_type = ComplaintTicket.StatusType.REPEAT
        if repeat_exists and not ticket.repeat_reason:
            ticket.repeat_reason = ComplaintTicket.RepeatReason.OTHER
            ticket.repeat_note = (ticket.repeat_note + "\n" if ticket.repeat_note else "") + "Auto-flagged: repeated Client ID in the same month; classify reason."
        if ticket.status == ComplaintTicket.Status.SOLVED and not ticket.resolved_at:
            ticket.resolved_at = timezone.now()
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
    if not request.session.get("owner_access"):
        messages.error(request, "Owner access is required to edit TKI records.")
        return redirect("owner_login")
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


# Private OLT monitoring dashboard. Live data is accepted only from a token-authenticated collector.
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import hmac
import json
from datetime import timedelta

from .models import OLTDevice, ONUStatus, OLTEvent


def _owner_required(request):
    if not request.session.get("owner_access"):
        return redirect("owner_login")
    return None


def olt_monitoring_dashboard(request):
    denied = _owner_required(request)
    if denied:
        return denied

    devices = list(OLTDevice.objects.annotate(
        online_count=Count("onus", filter=Q(onus__status=ONUStatus.Status.ONLINE)),
        offline_count=Count("onus", filter=Q(onus__status=ONUStatus.Status.OFFLINE)),
        unknown_count=Count("onus", filter=Q(onus__status=ONUStatus.Status.UNKNOWN)),
    ))
    last_seen = OLTDevice.objects.order_by("-last_seen").values_list("last_seen", flat=True).first()
    now = timezone.now()
    totals = {
        "olts": len(devices),
        "online": sum(device.online_count for device in devices),
        "offline": sum(device.offline_count for device in devices),
        "unknown": sum(device.unknown_count for device in devices),
        "events": OLTEvent.objects.filter(occurred_at__gte=now - timedelta(hours=24)).count(),
    }
    pon_summary = list(
        ONUStatus.objects.values("olt__name", "olt__identifier", "pon_port")
        .annotate(
            total_count=Count("id"),
            online_count=Count("id", filter=Q(status=ONUStatus.Status.ONLINE)),
            offline_count=Count("id", filter=Q(status=ONUStatus.Status.OFFLINE)),
            unknown_count=Count("id", filter=Q(status=ONUStatus.Status.UNKNOWN)),
        )
        .order_by("olt__name", "pon_port")
    )
    return render(request, "olt_monitoring_dashboard.html", {
        "devices": devices,
        "last_seen": last_seen,
        "collector_connected": bool(last_seen and last_seen >= now - timedelta(minutes=10)),
        "totals": totals,
        "pon_summary": pon_summary,
        "recent_events": OLTEvent.objects.select_related("olt").order_by("-occurred_at")[:30],
    })

@csrf_exempt
@require_POST
def olt_ingest(request):
    expected = os.environ.get("OLT_INGEST_TOKEN", "")
    auth = request.headers.get("Authorization", "")
    supplied = auth[7:] if auth.startswith("Bearer ") else ""
    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if len(request.body) > 2 * 1024 * 1024:
        return JsonResponse({"error": "Payload too large (maximum 2 MiB)"}, status=413)
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Expected a JSON payload"}, status=400)
    if not isinstance(payload, dict) or not isinstance(payload.get("olt"), dict) or not isinstance(payload.get("onus"), list):
        return JsonResponse({"error": "Payload must contain an olt object and onus array"}, status=400)
    info = payload["olt"]
    identifier = str(info.get("identifier", "")).strip()
    name = str(info.get("name", "")).strip()
    vendor = str(info.get("vendor", "other")).strip().lower()
    if not identifier or len(identifier) > 80 or not name or len(name) > 120:
        return JsonResponse({"error": "OLT identifier (max 80) and name (max 120) are required"}, status=400)
    if vendor not in {"huawei", "vsol", "cdata", "other", "zte"}:
        vendor = "other"
    try:
        pon_count = int(info.get("pon_port_count", 0))
        if not 0 <= pon_count <= 4096:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"error": "pon_port_count must be between 0 and 4096"}, status=400)
    raw_ip = info.get("management_ip")
    normalized_ip = None
    if raw_ip:
        import ipaddress
        try:
            normalized_ip = str(ipaddress.ip_address(raw_ip))
        except ValueError:
            return JsonResponse({"error": "Invalid management_ip"}, status=400)
    if len(payload["onus"]) > 20000:
        return JsonResponse({"error": "Maximum 20,000 ONU records per report"}, status=413)
    normalized = []
    seen = set()
    for item in payload["onus"]:
        if not isinstance(item, dict):
            return JsonResponse({"error": "Every ONU record must be an object"}, status=400)
        onu_id = str(item.get("id", "")).strip()
        status = str(item.get("status", "unknown")).strip().lower()
        port = str(item.get("pon_port", "")).strip()[:40]
        serial = str(item.get("serial_number", "")).strip()[:100]
        if not onu_id or len(onu_id) > 100 or status not in {"online", "offline", "unknown"}:
            return JsonResponse({"error": "Each ONU needs an id (max 100) and valid status"}, status=400)
        if onu_id in seen:
            return JsonResponse({"error": "Duplicate ONU id in report"}, status=400)
        seen.add(onu_id)
        normalized.append((onu_id, status, port, serial))

    now = timezone.now()
    with transaction.atomic():
        olt, _ = OLTDevice.objects.get_or_create(identifier=identifier, defaults={"name": name, "vendor": vendor})
        olt.name = name
        olt.vendor = vendor
        olt.location = str(info.get("location", ""))[:160]
        olt.pon_port_count = pon_count
        olt.management_ip = normalized_ip
        olt.last_seen = now
        olt.save()
        created = 0
        updated = 0
        events = 0
        for onu_id, status, port, serial in normalized:
            onu, is_new = ONUStatus.objects.get_or_create(
                olt=olt, onu_id=onu_id,
                defaults={"pon_port": port, "status": status, "serial_number": serial, "last_seen": now},
            )
            if is_new:
                created += 1
                if status in {"online", "offline"}:
                    OLTEvent.objects.create(olt=olt, onu_id=onu_id, pon_port=port, event_type=status, occurred_at=now, details="Initial observed state")
                    events += 1
                continue
            previous = onu.status
            if previous != status:
                if previous in {"online", "offline"} and status in {"online", "offline"}:
                    OLTEvent.objects.create(olt=olt, onu_id=onu_id, pon_port=port, event_type=status, occurred_at=now, details=f"State changed from {previous}")
                    events += 1
                onu.status_changed_at = now
            onu.pon_port = port
            onu.status = status
            onu.serial_number = serial
            onu.last_seen = now
            onu.save()
            updated += 1
    return JsonResponse({"ok": True, "olt": identifier, "created_onus": created, "updated_onus": updated, "events_created": events, "received_at": now.isoformat()})
