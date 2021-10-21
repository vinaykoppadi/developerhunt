from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from users import models, views
from django.contrib.auth.decorators import login_required
from .utils import searchProjects, paginateProjects



def projects(request):
    unreadCount = views.unread(request)
    projectsobj, search_query =searchProjects(request)
    profiles = models.Profile.objects.all()

    custom_range , projectsobj = paginateProjects(request, projectsobj, 3)

    context = {'projects': projectsobj, 'profiles': profiles, 'search_query': search_query,
                'custom_range': custom_range, 'unreadCount': unreadCount}

    return render(request, "projects/projects.html", context)


def project(requests, vinay):
    projectid = Project.objects.get(id=vinay)
    form = ReviewForm()
    unreadCount = views.unread(requests)

    if requests.method == 'POST':
        form = ReviewForm(requests.POST)
        review = form.save(commit=False)
        review.project = projectid
        review.owner = requests.user.profile
        review.save()

        projectid.getVoteCount
        messages.success(requests, 'Your review is successfully submitted!')
        return redirect('project', vinay=projectid.id)
    return render(requests, "projects/single-project.html", {'projects': projectid, 'form':form, 'unreadCount': unreadCount}, )

@login_required(login_url='login')
def create_project(requests):
    profile = requests.user.profile
    form = ProjectForm()
    if requests.method == 'POST':
        newtags = requests.POST.get('newtags').replace(",", " ").split()
        form = ProjectForm(requests.POST, requests.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            for tags in newtags:
                tags, created = Tag.objects.get_or_create(name=tags)
                project.tags.add(tags)
            messages.success(requests, f'Project {project} added successfully')
            return redirect('account')
    context = {'form' : form}

    return render(requests, "projects/create-project.html", context)

@login_required(login_url='login')
def update_project(requests, pk):
    profile = requests.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)
    if requests.method == 'POST':
        newtags = requests.POST.get('newtags').replace(",", " ").split()

        form = ProjectForm(requests.POST, requests.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            for tags in newtags:
                tags, created = Tag.objects.get_or_create(name=tags)
                project.tags.add(tags)
            messages.success(requests, f'Project {project} updated successfully')
            return redirect('account')
    context = {'form' : form , 'project': project}

    return render(requests, "projects/create-project.html", context)


@login_required(login_url='login')
def delete_project(requests, pk):
    profile = requests.user.profile
    project = profile.project_set.get(id=pk)
    if requests.method == 'POST':
        project.delete()
        messages.success(requests, f'Project {project} deleted successfully')
        return redirect('projects')
    context = {'object': project}
    return render(requests, "delete-project.html", context)
