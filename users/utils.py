from django.db.models import Q
from .models import Profile, Skill
from django.core.paginator import  Paginator , PageNotAnInteger, EmptyPage


def paginateProfiles(request, profiles, results):
    page = request.GET.get('page')
    paginator = Paginator(profiles, results)

    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:  # for zeroth page
        page = 1
        profiles = paginator.page(page)
    except  EmptyPage:  # for nth page
        page = paginator.num_pages
        profiles = paginator.page(page)

    leftpage = (int(page) - 1)

    if leftpage < 1:
        leftpage = 1

    rightpage = (int(page) + 2)

    if rightpage > paginator.num_pages:
        rightpage = paginator.num_pages + 1

    custom_range = range(leftpage, rightpage)

    return custom_range, profiles



def searchProfiles(request):

    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    skills = Skill.objects.filter(name__iexact=search_query)

    profiles1 = Profile.objects.distinct().filter(
        Q(name__icontains=search_query) |
        Q(short_intro__icontains=search_query) |
         Q(skill__in=skills))

    return profiles1, search_query