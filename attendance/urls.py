from django.urls import path
from . import views

urlpatterns = [
    path("students/attendance/", views.student_attendance, name="student_attendance"),
    path("owner/attendance/", views.attendance_admin, name="attendance_admin"),
]
