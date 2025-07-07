from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Vote
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

def project_list(request):
    projects = Project.objects.all()
    for project in projects:
        votes = Vote.objects.filter(project=project)
        project.avg_score = votes.aggregate(models.Avg('score'))['score__avg'] or 0
        project.vote_count = votes.count()
    return render(request, 'evaluation/project_list.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    votes = Vote.objects.filter(project=project)
    avg_score = votes.aggregate(models.Avg('score'))['score__avg'] or 0
    vote_count = votes.count()

    now = timezone.now()
    can_vote = True
    if project.vote_type == 'period':
        if project.vote_start and project.vote_end:
            if not (project.vote_start <= now <= project.vote_end):
                can_vote = False
    user_voted = False
    if request.user.is_authenticated:
        user_voted = votes.filter(user=request.user).exists()

    context = {
        'project': project,
        'avg_score': avg_score,
        'vote_count': vote_count,
        'can_vote': can_vote,
        'user_voted': user_voted,
    }
    return render(request, 'evaluation/project_detail.html', context)

@login_required
def project_vote(request, pk):
    project = get_object_or_404(Project, pk=pk)

    now = timezone.now()
    if project.vote_type == 'period':
        if not (project.vote_start and project.vote_end and project.vote_start <= now <= project.vote_end):
            messages.error(request, "현재 투표 기간이 아닙니다.")
            return redirect('evaluation:project_detail', pk=pk)

    existing_vote = Vote.objects.filter(project=project, user=request.user).first()
    if existing_vote:
        messages.error(request, "이미 투표하셨습니다.")
        return redirect('evaluation:project_detail', pk=pk)

    if request.method == 'POST':
        score = int(request.POST.get('score', 0))
        if score < 1 or score > 5:
            messages.error(request, "1점에서 5점 사이의 점수를 입력하세요.")
            return redirect('evaluation:project_detail', pk=pk)
        Vote.objects.create(project=project, user=request.user, score=score)
        messages.success(request, "투표가 완료되었습니다.")
        return redirect('evaluation:project_result', pk=pk)

    return redirect('evaluation:project_detail', pk=pk)

def project_result(request, pk):
    project = get_object_or_404(Project, pk=pk)
    votes = Vote.objects.filter(project=project)
    avg_score = votes.aggregate(models.Avg('score'))['score__avg'] or 0
    vote_count = votes.count()

    context = {
        'project': project,
        'avg_score': avg_score,
        'vote_count': vote_count,
    }
    return render(request, 'evaluation/project_result.html', context)
