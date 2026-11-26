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
    IELTSPracticeAttempt, IELTSAttendance, IELTSAssignment,
    IELTSAssignmentSubmission,
)


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
    list_display = ("student_name", "practice", "objective_score", "ai_score", "submitted_at")
    list_filter = ("practice__skill", "submitted_at")
    search_fields = ("student_name", "student_roll", "practice__title")
    readonly_fields = ("practice", "student_name", "student_roll", "answers", "objective_score", "total_objective", "submitted_at")


@admin.register(IELTSAttendance)
class IELTSAttendanceAdmin(admin.ModelAdmin):
    list_display = ("class_date", "batch", "topic", "updated_at")
    list_filter = ("batch", "class_date")
    search_fields = ("batch", "topic")
    fields = ("class_date", "batch", "topic", "roster")


@admin.register(IELTSAssignment)
class IELTSAssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "deadline", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "instructions")


@admin.register(IELTSAssignmentSubmission)
class IELTSAssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student_name", "assignment", "score", "reviewed_at", "submitted_at")
    list_filter = ("assignment", "reviewed_at")
    search_fields = ("student_name", "student_roll", "assignment__title")
    fields = ("assignment", "student_name", "student_roll", "answer_text", "file", "teacher_feedback", "marked_fragments", "score", "reviewed_at", "submitted_at")
    readonly_fields = ("submitted_at",)


@admin.register(IELTSStudent)
class IELTSStudentAdmin(admin.ModelAdmin):
    list_display = ("name", "roll", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "roll")


@admin.register(CourseAttendance)
class CourseAttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "class_date", "course_name", "module_name", "sign_in", "sign_out", "duration_minutes")
    list_filter = ("course_name", "class_date")
    search_fields = ("student__name", "student__roll", "module_name")
    readonly_fields = ("duration_minutes",)
