from django.conf import settings
from django.db import models
from django.utils import timezone
from attendance.models import StudentProfile

class BCSExam(models.Model):
    title = models.CharField(max_length=180)
    instructions = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=120)
    negative_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    marks_per_question = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    is_published = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    source_pdf = models.FileField(upload_to="bcs_exam/source_pdfs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ("-created_at",)
    def __str__(self): return self.title
    @property
    def question_count(self): return self.questions.count()

class BCSQuestion(models.Model):
    exam = models.ForeignKey(BCSExam, on_delete=models.CASCADE, related_name="questions")
    number = models.PositiveIntegerField()
    subject = models.CharField(max_length=100, blank=True)
    prompt = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1, choices=[(x,x) for x in "ABCD"], blank=True)
    explanation = models.TextField(blank=True)
    class Meta:
        ordering = ("number",)
        constraints = [models.UniqueConstraint(fields=("exam","number"), name="bcs_exam_question_number_uniq")]

class BCSAttempt(models.Model):
    exam = models.ForeignKey(BCSExam, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="bcs_exam_attempts")
    answers = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)
    unanswered_count = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ("-started_at",)
        constraints = [models.UniqueConstraint(fields=("exam","student"), condition=models.Q(submitted_at__isnull=True), name="one_open_bcs_exam_attempt")]
