from django.contrib import admin
from django.db.models import Avg
from .models import Project, Vote

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'vote_type', 'vote_start', 'vote_end', 'created_at', 'average_score')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(avg_score=Avg('vote__score')).order_by('-avg_score')

    def average_score(self, obj):
        avg = getattr(obj, 'avg_score', 0)
        if avg is None:
            return 0
        return round(avg, 2)
    average_score.short_description = '평균 점수'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'score', 'created_at')






