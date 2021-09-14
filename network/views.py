from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.utils import Error
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from django.core.exceptions import ObjectDoesNotExist

from .models import Comments, User, Posts, Follow, Like


def index(request):
    posts = Posts.objects.all()
    posts = posts.order_by("-timestamp").all()
    p = Paginator(posts, 10)
    lista = p.get_elided_page_range(1, on_each_side=2, on_ends=1)
    range = p.page_range
    
    return render(request, "network/index.html", {
        "posts": p.page(1),
        "page_num": 1,
        "listas": lista,
        "range": range,
    })


def pagination(request, page):
    posts = Posts.objects.all()
    posts = posts.order_by("-timestamp").all()
    p = Paginator(posts, 10)
    lista = p.get_elided_page_range(page, on_each_side=2, on_ends=1)
    range = p.page_range

    return render(request, "network/index.html", {
        "posts": p.page(page),
        "page_num": page,
        "listas": lista,
        "range": range,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Corroboramos que el nombre de usuario no haya sido usado.
        users = User.objects.values()
        for user in users:
            if user == username:
                return render(request, "network/register.html", {
                "message": "Username already taken."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":        
        post = request.POST
        post_save = Posts(user = request.user, content = post["content"])
        post_save.save()
        
        return HttpResponseRedirect(reverse("index"))


def usuario(request, name, page):
    if request.method == "GET":
        # Vamos a obtener los datos del user y sus posts.
        try:
            user = User.objects.get(username=name)
        except (ObjectDoesNotExist):
            return render(request, "network/usuario.html", {
            "message": "Este usuario no existe"
            })

        try:
            posts = Posts.objects.filter(user=user)
            posts = posts.order_by("-timestamp").all()
            p = Paginator(posts, 10)
            lista = p.get_elided_page_range(page, on_each_side=2, on_ends=1)
            range = p.page_range
        except (ObjectDoesNotExist):
            posts = ""

        try:
            followers = Follow.objects.filter(followed = user)
        except (ObjectDoesNotExist):
            followers = ""
        
        try:
            follows = Follow.objects.get(follow = user).followed.all()
        except (ObjectDoesNotExist):
            follows = ""
        
        if request.user.is_authenticated:
            try:
                if Follow.objects.get(follow=request.user, followed=user):
                    follow_or_unfollow = True
            except (ObjectDoesNotExist):
                follow_or_unfollow = False
        else:
            follow_or_unfollow = False

        diccionario =  {
            "follows": len(follows),
            "followers": len(followers),
            "bollean": follow_or_unfollow,
        }

        # Renderizamos la página.
        return render(request, "network/usuario.html", {
            "users": user,
            "posts": p.page(page),
            "page_num": page,
            "listas": lista,
            "range": range,
            "dic": diccionario
            })


@csrf_exempt
@login_required(login_url='login')
def follow_unfollow(request, name):
    if request.method == "POST":
        followed = User.objects.get(username = name)

        data = json.loads(request.body)
        if data["action"] == "follow":    
            if name == request.user.username:
                return HttpResponse(status=404)
            #  
            try:
                follow_save = Follow.objects.get(follow = request.user)
                follow_save.followed.add(followed)
            except (ObjectDoesNotExist):
                follow_save = Follow(follow = request.user)
                follow_save.save()
                follow_save.followed.add(followed)

            # Guardamos y renderizamos la página.
            follow_save.save()
            return HttpResponse(status=204)

        if data["action"] == "unfollow":
            try:
                follow_save = Follow.objects.get(follow = request.user, followed = followed)
                follow_save.followed.remove(followed)
                follow_save.save()
            except (ObjectDoesNotExist):
                follow_save = ""

            # Guardamos y renderizamos la página.
            return HttpResponse(status=204)


@login_required(login_url='login')
def following(request, page):   
    # 
    try:
        follows = Follow.objects.get(follow = request.user).followed.all()    
        posts = Posts.objects.filter(user__in=follows).order_by("-timestamp").all()
    except (ObjectDoesNotExist):
        return render(request, "network/usuario.html")

    p = Paginator(posts, 10)
    lista = p.get_elided_page_range(page, on_each_side=2, on_ends=1)
    range = p.page_range

    return render(request, "network/following.html", {
        "follows": p.page(page),
        "page_num": page,
        "listas": lista,
        "range": range,
    })


@csrf_exempt
@login_required(login_url='login')
def edit(request, post_id):
    if request.method == "GET":
        try:
            post = Posts.objects.get(pk=post_id)
        except (ObjectDoesNotExist):
            return JsonResponse({"error": "Invalid post."}, status=400)
            
        return JsonResponse({
            "content": post.content,
        })
    if request.method == "PUT":
        try:
            post = Posts.objects.get(pk=post_id)
        except (ObjectDoesNotExist):
            return JsonResponse({"error": "Post not found."}, status=404)

        if request.user != post.user:
            return JsonResponse({"error": "Invalid user."}, status=404)
        data = json.loads(request.body)
        if post.editado == False and post.content != data["content"]:
            post.editado = True
        post.content = data["content"]
        post.save()
        return HttpResponse(status=204)


@csrf_exempt
@login_required(login_url='login')
def like(request, post_id):
    if request.method == "POST":
        try:
            post = Posts.objects.get(pk=post_id)
            data = json.loads(request.body)
            action = data.get("action", "")
            if action == "like":
                try:
                    like = Like.objects.get(post=post)
                    like.user.add(request.user)
                except (ObjectDoesNotExist):
                    like = Like(post = post)
                    like.save()
                    like.user.add(request.user)
            if action == "unlike":
                like = Like.objects.get(post=post)
                like.user.remove(request.user)
                like.save()
            users = set()
            users.update(like.user.all())
            post.likes = len(users)
            post.save()
            return HttpResponseRedirect(reverse("index"))
        
        except (ObjectDoesNotExist):
            return JsonResponse({"error": "Invalid post."}, status=400)

    if request.method == "GET":
        post = Posts.objects.get(pk=post_id)
        try:
            like = Like.objects.get(post=post)
            users = set()
            users.update(like.user.all())
            likes = len(users)
        except (ObjectDoesNotExist):
            likes = 0
            
        return HttpResponse(likes)


@csrf_exempt
@login_required(login_url='login')
def likes_inicial(request, post_id):
    if request.method == "GET":
        post = Posts.objects.get(pk=post_id)
        try:
            like = Like.objects.get(post=post)
            users = set()
            users.update(like.user.all())
            if request.user in users:
                si = True
            else:
                si = False
        except (ObjectDoesNotExist):
            si = False
            
        return HttpResponse(si)


@csrf_exempt
def comments(request, post_id):
    post = Posts.objects.get(pk=post_id)
    if request.method == "GET":
        try:
            comments = Comments.objects.filter(post=post)
        except (ObjectDoesNotExist):
            comments = ""
        comments = comments.order_by("-timestamp").all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    if request.method == "POST":
        data = json.loads(request.body)
        if data["comment"] == '':
            return HttpResponse(status=204)
        comment = Comments(user = request.user, post = post, comment = data["comment"])
        comment.save()
        return HttpResponse(status=204)

