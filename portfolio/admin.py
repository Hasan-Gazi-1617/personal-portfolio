from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction


from .models import ComplaintTicket, TicketActivity


@admin.register(ComplaintTicket)
class ComplaintTicketAdmin(admin.ModelAdmin):
    list_display = ("tki_id", "client_id", "field_support_engineer", "higher_level_noc", "status", "dependency", "attention", "opened_at")
    list_filter = ("status", "dependency", "field_support_engineer", "higher_level_noc", "attention", "isp_related")
    search_fields = ("tki_id", "client_id", "complaint", "remarks", "findings")
    autocomplete_fields = ("assigned_engineer", "created_by")
    readonly_fields = ("created_at", "updated_at", "support_assigned_at", "resolved_at")


@admin.register(TicketActivity)
class TicketActivityAdmin(admin.ModelAdmin):
    list_display = ("ticket", "actor", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("ticket__tki_id", "actor__username", "detail")
    readonly_fields = ("ticket", "actor", "action", "detail", "created_at")


from .models import (
    IELTSNotice, IELTSMaterial, IELTSLesson, IELTSPracticeSet,
    IELTSPracticeAttempt, IELTSAttendance, IELTSAssignment, IELTSAssignmentSubmission,
)
from attendance.models import StudentProfile, StudentCourse, AttendanceRecord

# Use course/student terminology in Django Admin instead of IELTS-only labels.
for model, singular, plural in (
    (IELTSNotice, "Student notice", "Student notices"),
    (IELTSMaterial, "Course material", "Course materials"),
    (IELTSLesson, "Course lesson", "Course lessons"),
    (IELTSPracticeSet, "Course practice set", "Course practice sets"),
    (IELTSPracticeAttempt, "Student practice attempt", "Student practice attempts"),
    (IELTSAttendance, "Class attendance sheet", "Class attendance sheets"),
    (IELTSAssignment, "Course assignment", "Course assignments"),
    (IELTSAssignmentSubmission, "Student assignment submission", "Student assignment submissions"),
):
    model._meta.verbose_name = singular
    model._meta.verbose_name_plural = plural


@admin.register(IELTSNotice)
class IELTSNoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "is_published", "created_at")
    list_filter = ("course", "is_published", "created_at")
    search_fields = ("title", "message")


@admin.register(IELTSMaterial)
class IELTSMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "category", "is_published", "created_at")
    list_filter = ("course", "category", "is_published")
    search_fields = ("title", "description")


@admin.register(IELTSLesson)
class IELTSLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "skill", "order", "is_published")
    list_filter = ("course", "skill", "is_published")
    search_fields = ("title", "content")


@admin.register(IELTSPracticeSet)
class IELTSPracticeSetAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "skill", "time_minutes", "is_published")
    list_filter = ("course", "skill", "is_published")
    search_fields = ("title",)
    fields = ("title", "course", "skill", "instructions", "time_minutes", "questions", "is_published")


@admin.register(IELTSPracticeAttempt)
class IELTSPracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_roll", "practice", "course_display", "objective_score", "ai_score", "submitted_at")
    list_filter = ("practice__course", "practice__skill", "submitted_at")
    search_fields = ("student_name", "student_roll", "practice__title")
    readonly_fields = ("practice", "student_profile", "student_name", "student_roll", "answers", "objective_score", "total_objective", "submitted_at")

    @admin.display(description="Course")
    def course_display(self, obj):
        return obj.practice.course


 

@admin.register(IELTSAssignment)
class IELTSAssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "deadline", "is_published", "created_at")
    list_filter = ("course", "is_published")
    search_fields = ("title", "instructions")


@admin.register(IELTSAssignmentSubmission)
class IELTSAssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_roll", "student_profile", "assignment", "course_display", "score", "reviewed_at", "submitted_at")
    list_filter = ("assignment__course", "assignment", "reviewed_at")
    search_fields = ("student_name", "student_roll", "assignment__title", "student_profile__name", "student_profile__user__username")
    fields = ("student_profile", "assignment", "student_name", "student_roll", "answer_text", "file", "teacher_feedback", "marked_fragments", "score", "reviewed_at", "submitted_at")
    readonly_fields = ("submitted_at",)

    @admin.display(description="Course")
    def course_display(self, obj):
        return obj.assignment.course


class StudentCourseInline(admin.TabularInline):
    model = StudentCourse
    extra = 1
    fields = ("course", "modules", "joining_date", "course_finish_date", "is_active")
    show_change_link = True


class StudentProfileAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Login username")
    email = forms.EmailField(label="Login email")
    password = forms.CharField(
        label="Login password", required=False,
        widget=forms.PasswordInput,
        help_text="Required for a new account. Leave blank when editing to keep the current password.",
    )

    class Meta:
        model = StudentProfile
        fields = (
            "name", "roll", "course", "modules", "joining_date",
            "course_finish_date", "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        linked_user = getattr(self.instance, "user", None) if self.instance and self.instance.pk else None
        if linked_user:
            self.fields["username"].initial = linked_user.get_username()
            self.fields["email"].initial = linked_user.email
        else:
            self.fields["password"].required = True

    def clean(self):
        cleaned = super().clean()
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        username = cleaned.get("username")
        email = cleaned.get("email")
        password = cleaned.get("password")
        linked_user = getattr(self.instance, "user", None) if self.instance and self.instance.pk else None

        if username:
            matches = User._default_manager.filter(**{f"{username_field}__iexact": username})
            if linked_user:
                matches = matches.exclude(pk=linked_user.pk)
            if matches.exists():
                self.add_error("username", "This username is already in use.")

        if email:
            matches = User._default_manager.filter(email__iexact=email)
            if linked_user:
                matches = matches.exclude(pk=linked_user.pk)
            if matches.exists():
                self.add_error("email", "This email is already in use.")

        if password:
            candidate = linked_user or User(**{username_field: username or ""}, email=email or "")
            try:
                validate_password(password, candidate)
            except ValidationError as exc:
                self.add_error("password", exc)
        elif not linked_user:
            self.add_error("password", "Enter a password for the student's login account.")
        return cleaned


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    form = StudentProfileAdminForm
    list_display = ("name", "roll", "course", "username_display", "email_display", "is_active", "created_at")
    list_filter = ("course", "is_active", "joining_date")
    search_fields = ("name", "roll", "course", "user__username", "user__email")
    inlines = (StudentCourseInline,)
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Student information", {"fields": ("name", "roll", "course", "modules", "joining_date", "course_finish_date", "is_active")}),
        ("Student login credentials", {"fields": ("username", "email", "password")}),
        ("System information", {"fields": ("created_at",)}),
    )

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        User = get_user_model()
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data.get("password")

        if obj.user_id:
            account = obj.user
            setattr(account, User.USERNAME_FIELD, username)
            account.email = email
            if password:
                account.set_password(password)
            account.save()
        else:
            account = User._default_manager.create_user(
                **{User.USERNAME_FIELD: username},
                email=email,
                password=password,
            )
        obj.user = account
        super().save_model(request, obj, form, change)

    @admin.display(description="Username", ordering="user__username")
    def username_display(self, obj):
        return obj.user.get_username() if obj.user_id else "No account"

    @admin.display(description="Email", ordering="user__email")
    def email_display(self, obj):
        return obj.user.email if obj.user_id else "—"


@admin.register(IELTSAttendance)
class IELTSAttendanceAdmin(admin.ModelAdmin):
    list_display = ("class_date", "batch", "topic", "updated_at")
    list_filter = ("batch", "class_date")
    search_fields = ("batch", "topic")
    readonly_fields = ("updated_at",)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("class_date", "student", "course_name", "module_name", "period", "sign_in", "sign_out")
    list_filter = ("course_name", "module_name", "period", "class_date")
    search_fields = ("student__name", "student__roll", "student__user__username", "course_name", "module_name")
    autocomplete_fields = ("student",)


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "is_active", "joining_date", "course_finish_date")
    list_filter = ("course", "is_active")
    search_fields = ("student__name", "student__roll", "student__user__username", "course")
    autocomplete_fields = ("student",)
