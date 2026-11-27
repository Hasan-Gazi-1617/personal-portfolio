import re
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from attendance.models import StudentProfile, StudentCourse
from .models import BCSExam, BCSQuestion, BCSAttempt


def _student_profile(request):
    if not request.user.is_authenticated:
        raise PermissionDenied
    profile = StudentProfile.objects.filter(user=request.user, is_active=True).first()
    if not profile:
        raise PermissionDenied
    enrolled = StudentCourse.objects.filter(student=profile, course="BCS", is_active=True).exists() or profile.course == "BCS"
    if not enrolled:
        raise PermissionDenied
    return profile


def _owner(request):
    if not request.session.get("owner_access"):
        raise PermissionDenied


def _extract_pdf_questions(upload):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValueError("PDF reader is unavailable. Please contact administrator.")
    reader = PdfReader(upload)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    blocks = re.split(r"(?m)^\s*(?:Q(?:uestion)\s*)?(\d{1,3})[.)]\s*", text)
    parsed = []
    for i in range(1, len(blocks), 2):
        try:
            number = int(blocks[i])
        except (ValueError, IndexError):
            continue
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        option_matches = list(re.finditer(r"(?m)^\s*([A-Da-d])[).:]\s*", body))
        if len(option_matches) < 4:
            continue
        prompt = body[:option_matches[0].start()].strip()
        opts = {}
        for j, match in enumerate(option_matches[:4]):
            end = option_matches[j + 1].start() if j + 1 < len(option_matches) else len(body)
            opts[match.group(1).upper()] = body[match.end():end].strip()
        if prompt and all(opts.get(k) for k in "ABCD"):
            parsed.append({"number": number, "prompt": prompt, "option_a": opts["A"], "option_b": opts["B"], "option_c": opts["C"], "option_d": opts["D"]})
    return parsed


@login_required
def student_exam_list(request):
    profile = _student_profile(request)
    now = timezone.now()
    exams = [e for e in BCSExam.objects.filter(is_published=True).prefetch_related("questions") if (not e.starts_at or e.starts_at <= now) and (not e.ends_at or e.ends_at >= now)]
    attempts = {a.exam_id: a for a in BCSAttempt.objects.filter(student=profile)}
    return render(request, "bcs_exam/student_list.html", {"exams": exams, "attempts": attempts, "student": profile})


@login_required
def student_results(request):
    profile = _student_profile(request)
    attempts = BCSAttempt.objects.filter(student=profile, submitted_at__isnull=False).select_related("exam").order_by("-submitted_at")
    return render(request, "bcs_exam/student_results.html", {"attempts": attempts, "student": profile})


@login_required
def start_exam(request, exam_id):
    profile = _student_profile(request)
    exam = get_object_or_404(BCSExam, pk=exam_id, is_published=True)
    now = timezone.now()
    if (exam.starts_at and now < exam.starts_at) or (exam.ends_at and now > exam.ends_at):
        messages.error(request, "This examination is not currently available.")
        return redirect("bcs_exam_list")
    if not 50 <= exam.question_count <= 200 or exam.questions.filter(correct_option="").exists():
        messages.error(request, "This examination is not ready yet. Please contact your teacher.")
        return redirect("bcs_exam_list")
    attempt = BCSAttempt.objects.filter(exam=exam, student=profile, submitted_at__isnull=True).first()
    if not attempt:
        if BCSAttempt.objects.filter(exam=exam, student=profile, submitted_at__isnull=False).exists():
            messages.error(request, "You have already submitted this examination.")
            return redirect("bcs_exam_list")
        attempt = BCSAttempt.objects.create(exam=exam, student=profile)
    remaining_seconds = max(0, exam.duration_minutes * 60 - int((timezone.now() - attempt.started_at).total_seconds()))
    return render(request, "bcs_exam/take_exam.html", {"exam": exam, "attempt": attempt, "questions": exam.questions.all(), "remaining_seconds": remaining_seconds})


@login_required
@require_POST
def submit_exam(request, attempt_id):
    profile = _student_profile(request)
    with transaction.atomic():
        attempt = get_object_or_404(BCSAttempt.objects.select_for_update(), pk=attempt_id, student=profile, submitted_at__isnull=True)
        exam = attempt.exam
        expired = timezone.now() > attempt.started_at + timedelta(minutes=exam.duration_minutes)
        answers = {}
        correct = wrong = unanswered = 0
        score = Decimal("0")
        for q in exam.questions.all():
            selected = "" if expired else request.POST.get(f"q_{q.pk}", "").upper()
            if selected not in ("A", "B", "C", "D"):
                selected = ""
            answers[str(q.pk)] = selected
            if not selected:
                unanswered += 1
            elif selected == q.correct_option:
                correct += 1
                score += exam.marks_per_question
            else:
                wrong += 1
                score -= exam.negative_mark
        attempt.answers = answers
        attempt.correct_count, attempt.wrong_count, attempt.unanswered_count = correct, wrong, unanswered
        attempt.score = max(score, Decimal("0"))
        attempt.submitted_at = timezone.now()
        attempt.save()
    if expired:
        messages.warning(request, "The examination time expired. The attempt was submitted with unanswered responses.")
    return redirect("bcs_exam_result", attempt_id=attempt.pk)


@login_required
def exam_result(request, attempt_id):
    profile = _student_profile(request)
    attempt = get_object_or_404(BCSAttempt.objects.prefetch_related("exam__questions"), pk=attempt_id, student=profile, submitted_at__isnull=False)
    return render(request, "bcs_exam/result.html", {"attempt": attempt, "questions": attempt.exam.questions.all()})


def teacher_exams(request):
    _owner(request)
    exams = BCSExam.objects.all().prefetch_related("questions")
    submissions = BCSAttempt.objects.filter(submitted_at__isnull=False).select_related("student", "exam").order_by("-submitted_at")
    pending_review_count = submissions.filter(reviewed_at__isnull=True).count()
    attempts = submissions[:300]
    return render(request, "bcs_exam/teacher.html", {"exams": exams, "attempts": attempts, "pending_review_count": pending_review_count})


@require_POST
def create_exam(request):
    _owner(request)
    upload = request.FILES.get("source_pdf")
    try:
        test_number = int(request.POST.get("model_test_number", ""))
        duration = int(request.POST.get("duration_minutes", 120))
        negative = Decimal(request.POST.get("negative_mark", "0"))
        marks = Decimal(request.POST.get("marks_per_question", "1"))
        if test_number < 1 or not upload or not upload.name.lower().endswith(".pdf"):
            raise ValueError("Select a valid Model Test number and PDF question paper.")
        if not 1 <= duration <= 600 or negative < 0 or marks <= 0:
            raise ValueError("Please check duration and marking settings.")
        if BCSExam.objects.filter(model_test_number=test_number).exists():
            raise ValueError(f"BCS Preliminary Model Test {test_number} already exists.")
        parsed = _extract_pdf_questions(upload)
        if not 50 <= len(parsed) <= 200:
            raise ValueError(f"PDF থেকে {len(parsed)}টি complete MCQ পাওয়া গেছে। ৫০ থেকে ২০০টি প্রশ্ন থাকতে হবে।")
        upload.seek(0)
        with transaction.atomic():
            exam = BCSExam.objects.create(title=f"BCS Preliminary Model Test {test_number}", model_test_number=test_number, duration_minutes=duration, negative_mark=negative, marks_per_question=marks, source_pdf=upload)
            for q in parsed:
                BCSQuestion.objects.create(exam=exam, **q)
        messages.success(request, f"Model Test {test_number}: {len(parsed)}টি প্রশ্ন draft হয়েছে। Preview ও Answer Key যাচাই করে Publish করুন।")
        return redirect("bcs_exam_edit", exam_id=exam.pk)
    except (ValueError, InvalidOperation) as exc:
        messages.error(request, str(exc))
        return redirect("bcs_teacher_exams")
    except Exception as exc:
        messages.error(request, f"PDF থেকে প্রশ্ন তৈরি করা যায়নি: {exc}")
        return redirect("bcs_teacher_exams")


def edit_exam(request, exam_id):
    _owner(request)
    exam = get_object_or_404(BCSExam, pk=exam_id)
    if request.method == "POST":
        for q in exam.questions.all():
            answer = request.POST.get(f"answer_{q.pk}", "").upper()
            q.correct_option = answer if answer in "ABCD" else ""
            q.explanation = request.POST.get(f"explanation_{q.pk}", "").strip()
            q.save(update_fields=["correct_option", "explanation"])
        if request.POST.get("publish") == "yes":
            if not 50 <= exam.question_count <= 200 or exam.questions.filter(correct_option="").exists():
                messages.error(request, "৫০-২০০টি প্রশ্ন এবং প্রতিটি প্রশ্নের সঠিক উত্তর নির্ধারণ করতে হবে।")
            else:
                exam.is_published = True
                exam.save(update_fields=["is_published"])
                messages.success(request, "BCS Preliminary Examination published.")
        else:
            messages.success(request, "Answer key saved.")
        return redirect("bcs_exam_edit", exam_id=exam.pk)
    return render(request, "bcs_exam/edit_exam.html", {"exam": exam, "questions": exam.questions.all()})


def review_attempt(request, attempt_id):
    _owner(request)
    attempt = get_object_or_404(BCSAttempt.objects.select_related("student", "exam"), pk=attempt_id, submitted_at__isnull=False)
    if request.method == "POST":
        try:
            raw_score = request.POST.get("teacher_score", "").strip()
            score = Decimal(raw_score) if raw_score else None
            max_score = attempt.exam.question_count * attempt.exam.marks_per_question
            if score is not None and (score < 0 or score > max_score):
                raise ValueError
            attempt.teacher_score = score
            attempt.teacher_feedback = request.POST.get("teacher_feedback", "").strip()
            attempt.reviewed_at = timezone.now()
            attempt.reviewed_by = request.user if request.user.is_authenticated else None
            attempt.save(update_fields=["teacher_score", "teacher_feedback", "reviewed_at", "reviewed_by"])
            messages.success(request, "Teacher review saved and published to the student's Result page.")
            return redirect("bcs_teacher_exams")
        except (ValueError, InvalidOperation):
            messages.error(request, "Enter a valid final mark within the exam's full marks.")
    return render(request, "bcs_exam/review_attempt.html", {"attempt": attempt, "questions": attempt.exam.questions.all()})
