from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .models import Profile, Message
from .utils import searchProfiles, paginateProfiles



# Create your views here.


def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST["username"].lower()
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, "Username or password is incorrect")

    return render(request, 'users/login_register.html')


def logoutUser(request):
    logout(request)
    messages.info(request, "Username was logged out")
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created')

            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)

def unread(request):
    try:
        proflie = request.user.profile
        messageRequest = proflie.messages.all()
        unreadCount = messageRequest.filter(is_read=False).count()
    except:
        unreadCount = ""
    if unreadCount == 0:
        return ""
    else:
        return f"( {unreadCount} )"

def profiles(request):
    profiles1, search_query = searchProfiles(request)
    unreadCount = unread(request)
    custum_range, profiles1 = paginateProfiles(request, profiles1, 4)

    context = {"profiles": profiles1, 'search_query': search_query, 'custom_range':custum_range, 'unreadCount': unreadCount}
    return render(request, 'users/profiles.html', context)


def userProfile(requests, pk):
    unreadCount = unread(requests)
    profile = Profile.objects.get(id=pk)
    topSkill = profile.skill_set.exclude(description__exact="")
    otherSkill = profile.skill_set.filter(description="")
    context = {'profile': profile, 'topSkill': topSkill, 'otherSkill': otherSkill, 'unreadCount': unreadCount}
    return render(requests, 'users/user-profile.html', context)


@login_required(login_url='login')
def userAccount(requests):
    profile = requests.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    unreadCount = unread(requests)

    context = {'profile': profile, 'skills': skills, 'projects': projects, 'unreadCount': unreadCount}
    return render(requests, 'users/account.html', context)

@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile

    form = ProfileForm(instance= profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    context ={'form': form}
    
    return render(request, 'users/profile_form.html', context)

@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile

    form = SkillForm()
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill was created successfully')
            return redirect('account')
    context = {'form':form}
    return render(request, 'users/skills_form.html', context)


@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill =profile.skill_set.get(id=pk)

    form = SkillForm(instance=skill)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated successfully')
            return redirect('account')
    context = {'form':form}
    return render(request, 'users/skills_form.html', context)

@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill was deleted2 successfully')
        return redirect('account')
    context = {'object': skill}
    return render(request, 'delete-project.html', context)

@login_required(login_url='login')
def inbox(request):
    proflie = request.user.profile
    messageRequest = proflie.messages.all()
    try:
        unreadCount = messageRequest.filter(is_read=False).count()
    except:
        unreadCount = ""
    if unreadCount == 0:
        unreadCount= ""
    else:
        unreadCount= f"( {unreadCount} )"
    context = {'messageRequest':messageRequest, 'unreadCount':unreadCount}
    return render(request, 'users/inbox.html', context)

@login_required(login_url='login')
def viewMessages(request, pk):
    profiles = request.user.profile
    message = profiles.messages.get(id=pk)
    if message.is_read == False:
        message.is_read =True
        message.save()
    context = {'message':message, 'profiles':profiles}
    return render(request, 'users/message.html', context)

def createMessage(request, pk):
    form = MessageForm()
    recipient = Profile.objects.get(id=pk)
    try:
        sender = request.user.profile
    except :
        sender = None
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email

            message.save()
            messages.success(request, 'Message send successfully')
            return redirect('user-profile', pk=recipient.id)

    context = {'form':form, 'recipient':recipient,}
    return render(request, 'users/message_form.html', context)


def replyMessage(request, pk):
    form = MessageForm()
    messages1 = Message.objects.get(id=pk)
    recipient = messages1.sender
    try:
        sender = request.user.profile
    except :
        sender = None
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email

            message.save()
            messages.success(request, 'Message send successfully')
            return redirect('inbox')

    context = {'form':form, 'recipient':recipient,}
    return render(request, 'users/message_form.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    profile = request.user.profile
    message = profile.message_set.get(id=pk)
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message was deleted2 successfully')
        return redirect('account')
    context = {'object': message}
    return render(request, 'delete-project.html', context)
