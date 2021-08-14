from django.db import models
from django.contrib.auth.models import User
#from django.db.models.enums import Choices
# Create your models here.

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField(max_length=10000, blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    liked_by = models.ManyToManyField(User, related_name='liked_by', blank=True)
    date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField(max_length=1000)

    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    body = models.TextField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)


class About(models.Model):
    user = models.OneToOneField(User, related_name='about', on_delete=models.CASCADE)
    profilePicture = models.ImageField(upload_to='images/profile/', default = 'images/useravater.png')
    followed_by = models.ManyToManyField(User, related_name='followed_by', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)
    chatList = models.ManyToManyField(User, related_name='chatList', blank=True)
    bio = models.TextField(max_length=10000, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    choice = (
        ('like', 'liked'),
        ('comment', 'commented'),
        ('follow', 'following')
    )
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    topic = models.CharField(max_length=20, choices=choice, default='like')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
