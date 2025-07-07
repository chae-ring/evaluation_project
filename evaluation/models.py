from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    VOTE_TYPE_CHOICES = [
        ('always', '상시'),
        ('period', '기간 설정'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPE_CHOICES, default='always')
    vote_start = models.DateTimeField(null=True, blank=True)
    vote_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f'{self.user.username} - {self.project.title} - {self.score}'

