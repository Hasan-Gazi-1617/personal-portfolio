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
from attendance.models import StudentProfile, StudentCourse, AttendanceRecord, COURSE_MODULES

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
    email = forms.EmailField(label="Student email")
    password = forms.CharField(
        label="Student password",
        required=False,
        widget=forms.PasswordInput,
        help_text="Required for a new student. Leave blank when editing to keep the current password.",
    )
    modules = forms.MultipleChoiceField(
        label="Modules",
        required=False,
        choices=[(module, module) for module in sorted({m for values in COURSE_MODULES.values() for m in values})],
        widget=forms.SelectMultiple(attrs={
            "data-module-map": __import__("json").dumps(COURSE_MODULES),
        }),
        help_text="Select the course first, then choose its modules. Hold Ctrl to select multiple modules.",
    )

    class Meta:
        model = StudentProfile
        fields = ("name", "roll", "course", "modules", "joining_date", "course_finish_date", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        linked_user = getattr(self.instance, "user", None) if self.instance and self.instance.pk else None
        if linked_user:
            self.fields["email"].initial = linked_user.email
        else:
            self.fields["password"].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        User = get_user_model()
        users = User._default_manager.filter(email__iexact=email)
        linked_user = getattr(self.instance, "user", None) if self.instance and self.instance.pk else None
        if linked_user:
            users = users.exclude(pk=linked_user.pk)
        if users.exists():
            raise forms.ValidationError("This email already has a student account.")
        return email

    def clean_modules(self):
        modules = self.cleaned_data.get("modules", [])
        course = self.cleaned_data.get("course")
        if any(module not in COURSE_MODULES.get(course, []) for module in modules):
            raise forms.ValidationError("Choose modules from the selected course only.")
        return modules

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        linked_user = getattr(self.instance, "user", None) if self.instance and self.instance.pk else None
        if not linked_user and not password:
            self.add_error("password", "Enter a password for student login.")
        return cleaned


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    form = StudentProfileAdminForm
    list_display = ("name", "roll", "course", "email_display", "is_active", "created_at")
    list_filter = ("course", "is_active", "joining_date")
    search_fields = ("name", "roll", "course", "user__email")
    inlines = (StudentCourseInline,)
    readonly_fields = ("created_at",)

    class Media:
        js = ("admin/course-module-select.js",)

    fieldsets = (
        ("Student registration", {"fields": ("name", "roll", "course", "modules", "joining_date", "course_finish_date", "is_active")}),
        ("Student login", {"fields": ("email", "password")}),
        ("System information", {"fields": ("created_at",)}),
    )

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        User = get_user_model()
        email = form.cleaned_data["email"]
        password = form.cleaned_data.get("password")
        if obj.user_id:
            account = obj.user
            account.email = email
            setattr(account, User.USERNAME_FIELD, email)
            if password:
                account.set_password(password)
            account.save()
        else:
            account = User._default_manager.create_user(
                **{User.USERNAME_FIELD: email},
                email=email,
                password=password,
            )
        obj.user = account
        obj.modules = form.cleaned_data.get("modules", [])
        super().save_model(request, obj, form, change)

    @admin.display(description="Student email", ordering="user__email")
    def email_display(self, obj):
        return obj.user.email if obj.user_id else "Account not created"


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
