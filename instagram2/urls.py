from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('message/', views.message, name='message'),
    path('explore/', views.explore, name='explore'),
    path('exploreMore/<str:pk>/', views.exploreMore, name='exploreMore'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('editProfile/', views.editProfile, name='editProfile'),
    path('handleSignup/', views.handleSignup, name='handleSignup'),
    path('handleLogin/', views.handleLogin, name='handleLogin'),
    path('getMorePost/', views.getMorePost, name='getMorePost'),
    path('likePost/<str:pk>/', views.likePost, name='likePost'),
    path('cancelLikePost/<str:pk>/', views.cancelLikePost, name='cancelLikePost'),
    path('addComment/<str:pk>/', views.addComment, name='addComment'),
    path('getMoreComments/<str:pk>/', views.getMoreComments, name='getMoreComments'),
    path('uploadPhoto/', views.uploadPhoto, name='uploadPhoto'),
    path('photoUploadHandler/', views.photoUploadHandler, name='photoUploadHandler'),
    path('sendMessage/', views.sendMessage, name='sendMessage'),
    path('conversation/<str:pk>/', views.conversation, name='conversation'),
    path('sendMessageFromStories/', views.sendMessageFromStories, name='sendMessageFromStories'),
    path('userPosts/<str:pk>/', views.userPosts, name='userPosts'),
    path('getMoreUserPost/', views.getMoreUserPost, name='getMoreUserPost'),
    path('follow/<str:pk>/', views.follow, name='follow'),
    path('unfollow/<str:pk>/', views.unfollow, name='unfollow'),
    path('getNotifications/', views.getNotifications, name='getNotifications'),
    path('searchUser/', views.searchUser, name='searchUser'),
]
