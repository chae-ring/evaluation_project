from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Avg
from django.contrib import messages
from .models import Project, Vote

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = False  
            user.save()
            login(request, user)
            return redirect('project_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def project_list(request):
    sort = request.GET.get('sort', 'desc') 

    projects = Project.objects.annotate(avg_score=Avg('vote__score'))

    if sort == 'asc':
        projects = projects.order_by('avg_score')
    else:
        projects = projects.order_by('-avg_score')

    for project in projects:
        project.avg_score = project.avg_score or 0
        project.avg_score_int = int(round(project.avg_score))

    context = {'projects': projects, 'sort': sort}
    return render(request, 'evaluation/project_list.html', context)


def project_detail(request, id):
    project = get_object_or_404(Project, pk=id)
    votes = Vote.objects.filter(project=project)
    avg_score = votes.aggregate(Avg('score'))['score__avg'] or 0
    avg_score_int = int(round(avg_score))  

    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, project=project).first()

    can_vote = False
    if project.vote_type == 'always':
        can_vote = True
    elif project.vote_type == 'period':
        from django.utils import timezone
        now = timezone.now()
        if project.vote_start <= now <= project.vote_end:
            can_vote = True

    context = {
        'project': project,
        'avg_score': avg_score,
        'avg_score_int': avg_score_int,  
        'user_vote': user_vote,
        'can_vote': can_vote,
    }
    return render(request, 'evaluation/project_detail.html', context)

@login_required
def project_vote(request, id):
    project = get_object_or_404(Project, pk=id)
    if request.method == 'POST':
        score = int(request.POST.get('score', 0))
        if score < 1 or score > 5:
            messages.error(request, '점수는 1에서 5 사이여야 합니다.')
            return redirect('project_detail', id=id)

        if Vote.objects.filter(user=request.user, project=project).exists():
            messages.error(request, '이미 투표하셨습니다.')
            return redirect('project_detail', id=id)

        from django.utils import timezone
        now = timezone.now()
        if project.vote_type == 'period':
            if not (project.vote_start <= now <= project.vote_end):
                messages.error(request, '투표 기간이 아닙니다.')
                return redirect('project_detail', id=id)

        Vote.objects.create(user=request.user, project=project, score=score)
        messages.success(request, '투표가 완료되었습니다.')
        return redirect('project_result', id=id)

    return redirect('project_detail', id=id)

from django.db.models import Avg

def project_result(request, id):
    project = get_object_or_404(Project, pk=id)
    votes = Vote.objects.filter(project=project)
    avg_score = votes.aggregate(Avg('score'))['score__avg'] or 0
    total_votes = votes.count()
    avg_score_int = int(round(avg_score)) 

    context = {
        'project': project,
        'avg_score': avg_score,
        'avg_score_int': avg_score_int, 
        'total_votes': total_votes,
    }
    return render(request, 'evaluation/project_result.html', context)



