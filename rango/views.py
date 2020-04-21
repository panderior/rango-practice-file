from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.google_custom_search import run_query
from django.contrib.auth.models import User

# HELPER FUNCTIONS


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(
        request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(
        last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# VIEWS


def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    # context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}

    # request.session.set_test_cookie()     # set test cookie

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context_dict)
    return response


def about(request):
    # prints out whether the method is a GET or a POST

    # if (request.session.test_cookie_worked()):    # check test cookie
    # print("TEST COOKIE WORKED!")
    # request.session.delete_test_cookie()

    print(request.method)
    # prints out the user name, if no one is logged in it prints `AnonymousUser`
    print(request.user)

    visitor_cookie_handler(request)
    context_dict = {'visits': request.session['visits']}
    response = render(request, 'rango/about.html', context_dict)
    return response


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    context_dict['query'] = category.name
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list
            context_dict['query'] = query

    return render(request, 'rango/category.html', context_dict)


@ login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


@ login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    registered = False

    if (request.method == 'POST'):
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if (user_form.is_valid() and profile_form.is_valid()):
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if ('picture' in request.FILES):
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    content_dict = {'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered
                    }

    return render(request, 'rango/register.html', content_dict)


def user_login(request):
    if (request.method == 'POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        content_dict = {}

        user = authenticate(username=username, password=password)
        if (user):
            if (user.is_active):
                login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            content_dict['incorrect_credentials'] = True
            return render(request, 'rango/login.html', content_dict)
    else:
        return render(request, 'rango/login.html', {})


@ login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))


def search(request):
    result_list = []
    query = ""
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})


def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


@login_required
def register_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user

            if ('picture' in request.FILES):
                profile.picture = request.FILES['picture']

            profile.save()
            return HttpResponseRedirect(reverse('rango:index'))
        else:
            print(profile_form.errors)
    else:
        profile_form = UserProfileForm()

    content_dict = {'form': profile_form}

    return render(request, 'rango/profile_registration.html', content_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango:index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})

    '''
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        website = request.POST.get('website')
        picture = request.FILES['picture']

        user.username = username
        user.email = email
        userprofile.website = website
        userprofile.picture = picture

        user.save()
        userprofile.save()

        return HttpResponseRedirect(reverse('rango:index'))

    content_dict = {'user': user, 'user_profile': user_profile}
    return render(request, 'rango/profile.html', content_dict)      '''

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)
    context_dict = {'userprofile': userprofile,
                    'selecteduser': user, 'form': form}
    return render(request, 'rango/profile.html', context_dict)


def list_users(request):
    user_profile_list = UserProfile.objects.all()
    users_list = []

    for user_profile in user_profile_list:
        user = user_profile.user
        website = user_profile.website
        user_info = {"username": user.username,
                     "email": user.email,
                     "website": website}
        users_list.append(user_info)

    content_dict = {'users_list': users_list}
    return render(request, 'rango/list_users_old.html', content_dict)


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    context_dict = {'userprofile_list': userprofile_list}

    return render(request, 'rango/list_profiles.html', context_dict)
