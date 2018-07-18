from django.conf.urls import url
from . import views


urlpatterns = [
    url('^$', views.home, name="home"),
    url('^create user$', views.create_user, name="create-user"),
    url('^logout$', views.signout, name="logout"),
    url('^get-projects/$', views.load_projects, name="load-projects"),
    url('^get-projects/(?P<content>[a-z-A-Z-0-9]+)$', views.load_projects_with_filter, name="load-projects-with-filter"),
    url('^search/$', views.search, name="search"),
    url('^search/user/(?P<content>[a-z-A-Z-0-9]+)$', views.search_user, name="search-user"),
    url('^search/project/(?P<content>[a-z-A-Z-0-9]+)$', views.search_project, name="search-project"),
    url('^get-user/(?P<content>[a-z-A-Z-0-9]+)$', views.load_user, name='load-user'),
    url('^Dashboard/$', views.dashboard, name="dashboard"),
    url('^friends/send-request$', views.send_friend_request, name="send-friend-request"),
    url('^sync$', views.sync, name="sync"),
    url('^friends/accept-request$', views.accept_request, name="accept-request"),
    url('^friends/decline-request$', views.decline_request, name="decline-request"),
    url('^friends/view$', views.ViewFriends.as_view(), name="view-friends"),
    url('^friends/remove$', views.unfriend, name="remove-friend"),
    url('^Dashboard/create-project$', views.create_project, name="create-project"),
    url('^profile/$', views.EditProfile.as_view(), name="edit-profile"),
    url('^remove-invitation$', views.remove_invitation, name="remove-invitation"),
    url('^rate$', views.rate_project, name='rate'),
    url('^load-friends$', views.load_friends, name='load-friends'),
    url('^invite-friend$', views.invite_friend, name='invite-friend'),
    url('^profile/change-password$', views.ChangePassword.as_view(), name="change-password"),
    url('^project/view/(?P<pk>[0-9]+)$', views.ViewProject.as_view(), name="view-project"),
    url('^project/edit/(?P<pk>[0-9]+)$', views.EditProject.as_view(), name="edit-project"),
    url('^project/delete$', views.delete_project, name="delete-project"),
    url('^leave-comment$', views.leave_comment, name="leave-comment")


]
