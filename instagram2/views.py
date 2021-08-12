from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import *
import json
import math
from django.db.models import Q, Max, Min

# Create your views here.
def myAbout(me):
    try:
        about = About.objects.get(user=me)
    except :
        about = About.objects.create(user=me)

    return about

@login_required(login_url='/accounts/login/')
def home(request):
    allposts = Post.objects.all().order_by('-id')
    paginator = Paginator(allposts, 2)
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)

    aboutMe = myAbout(request.user)
    followingUserId = []
    followingUser = aboutMe.following.all()
    for i in followingUser:
        followingUserId.append(i.id)
    randomUser = User.objects.all().exclude(id__in = followingUserId).exclude(id=request.user.id).order_by('?')[:5]
    #randomUser = list(randomUser.values())
    randomUserList = []
    for i in randomUser:
        l = {}
        l['id'] = i.id
        l['username'] = i.username
        aboutUser = myAbout(i)
        l['profilePicture'] = aboutUser.profilePicture.url

        randomFollower = aboutUser.followed_by.all().order_by('?').first()
        if request.user in aboutUser.following.all():
            l['randomFollower'] = 'Follows you'
        elif randomFollower == None:
            l['randomFollower'] = 'New to Instagram'
        else:
            l['randomFollower'] = randomFollower.username

        randomUserList.append(l)

    
    storiesIdList = []
    stories = Post.objects.all().order_by('?')[:7]
    for i in stories:
        aboutUser = About.objects.get(user=i.user).profilePicture
        i.userProfilePicture = aboutUser
        storiesIdList.append(i.id)

            
    return render(request, 'home.html', {
        'home': True,
        'post': post,
        'aboutMe': aboutMe,
        'randomUser': randomUserList,
        'stories': stories,
        'storiesIdList': storiesIdList,
    })


@login_required(login_url='/accounts/login/')
def getMorePost(request):
    data = json.loads(request.body.decode("utf-8"))

    if request.method == 'POST':
        postId = data['postId']

    post2 = Post.objects.exclude(id__in=postId).order_by('?')[:2]#[(page_number-1)*2:page_number*2]
    # for i in post2:
    #     print(i.image.url)
    post = list(post2.values())
    for i in post:
        user = User.objects.get(id=i['user_id'])
        i['userfullname'] = user.first_name+' '+user.last_name
        aboutUser = myAbout(user)
        i['userProfilePricture'] = aboutUser.profilePicture.url
        postt = Post.objects.get(id=i['id'])
        i['image'] = postt.image.url
        i['totallikes'] = postt.liked_by.count()
        
        if request.user in postt.liked_by.all():
            i['isLiked'] = True
        else:
            i['isLiked'] = False

        comments = Comment.objects.filter(post=postt)[:2]
        comments2 = list(comments.values())
        for ii in comments2:
            userfullname2 = User.objects.get(id=ii['user_id']).first_name
            ii['userfullname'] = userfullname2
        i['comments'] = comments2
        i['totalComments'] = Comment.objects.filter(post=postt).count()
    return JsonResponse({'response': post})


@login_required(login_url='/accounts/login/')
def getMoreComments(request, pk):
    post = get_object_or_404(Post, pk=pk)
    page = json.loads(request.body.decode("utf-8"))['page']
    page = int(page) - 1
    comments = Comment.objects.filter(post=post)[5*page+2:5*(page+1)+2]
    comments2 = list(comments.values())
    for ii in comments2:
        userfullname2 = User.objects.get(id=ii['user_id']).first_name
        ii['userfullname'] = userfullname2
    return JsonResponse({'response': comments2})



@login_required(login_url='/accounts/login/')
def likePost(request, pk):
    user = request.user
    try:
        post = get_object_or_404(Post, pk=pk)
        post.liked_by.add(user)
        return JsonResponse({'response': 'liked'})
    except:
        return JsonResponse({'response': '404'})

@login_required(login_url='/accounts/login/')
def cancelLikePost(request, pk):
    user = request.user
    try:
        post = get_object_or_404(Post, pk=pk)
        post.liked_by.remove(user)
        return JsonResponse({'response': 'likeCanceled'})
    except:
        return JsonResponse({'response': '404'})
    
    
@login_required(login_url='/accounts/login/')
def addComment(request, pk):
    user = request.user
    post = get_object_or_404(Post, pk=pk)
    data = json.loads(request.body.decode("utf-8"))
    Comment.objects.create(user=user, post=post, body=data['body'])
    return JsonResponse({'response': 'ok'})


@login_required(login_url='/accounts/login/')
def message(request):
    me = request.user
    myAllMsg = Message.objects.filter(Q(sender = me)|Q(receiver = me)).order_by('-date')
    conversationList = []
    for lastMsg in myAllMsg:
        if lastMsg.sender == me:
            if lastMsg.receiver not in conversationList:
                conversationList.append(lastMsg.receiver)
            
        else:
            if lastMsg.sender not in conversationList:
                conversationList.append(lastMsg.sender)

    conversationList2 = []
    for i in conversationList:
        l = {}
        l['id'] = i.id
        l['username'] = i.username
        lm = Message.objects.filter(Q(sender = me, receiver = i)|Q(receiver = me, sender = i)).last()
        try:
            lmb = lm.body
            if len(lmb) > 50:
                lmb = lmb[:50] + '...'
        except:
            lmb = 'Sent an Image'
        
        l['lm'] = lmb
        user = User.objects.get(id = i.id)
        aboutUser = myAbout(user)
        l['profilePicture'] = aboutUser.profilePicture.url
        conversationList2.append(l)
    
    try:
        myChatList = About.objects.get(user=me)
    except:
        myChatList = About.objects.create(user=me)
    
    for i in myChatList.chatList.all():
        if i not in conversationList:
            l = {}
            l['id'] = i.id
            l['username'] = i.username
            l['lm'] = 'Active 1 hour ago'
            conversationList2.append(l)

    aboutMe = myAbout(request.user)

    return render(request, 'message.html', {
        'message': True,
        'conversationList': conversationList2,
        'aboutMe': aboutMe,
    })

@login_required(login_url='/accounts/login/')
def conversation(request, pk):
    page = json.loads(request.body.decode("utf-8"))['pageNo']
    user1 = request.user.id
    user2 = User.objects.get(id=pk).id
    msg = Message.objects.filter(Q(receiver = user1, sender = user2)|Q(sender = user1, receiver = user2)).order_by('-date')[(page-1)*10:page*10]#.reverse()
    moreMessage = True
    if msg.count() == 0:
        moreMessage = False
    messages = list(msg.values())
    return JsonResponse({'messages': messages, 'moreMessage': moreMessage})


@login_required(login_url='/accounts/login/')
def sendMessage(request):
    sender = request.user
    try:
        data = json.loads(request.body.decode("utf-8"))
        receiverId = data['receiver']
        receiver = User.objects.get(id=receiverId)
        body = data['body']
        Message.objects.create(sender=sender, receiver=receiver, body=body)
        return JsonResponse({'response': 'sent'})
    except:
        image = request.FILES.get('image')
        receiverId = request.POST.get('receiver')
        receiver = User.objects.get(id=receiverId)
        Message.objects.create(sender=sender, receiver=receiver, image=image)
        return JsonResponse({'response': 'sent'})
    
    
@login_required(login_url='/accounts/login/')
def sendMessageFromStories(request):
    data = json.loads(request.body.decode("utf-8"))
    post = data['postId']
    receiver = Post.objects.get(id=post).user
    #receiver = User.objects.get(id=receiverId)
    body = data['body']
    sender = request.user
    Message.objects.create(sender=sender, receiver=receiver, body=body)
    return JsonResponse({'response': 'sent'})


@login_required(login_url='/accounts/login/')
def explore(request):
    posts = Post.objects.all().order_by('?')[:12]
    for i in posts:
        i.totalLikes = i.liked_by.all().count()
        i.totalComments = Comment.objects.filter(post=i.id).count()
    
    try:
        data = json.loads(request.body.decode("utf-8"))['exploreItemId']
        posts2 = Post.objects.all().exclude(id__in = data).order_by('?')[:12]

        noMoreExplorePost = False

        posts3 = list(posts2.values())

        countPost = posts2.count()
        if countPost < 12:
            needMore = 12-countPost
            morePosts = Post.objects.all().order_by('?')[:needMore]
            posts3.append(list(morePosts.values())[0])
            noMoreExplorePost = True


        for i in posts3:
            p = Post.objects.get(id=i['id'])
            i['totalLikes'] = p.liked_by.all().count()
            i['totalComments'] = Comment.objects.filter(post=p.id).count()
            i['image'] = p.image.url
            
        return JsonResponse({'posts': posts3, 'noMoreExplorePost': noMoreExplorePost})

    except:
        pass
    # allPosts = list(posts.values())
    # for i in allPosts:
    #     comments = Comment.objects.filter(post = i['id']).count()
    #     totalLikes = Post.objects.get(id=i['id']).liked_by.all().count()
    #     i['totalLikes'] = totalLikes
    #     i['totalComments'] = comments
    aboutMe = myAbout(request.user)
    return render(request, 'explore.html', {
        'explore': True,
        'posts': posts,
        'aboutMe': aboutMe,
    })


@login_required(login_url='/accounts/login/')
def exploreMore(request, pk):
    post = Post.objects.get(id=pk)
    post.totalLikes = post.liked_by.all().count()
    post.totalComments = Comment.objects.filter(post=pk).count()
    userAbout = myAbout(post.user)
    post.userProfilePicture = userAbout.profilePicture.url
    try:
        post.firstComment = Comment.objects.filter(post=pk)[:1][0]
    except :
        post.firstComment = False
    try:
        post.secondComment = Comment.objects.filter(post=pk)[1:2][0]
    except :
        post.secondComment = False
    
    
    #print(post.secondComment.values())
    aboutMe = myAbout(request.user)
    followingUserId = []
    followingUser = aboutMe.following.all()
    for i in followingUser:
        followingUserId.append(i.id)
    randomUser = User.objects.all().exclude(id__in = followingUserId).exclude(id=request.user.id).order_by('?')[:5]
    #randomUser = list(randomUser.values())
    randomUserList = []
    for i in randomUser:
        l = {}
        l['id'] = i.id
        l['username'] = i.username
        aboutUser = myAbout(i)
        l['profilePicture'] = aboutUser.profilePicture.url

        randomFollower = aboutUser.followed_by.all().order_by('?').first()
        if request.user in aboutUser.following.all():
            l['randomFollower'] = 'Follows you'
        elif randomFollower == None:
            l['randomFollower'] = 'New to Instagram'
        else:
            l['randomFollower'] = randomFollower.username

        randomUserList.append(l)

    return render(request, 'exploremore.html', {
        'p': post,
        'aboutMe': aboutMe,
        'randomUser': randomUserList,
        'exploreMore': True,
    })


@login_required(login_url='/accounts/login/')
def profile(request, pk):
    #myUsername = request.user.username
    user = User.objects.get(id=pk)
    aboutUser = myAbout(user)
    userPosts = Post.objects.filter(user=user).order_by('-date')
    # for i in userPosts:
    #     i.image = i.image.url
    #     i.totalLikes = i.liked_by.all().count()
    #     print(i.liked_by.all().count())
    #     i.totalComments = Comment.objects.filter(post=i.id).count()
    #     print(i.totalLikes)
    # print(userPosts.values())
    posts = []
    zero = 0
    zero2 = 0
    lenOfPosts = len(userPosts)
    userPosts = userPosts.values()
    
    subListLen = math.ceil(lenOfPosts/3)
    while zero < subListLen:
        subList = []
        while len(subList) < 3:
            try:
                subList.append(userPosts[zero2])
                zero2 += 1
            except :
                break
            
        posts.append(subList)
        zero += 1

    for i in posts:
        for j in i:
            post = Post.objects.get(id=j['id'])
            j['image'] = post.image.url
            j['totalLikes'] = post.liked_by.all().count()
            j['totalComments'] = Comment.objects.filter(post=post).count()

    aboutMe = myAbout(request.user)
    totalPosts = Post.objects.filter(user=user).count()
    return render(request, 'profile.html',{
        'aboutMe': aboutMe,
        'user': user,
        'aboutUser': aboutUser,
        'userPosts': posts,
        'totalPosts': totalPosts,
    })

@login_required(login_url='/accounts/login/')
def userPosts(request, pk):
    post = Post.objects.get(id=pk)
    post.totalLikes = post.liked_by.all().count()
    post.totalComments = Comment.objects.filter(post=pk).count()
    userAbout = myAbout(post.user)
    post.userProfilePicture = userAbout.profilePicture.url
    try:
        post.firstComment = Comment.objects.filter(post=pk)[:1][0]
    except :
        post.firstComment = False
    try:
        post.secondComment = Comment.objects.filter(post=pk)[1:2][0]
    except :
        post.secondComment = False
    
    
    #print(post.secondComment.values())
    aboutMe = myAbout(request.user)
    followingUserId = []
    followingUser = aboutMe.following.all()
    for i in followingUser:
        followingUserId.append(i.id)
    randomUser = User.objects.all().exclude(id__in = followingUserId).exclude(id=request.user.id).order_by('?')[:5]
    #randomUser = list(randomUser.values())
    randomUserList = []
    for i in randomUser:
        l = {}
        l['id'] = i.id
        l['username'] = i.username
        aboutUser = myAbout(i)
        l['profilePicture'] = aboutUser.profilePicture.url

        randomFollower = aboutUser.followed_by.all().order_by('?').first()
        if request.user in aboutUser.following.all():
            l['randomFollower'] = 'Follows you'
        elif randomFollower == None:
            l['randomFollower'] = 'New to Instagram'
        else:
            l['randomFollower'] = randomFollower.username

        randomUserList.append(l)

    return render(request, 'userposts.html', {
        'p': post,
        'aboutMe': aboutMe,
        'randomUser': randomUserList,
        'exploreMore': True,
    })


@login_required(login_url='/accounts/login/')
def getMoreUserPost(request):
    data = json.loads(request.body.decode("utf-8"))

    if request.method == 'POST':
        postId = data['postId']
    print(postId)
    post2 = Post.objects.filter(id__lt = postId[0], user = Post.objects.get(id=postId[0]).user).exclude(id__in=postId)[:2]#[(page_number-1)*2:page_number*2]
    # for i in post2:
    #     print(i.image.url)
    print(post2)
    post = list(post2.values())
    for i in post:
        user = User.objects.get(id=i['user_id'])
        i['userfullname'] = user.first_name+' '+user.last_name
        aboutUser = myAbout(user)
        i['userProfilePricture'] = aboutUser.profilePicture.url
        postt = Post.objects.get(id=i['id'])
        i['image'] = postt.image.url
        i['totallikes'] = postt.liked_by.count()
        
        if request.user in postt.liked_by.all():
            i['isLiked'] = True
        else:
            i['isLiked'] = False

        comments = Comment.objects.filter(post=postt)[:2]
        comments2 = list(comments.values())
        for ii in comments2:
            userfullname2 = User.objects.get(id=ii['user_id']).first_name
            ii['userfullname'] = userfullname2
        i['comments'] = comments2
        i['totalComments'] = Comment.objects.filter(post=postt).count()
    return JsonResponse({'response': post})


@login_required(login_url='/accounts/login/')
def editProfile(request):
    #myUsername = request.user.username
    aboutMe = myAbout(request.user)
    return render(request, 'editprofile.html',{
        'aboutMe': aboutMe,
    })


@login_required(login_url='/accounts/login/')
def uploadPhoto(request):
    #myUsername = request.user.username
    aboutMe = myAbout(request.user)
    return render(request, 'uploadphoto.html',{'aboutMe': aboutMe})


@login_required(login_url='/accounts/login/')
def photoUploadHandler(request):
    user = request.user
    if request.method == 'POST':
        img = request.FILES['photo']
        caption = request.POST['caption']
        Post.objects.create(user=user, image=img, caption = caption)
        return redirect('/profile')



def handleSignup(request):
    data = json.loads(request.body.decode("utf-8"))
    if request.method == 'POST':
        username = data['username']
        email = data['email']
        pass1 = data['pass1']
        pass2 = data['pass2']
        if len(username) < 1:
            return JsonResponse({'response':'Username can\'t be empty.'})
        if ' ' in username:
            return JsonResponse({'response':'Username must contain letters, digits and @/./+/-/_ only.'})
        if pass1!=pass2:
            return JsonResponse({'response':'The two password field didn\'t match.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'response':'This username is already taken. Please try another one.'})
        if len(pass1) < 4:
            return JsonResponse({'response':'Your password must contain at least 4 characters.'})

        try:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = data['fullname']
            myuser.save()
            messages.success(request, 'Your account created successfully.')
        except:
            return JsonResponse({'response':'Username must contain letters, digits and @/./+/-/_ only.'})
        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are Logged in.')
            return JsonResponse({'response':'ok'})
    else:
        return HttpResponse('404 - Page Not Found')

def handleLogin(request):
    data = json.loads(request.body.decode("utf-8"))
    if request.method == 'POST':
        username = data['username']
        password = data['pass']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are now Logged in.')
            return JsonResponse({'response': 'ok'})
        else:
            return JsonResponse({'response': 'Invalid username or password, please try again'})
        
    else:
        return HttpResponse('404 - Page Not Found')


def handleLogout(request):
    logout(request)
    messages.warning(request, 'You are Logged out.')
    #return JsonResponse({'response': 'ok'})
    return redirect(request.META['HTTP_REFERER'])



