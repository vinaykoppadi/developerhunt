from .models import Project, Tag
from django.db.models import Q
from django.core.paginator import  Paginator , PageNotAnInteger, EmptyPage


def paginateProjects(request, projectsobj, results):
    page = request.GET.get('page')
    paginator = Paginator(projectsobj, results)

    try:
        projectsobj = paginator.page(page)
    except PageNotAnInteger:  # for zeroth page
        page = 1
        projectsobj = paginator.page(page)
    except  EmptyPage:  # for nth page
        page = paginator.num_pages
        projectsobj = paginator.page(page)

    leftpage = (int(page) - 1)

    if leftpage < 1:
        leftpage = 1

    rightpage = (int(page) + 2)

    if rightpage > paginator.num_pages:
        rightpage = paginator.num_pages + 1

    custom_range = range(leftpage, rightpage)

    return custom_range, projectsobj


def searchProjects(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    tags = Tag.objects.filter(name__icontains=search_query)

    projectsobj = Project.objects.distinct().filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(owner__name__icontains=search_query) |
        Q(tags__in=tags)
    )

    return projectsobj, search_query