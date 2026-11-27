from django.urls import path
from . import views
urlpatterns = [
 path("students/preliminary-examination/", views.student_exam_list, name="bcs_exam_list"),
 path("students/preliminary-examination/<int:exam_id>/start/", views.start_exam, name="bcs_exam_start"),
 path("students/preliminary-examination/attempt/<int:attempt_id>/submit/", views.submit_exam, name="bcs_exam_submit"),
 path("students/preliminary-examination/attempt/<int:attempt_id>/result/", views.exam_result, name="bcs_exam_result"),
 path("owner/bcs-exams/", views.teacher_exams, name="bcs_teacher_exams"),
 path("owner/bcs-exams/create/", views.create_exam, name="bcs_exam_create"),
 path("owner/bcs-exams/<int:exam_id>/", views.edit_exam, name="bcs_exam_edit"),
]
