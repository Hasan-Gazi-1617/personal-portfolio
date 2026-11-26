from django.contrib import admin

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
    IELTSPracticeAttempt, IELTSAssignment, IELTSAssignmentSubmission,
)
from attendance.models import StudentProfile, AttendanceRecord

# Use course/student terminology in Django Admin instead of IELTS-only labels.
for model, singular, plural in (
    (IELTSNotice, "Student notice", "Student notices"),
    (IELTSMaterial, "Course material", "Course materials"),
    (IELTSLesson, "Course lesson", "Course lessons"),
    (IELTSPracticeSet, "Course practice set", "Course practice sets"),
    (IELTSPracticeAttempt, "Student practice attempt", "Student practice attempts"),
    (IELTSAssignment, "Course assignment", "Course assignments"),
    (IELTSAssignmentSubmission, "Student assignment submission", "Student assignment submissions"),
):
    model._meta.verbose_name = singular
    model._meta.verbose_name_plural = plural


@admin.register(IELTSNotice)
class IELTSNoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "message")


@admin.register(IELTSMaterial)
class IELTSMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published")
    search_fields = ("title", "description")


@admin.register(IELTSLesson)
class IELTSLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "order", "is_published")
    list_filter = ("skill", "is_published")
    search_fields = ("title", "content")


@admin.register(IELTSPracticeSet)
class IELTSPracticeSetAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "time_minutes", "is_published")
    list_filter = ("skill", "is_published")
    search_fields = ("title",)
    fields = ("title", "skill", "instructions", "time_minutes", "questions", "is_published")


@admin.register(IELTSPracticeAttempt)
class IELTSPracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_roll", "practice", "objective_score", "ai_score", "submitted_at")
    list_filter = ("practice__skill", "submitted_at")
    search_fields = ("student_name", "student_roll", "practice__title")
    readonly_fields = ("practice", "student_name", "student_roll", "answers", "objective_score", "total_objective", "submitted_at")


 

@admin.register(IELTSAssignment)
class IELTSAssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "deadline", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "instructions")


@admin.register(IELTSAssignmentSubmission)
class IELTSAssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student_name", "student_roll", "student_profile", "assignment", "score", "reviewed_at", "submitted_at")
    list_filter = ("assignment", "reviewed_at", "student_profile__course")
    search_fields = ("student_name", "student_roll", "assignment__title", "student_profile__name", "student_profile__user__username")
    fields = ("student_profile", "assignment", "student_name", "student_roll", "answer_text", "file", "teacher_feedback", "marked_fragments", "score", "reviewed_at", "submitted_at")
    readonly_fields = ("submitted_at",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "roll", "course", "username_display", "email_display", "is_active")
    list_filter = ("course", "is_active")
    search_fields = ("name", "roll", "course", "user__username", "user__email")
    autocomplete_fields = ("user",)

    @admin.display(description="Username")
    def username_display(self, obj):
        return obj.user.username if obj.user_id else "No account"

    @admin.display(description="Email")
    def email_display(self, obj):
        return obj.user.email if obj.user_id else "—"


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("class_date", "student", "course_name", "module_name", "period", "sign_in", "sign_out")
    list_filter = ("course_name", "module_name", "period", "class_date")
    search_fields = ("student__name", "student__roll", "student__user__username", "course_name", "module_name")
    autocomplete_fields = ("student",)
