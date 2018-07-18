# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
import urllib
import urllib2
import json
from django.http import Http404
from .models import *
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from .forms import *
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView
from django.conf import settings
import math

index = 0
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December']

user_card_info = """
        <div class="card h-100">
            <a href="#"><img class="card-img-top" width="700" height="350" src="%s" alt="img"></a>
            <div class="card-body">
              <h4 class="card-title">
                <a href="#">%s</a>
              </h4>
                 <p class="card-text">name: %s %s</p>
                 <p>email: %s</p>
                 """

user_card_friends = """<div style="text-align: right"><p style="color: #132">already friends</p></div>"""

user_card_request_sent = """<div style="text-align: right"><p style="color: #132">sent a request</p></div>"""

user_card_request_not_sent = """<div style="text-align: right"><a id="%s" class="btn btn-primary" onclick="sendFriendRequest(this)" href="#">send friend request</a></div>"""

project_card = """<div class="card h-100">
              <div class="card-header" style="height: 80px">
                <div class="row">
                   <img src="%s" alt="img" width="50" height="50"/>
                    <p class="card-header-name">%s</p>
                    <p class="card-date">%s</p>
                </div>
              </div>
            <a href="%s"><img class="card-img-top" width="700" height="300" src="%s" alt="img"></a>
            <div class="card-body">
              <h4 class="card-title">
                  <a href="%s" style="margin-right: 5px">%s</a><span class="card-date" style="margin: 0;font-size: 13px">--%s</span>
              </h4>
              <p class="card-text">%s</p>
            </div>
          </div>
          """

friend_request = """<div>
                          <p> <b>%s</b> wants to be a friend with you</p>
                          <a id="accept-%s" onclick="acceptRequest(this)" style="width: 60px;padding: 3px" href="#" class="btn btn-success">accept</a>
                          <a id="decline-%s" onclick="declineRequest(this)" href="#">decline</a>
                          <div class="dropdown-divider"></div>
                      </div>
                      """

friend_suggestion = """<p><b>%s</b> invites you to see <a onclick="removeInvitation(this)" id="%s" href="%s">%s</a></p>"""

comment_formation  ="""<p>%s</p>
                  <small class="text-muted">Posted by %s on %s</small>
                  <hr/>"""

def aproximate(number):
    if int(number)+.5 <= number:
        return int(math.ceil(number))
    return int(math.floor(number))


def load_projects(request):
    global index
    index += 1
    projects = Project.objects.order_by('rating')
    if index >= len(projects):
        return JsonResponse({})

    project = projects[index]
    project.description = project.description[:80] + '...'
    return JsonResponse(create_project_data(project))


def load_projects_with_filter(request, content):
    global index
    index += 1
    projects = Project.objects.filter(name__contains=content)
    if index >= len(projects):
        return JsonResponse({})

    project = projects[index]
    project.description = project.description[:80] + '...'
    return JsonResponse(create_project_data(project))


@login_required()
def send_friend_request(request):
    user = get_object_or_404(User, pk=request.GET.get('pk', -1))
    if request.user.profile in user.friends.array.all() or request.user.profile in user.friends.array.all():
        return JsonResponse({})

    user.pendingfriendrequests.array.add(request.user.profile)
    user.pendingfriendrequests.save()
    return JsonResponse({'html': '<p style="color: #132">request sent</p>'})


def create_project_data(project):
    card = project_card%(project.user.profile.image.url, project.user.username,
                         project.pub_date, reverse('main:view-project', kwargs={'pk': project.pk}),
                         project.image.url, reverse('main:view-project', kwargs={'pk': project.pk}),
                         project.name, project.address, project.description)

    return {'html': card}


def create_user_data(user):
    card = user_card_info % (user.profile.image.url, user.username, user.first_name, user.last_name, user.email)
    if user.is_friend:
        card += user_card_friends
    elif user.request_sent:
        card += user_card_request_sent
    else:
        card += user_card_request_not_sent % (user.pk)

    card += "</div></div>"

    return {'html': card}


def load_user(request, content):
    global index
    index += 1

    users = User.objects.filter(username__contains=content, profile__account_type='normal').exclude(username=request.user.username)
    if index >= len(users):
        return JsonResponse({})
    if request.user.profile in users[index].friends.array.all():
        users[index].is_friend = True
    else:
        users[index].is_friend = False

    if request.user.profile in users[index].pendingfriendrequests.array.all() or users[index].profile in request.user.pendingfriendrequests.array.all():
        users[index].request_sent = True
    else:
        users[index].request_sent = False

    return JsonResponse(create_user_data(users[index]))


def signout(request):
    logout(request)
    return redirect(reverse('static-pages:index'))


def create_user(request):
    try:
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
            }
        
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        result = json.load(response)
        if not result['success']:
           raise ''
  
        user = User()
        user.username = request.POST['username']
        user.email = request.POST['email']

        user.set_password(request.POST['password'])
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']

        user.save()
        Profile(user=user, account_type=request.POST['user-type']).save()
    except:
        return redirect(reverse("static-pages:index"))

    if user.profile.account_type == 'normal':
        Friends(user=user).save()
        PendingFriendRequests(user=user).save()

    login(request, user)
    return redirect(reverse("main:home"))


@login_required()
def home(request):
    global index
    index = 8
    projects = Project.objects.order_by('rating')[:9]

    for project in projects:
        project.description = project.description[:80] + '...'

    normal_account = True if request.user.profile.account_type == 'normal' else False

    context = {
        'user': request.user,
        'custom_bootstrap': True,
        'normal_account': normal_account,
        'home_active': 'active',
        'data_url': reverse('main:load-projects'),
        'projects': projects

    }

    return render(request, 'main/home/home.html', context)


@login_required()
def search(request):
    option = request.POST['search_option']
    content = request.POST['content']

    if content == "":
        return redirect(reverse('main:home'))

    if ' ' in content:
        content = ''.join(content.split(' '))

    if option == 'user':
        return HttpResponseRedirect(reverse('main:search-user', kwargs={'content': content}))

    return HttpResponseRedirect(reverse('main:search-project', kwargs={'content': content}))


@login_required()
def search_user(request, content):
    if request.user.profile.account_type != 'normal':
        raise Http404
    global index
    users = User.objects.filter(username=content, profile__account_type='normal').exclude(username=request.user.username)

    if not users.exists():
        users = User.objects.filter(username__contains=content, profile__account_type='normal').exclude(username=request.user.username)

    if len(users) > 9:
        users = users[:9]
        index = 8
    else:
        index = len(users) - 1

    for user in users:
        if user.profile in request.user.friends.array.all():
            user.is_friend = True
        else:
            user.is_friend = False

        if request.user.profile in user.pendingfriendrequests.array.all() or\
                        user.profile in request.user.pendingfriendrequests.array.all():
            user.request_sent = True
        else:
            user.request_sent = False

    context = {
        'user': request.user,
        'users': users,
        'custom_bootstrap': True,
        'normal_account': True if request.user.profile.account_type == 'normal' else False,
        'data_url': reverse('main:load-user', kwargs={'content': content}),
    }
    if not users.exists():
        context['not_found'] = "couldn't find user " + content

    return render(request, 'main/home/home.html', context)


@login_required()
def search_project(request, content):
    global index
    projects = Project.objects.filter(name=content)
    if not projects.exists():
        projects = Project.objects.filter(name__contains=content)

    if len(projects) > 9:
        index = 8
    elif len(projects) < 9 and len(projects) != 0:
        index = len(projects) - 1

    for project in projects:
        project.description = project.description[:80] + '...'

    context = {
        'projects': projects,
        'user': request.user,
        'custom_bootstrap': True,
        'normal_account': True if request.user.profile.account_type == 'normal' else False,
        'data_url': reverse('main:load-projects-with-filter', kwargs={'content': content})
    }

    if not projects.exists():
        context['not_found'] = "couldn't find project " + content
    return render(request, 'main/home/home.html', context)


@login_required()
def dashboard(request):
    if request.user.profile.account_type == 'normal':
        return redirect(reverse('main:home'))

    return render(request, 'main/dashboard/dashboard.html', {
        'user': request.user,
        'normal_account': False,
        'dashboard_active': 'active',
        'projects': request.user.project_set.order_by('-pub_date')

    })


def remove_invitation(request):

    invitation = get_object_or_404(Suggestion, pk=request.GET.get('id', -1))
    request.user.profile.suggestions.remove(invitation)
    request.user.profile.save()
    return HttpResponse("")


def sync(request):
    requests = []
    suggestions = []
    for profile in request.user.pendingfriendrequests.array.all():
        html = friend_request%(profile.user.username, profile.pk, profile.pk)
        requests.append(html)

    for suggestion in request.user.profile.suggestions.all():
        html = friend_suggestion%(
            suggestion.user.username, suggestion.id,
            reverse('main:view-project', kwargs={'pk': suggestion.project.pk}),
            suggestion.project.name
        )
        suggestions.append(html)

    return JsonResponse({'friend_requests_length': len(requests),
                         'suggestions_length': len(suggestions),
                         'html': '\n'.join(requests+suggestions)
                    })


@login_required()
def leave_comment(request):
    text = request.GET.get('text', '')
    project = get_object_or_404(Project, pk=request.GET.get('projectId', -1))

    comment = Comment(user=request.user, text=text, project=project)
    comment.save()
    return HttpResponse(comment_formation%(text, request.user.username, comment.pub_date))


def accept_request(request):
    profile = get_object_or_404(Profile, pk=request.GET.get("id", -1))
    if profile in request.user.pendingfriendrequests.array.all():

        request.user.friends.array.add(profile)
        profile.user.friends.array.add(request.user.profile)
        profile.user.friends.save()

        request.user.friends.save()
        request.user.pendingfriendrequests.array.remove(profile)
        request.user.pendingfriendrequests.save()
    else:
        raise Http404
    return JsonResponse({'state': 'success'})


def decline_request(request):
    profile = get_object_or_404(Profile, pk=request.GET.get("id", -1))
    if profile in request.user.pendingfriendrequests.array.all():

        request.user.pendingfriendrequests.array.remove(profile)
        request.user.pendingfriendrequests.save()
    else:
        raise Http404
    return JsonResponse({'state': 'success'})


@login_required()
def create_project(request):
    if request.user.profile.account_type == 'normal':
        return redirect(reverse('main:home'))

    if request.method == "POST":
        form = ProjectCreationForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            form.save()
            return redirect(reverse('main:dashboard'))

        return redirect(reverse('main:create-project'))

    return render(request, 'main/dashboard/project_create.html',
                  {'user': request.user, 'dashboard_active': 'active', 'form': ProjectCreationForm(request=request)})


def delete_project(request):
    id = request.GET.get('pk', -1)
    project = get_object_or_404(Project, pk=int(id))

    if request.user != project.user:
        raise Http404

    project.delete()
    return JsonResponse({"id": id})


def unfriend(request):
    friend = get_object_or_404(Profile, pk=request.GET.get('id', -1))
    if friend in request.user.friends.array.all():
        request.user.friends.array.remove(friend)
        friend.user.friends.array.remove(request.user.profile)

        request.user.friends.save()
        friend.user.friends.save()

    return HttpResponse("")


@login_required()
def load_friends(request):
    friends = request.user.friends.array.all()
    FHTML = '<a href="#" onclick="inviteFriend(this)" id="%s"><b>%s %s (%s)</b></a><hr/>'
    html = ""
    for friend in friends:
        html += FHTML%(friend.user.id, friend.user.first_name, friend.user.last_name, friend.user.username)

    return HttpResponse(html)


@login_required()
def invite_friend(request):
    friend = get_object_or_404(User, pk=request.GET.get('friendId'))
    project = get_object_or_404(Project, pk=request.GET.get('projectId'))

    if friend.profile not in request.user.friends.array.all():
        raise Http404
    suggestion = Suggestion(user=request.user, project=project)
    suggestion.save()

    friend.profile.suggestions.add(suggestion)
    friend.profile.save()
    return HttpResponse("")


@login_required()
def rate_project(request):
    rating = int(request.GET.get('rating', 0))
    project = get_object_or_404(Project, pk=request.GET.get('id', -1))
    if project in request.user.profile.rated_projects.all():
        raise Http404

    if rating > 5 or rating < 0:
        raise Http404
    request.user.profile.rated_projects.add(project)
    project.rated_users += 1

    project.total_rating = project.total_rating + rating
    project.rating = (project.total_rating) / project.rated_users
    project.save()
    return HttpResponse("")


@method_decorator(login_required, name='dispatch')
class ViewProject(DetailView):
    model = Project
    context_object_name = 'project'
    template_name = 'main/project_view.html'

    def get_context_data(self, **kwargs):
        rate = aproximate(self.get_object().rating)
        context = super(ViewProject, self).get_context_data(**kwargs)
        context['normal_account'] = True if self.request.user.profile.account_type == 'normal' else False

        context['full_stars'] = [i for i in range(rate)]
        context['empty_stars'] = [i for i in range(5-rate)]
        context['user_rated'] = self.get_object() in self.request.user.profile.rated_projects.all()
        return context


@method_decorator(login_required, name='dispatch')
class EditProject(UpdateView):
    model = Project
    template_name = 'main/dashboard/project_create.html'
    context_object_name = 'form'
    form_class = ProjectCreationForm

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if self.request.user.profile.account_type == 'normal':
            return redirect(reverse('main:home'))

        if project.user != self.request.user:
            raise Http404
        return super(EditProject, self).get(self, pk)

    def get_context_data(self, **kwargs):
        context = super(EditProject, self).get_context_data(**kwargs)
        project = self.get_object()
        self.get_form_class().project = project

        context['longitude'] = project.longitude
        context['latitude'] = project.latitude
        context['update_mode'] = True
        return context


@method_decorator(login_required, name='dispatch')
class EditProfile(UpdateView):
    model = User
    template_name = 'main/profile.html'
    form_class = UserProfileForm
    context_object_name = 'form'
    success_url = '/home/'

    def get_object(self, queryset=None):
        self.get_form_class().user = self.request.user
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super(EditProfile, self).get_context_data(**kwargs)
        context['image'] = self.request.user.profile.image.url
        context['normal_account'] = True if self.request.user.profile.account_type == 'normal' else False
        context['profile_active'] = 'active'
        return context


@method_decorator(login_required, name='dispatch')
class ChangePassword(UpdateView):
    model = User
    form_class = PasswordChangeForm

    template_name = 'main/profile.html'
    context_object_name = 'form'
    success_url = '/home/'

    def get_object(self, queryset=None):
        self.get_form_class().request = self.request
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super(ChangePassword, self).get_context_data(**kwargs)
        context['password_phase'] = True
        context['normal_account'] = True if self.request.user.profile.account_type == 'normal' else False
        context['profile_active'] = 'active'
        return context


@method_decorator(login_required, name='dispatch')
class ViewFriends(ListView):
    model = Friends
    context_object_name = 'friends'
    template_name = 'main/friends.html'

    def get(self, request, *args, **kwargs):
        if request.user.profile.account_type != 'normal':
            raise Http404
        return super(ViewFriends, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.friends.array.all()

    def get_context_data(self, **kwargs):
        context = super(ViewFriends, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['normal_account'] = True
        return context
