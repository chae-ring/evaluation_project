from django.contrib import admin
from .models import Project, Vote

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'vote_type', 'vote_start', 'vote_end', 'created_at')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'score', 'created_at')
