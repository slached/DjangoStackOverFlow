from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import DiscussForm
from .models import Discuss, Tag


def logout_page(request):
    logout(request)
    return redirect('home')


def login_page(request):
    if request.method == 'POST':

        mail = request.POST.get('mail')
        password = request.POST.get('password')

        user = authenticate(username=mail, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Password or mail incorrect')

    context = {
        'title': 'login',
    }

    return render(request, 'base/login.html', context=context)


def register_page(request):
    context = {
        'title': 'register',
    }

    if request.method == 'POST':
        mail = request.POST.get('mail')
        password = request.POST.get('password')
        username = request.POST.get('username')

        user = User.objects.create_user(username=mail, password=password)

        user.myuser.username = username
        user.save()

        login(request, user)
        return redirect('home')

    return render(request, 'base/register.html', context=context)


def home(request):
    discuss = Discuss.objects.all()

    all_tags = Tag.objects.all()

    print(request.user)

    if request.method == 'POST':
        new_followed_tag = request.POST['added-tag']

        current_user = request.user

        ok = new_followed_tag.lower() in str(all_tags).lower()

        if ok:
            current_user.myuser.watchedTags.add(str(new_followed_tag))
        else:
            messages.error(request, f"{new_followed_tag} does not exist on this site.")

    context = {
        'title': 'Stack Overflow - Where Developers Learn, Share & Build Careers',
        'whichSelected': 'home',
        'discuss': discuss,

    }

    return render(request, 'base/home.html', context=context)


def questions(request):
    filter_query = request.GET.get('filter') if request.GET.get('filter') is not None else "newest"

    if filter_query == 'newest':
        discuss = Discuss.objects.all().order_by('-created')
    else:
        discuss = Discuss.objects.all()

    context = {
        'title': 'Questions - StackOverflow',
        'discuss': discuss,
        'whichSelected': 'questions'
    }

    return render(request, 'base/questions.html', context=context)


def tags(request):
    discuss = Discuss.objects.all()

    def count_tag_amount_and_update():
        temp_dict = {tpc.tags: 0 for ds in discuss for tpc in ds.topics.all()}

        for i in discuss:
            for j in i.topics.all():
                temp_dict[j.tags] += 1

        for key, value in temp_dict.items():
            altered_topic = Tag.objects.get(tags=key)
            altered_topic.tag_count = value
            altered_topic.save()

    count_tag_amount_and_update()  # this is for update the amount of tag

    filter_tag = request.GET.get('filter') if request.GET.get('filter') is not None else "popular"

    if filter_tag == 'popular':
        whole_tags = Tag.objects.all().order_by('-tag_count')
    elif filter_tag == 'name':
        whole_tags = Tag.objects.all().order_by('tags')
    elif filter_tag == 'new':
        whole_tags = Tag.objects.all().order_by('-created')
    else:
        whole_tags = Tag.objects.filter(
            Q(tags__startswith=filter_tag)

        )
    context = {
        'title': 'Tags - StackOverflow',
        'tags': whole_tags,
        'whichSelected': 'Tags'

    }
    return render(request, 'base/tags.html', context=context)


def users(request):
    filter_query = request.GET.get('filter') if request.GET.get('filter') is not None else "reputation"

    discuss = Discuss.objects.all()

    update_user()

    if filter_query == 'reputation':
        user_datas = User.objects.order_by('-myuser__quantity')
    elif filter_query == 'newuser':
        user_datas = User.objects.order_by('-date_joined')
    elif filter_query == 'voters':
        user_datas = User.objects.all()
    elif filter_query == 'editors':
        user_datas = User.objects.all()
    elif filter_query == 'moderators':
        user_datas = User.objects.all()
    else:
        user_datas = User.objects.filter(
            Q(username__startswith=filter_query)
        )

    context = {
        'title': 'Users - StackOverflow',
        'whichSelected': 'Users',
        'users': user_datas,
    }

    return render(request, 'base/users.html', context=context)


@login_required(login_url='login')
def discuss_room(request, id):
    specified_discuss = Discuss.objects.get(id=id)
    specified_discuss.views.add(request.user)  # added new user to views section

    context = {
        'specified_discuss': specified_discuss,
        'whichSelected': 'questions'
    }

    return render(request, 'base/discuss_room.html', context=context)


@login_required(login_url="login")
def create_discuss(request):
    template = 'base/create_discuss.html'

    form = DiscussForm()

    if request.method == 'POST':
        form = DiscussForm(request.POST)

        if form.is_valid():
            new_form = form.save(commit=False)

            new_form.user = request.user
            new_form.save()
            form.save_m2m()

            update_user()

            return redirect('questions')

    context = {
        'title': 'Create Discuss',
        'form': form
    }
    return render(request, template, context=context)


def update_user():
    discuss = Discuss.objects.all()

    temp_dict = {}

    for item in discuss:
        temp_dict[str(item.user)] = 0

    for item in discuss:
        temp_dict[str(item.user)] += 1

    for key, value in temp_dict.items():
        user = User.objects.get(username=key)
        user.myuser.quantity = value
        user.save()
