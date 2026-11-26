from datetime import datetime
from django.db import models
from django.conf import settings


COURSE_MODULES = {
    "IELTS": ["Listening", "Reading", "Writing", "Speaking", "Lexical Resources"],
    "Language Testing": ["Listening", "Reading", "Writing", "Speaking", "Lexical Resources", "Grammatical Theory"],
    "Programming": ["C", "C++", "C#", "Java", "Python", "Ruby", "Fortran", "Golang"],
    "CSE Course": ["Structured Programming", "Object-Oriented Programming", "Data Structures", "Algorithms", "Discrete Mathematics", "Digital Logic Design", "Computer Organization & Architecture", "Database Management Systems", "Operating Systems", "Computer Networks", "Software Engineering", "Web Engineering", "Compiler Design", "Theory of Computation", "Artificial Intelligence", "Machine Learning", "Cyber Security", "Computer Graphics", "Microprocessors & Embedded Systems", "Distributed Systems", "Data Mining", "Cloud Computing", "Information Systems"],
    "School Academy": ["General Science", "Mathematics", "Chemistry", "Physics", "Biology", "ICT"],
    "College Academy": ["Mathematics", "Physics", "Chemistry", "ICT"],
    "Undergraduate Courses": ["Programming Fundamentals", "Object-Oriented Programming", "Data Structures", "Algorithms", "Database Systems", "Operating Systems", "Computer Networks", "Software Engineering", "Web Development", "Mathematics", "Statistics", "Digital Logic", "Computer Architecture", "Artificial Intelligence", "Machine Learning", "Cyber Security"],
    "BCS": ["Bangla Language & Literature", "English Language & Literature", "Bangladesh Affairs", "International Affairs", "Geography, Environment & Disaster Management", "General Science", "Computer & ICT", "Mathematical Reasoning", "Mental Ability", "Ethics, Values & Good Governance"],
}


class StudentProfile(models.Model):
    COURSE_CHOICES = [(name, name) for name in COURSE_MODULES]
    name = models.CharField(max_length=120, db_index=True)
    roll = models.CharField(max_length=40, blank=True)
    course = models.CharField(max_length=40, choices=COURSE_CHOICES)
    modules = models.JSONField(default=list, help_text="Modules assigned to this student")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="student_profile")
    joining_date = models.DateField(null=True, blank=True)
    course_finish_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("course", "name")
        constraints = [models.UniqueConstraint(fields=("name", "roll", "course"), name="unique_student_course_roll")]

    def __str__(self):
        return f"{self.name} ({self.roll or 'No roll'}) · {self.course}"


class AttendanceRecord(models.Model):
    class Period(models.TextChoices):
        AM = "AM", "AM"
        PM = "PM", "PM"

    class_date = models.DateField(db_index=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name="attendance_records")
    period = models.CharField(max_length=2, choices=Period.choices)
    course_name = models.CharField(max_length=40)
    module_name = models.CharField(max_length=120)
    sign_in = models.TimeField(null=True, blank=True)
    sign_out = models.TimeField(null=True, blank=True)
    sign_out_date = models.DateField(null=True, blank=True, help_text="Bangladesh-local date when the student signed out")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-class_date", "period", "student__name")


    @property
    def total_minutes(self):
        if not self.sign_in or not self.sign_out:
            return None
        start = datetime.combine(self.class_date, self.sign_in)
        end = datetime.combine(self.sign_out_date or self.class_date, self.sign_out)
        if end < start:
            from datetime import timedelta
            end += timedelta(days=1)
        return int((end - start).total_seconds() // 60)

    @property
    def total_duration(self):
        minutes = self.total_minutes
        if minutes is None:
            return "—"
        hours, mins = divmod(minutes, 60)
        return f"{hours}h {mins}m" if hours else f"{mins}m"

    def __str__(self):
        return f"{self.student.name} · {self.class_date} · {self.period}"
