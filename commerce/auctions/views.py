from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from .models import Comments, User, Auction, Bids, Watchlist, Categoria


#class New_Auction(forms.Form):
    #title = forms.CharField(label="Title", min_length = 3, max_length = 20, help_text="Title")
    #description = forms.CharField(label="Description", widget=forms.Textarea, min_length = 20, max_length = 1000, help_text="Description")
    #image = forms.URLField(label="Image URL", help_text="URL")
    #bid = forms.IntegerField(help_text="Bid")
    #categories = forms.CharField(help_text="Categories")

def index(request):
    auctions = Auction.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "auctions": auctions,
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Corroboramos que el nombre de usuario no haya sido usado.
        users = User.objects.values()
        for user in users:
            if user == username:
                return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        # Guardamos el valor del formulario en auction, y los datos del user aparte
        auction = request.POST
        title = auction["title"]
        current_user = request.user

        # Creamos una variable que guarde la estructura del form Auction y le asignamos un valor a cada variable.
        auction_save = Auction(user = current_user, title = title, description = auction["description"],
                        image = auction["image"], starting_bid = auction["bid"], strongest_bid = auction["bid"],
                        winner = current_user, active = True)

        # Guardamos aparte el titulo de la auction y el user que la creó.
        auctions_title = Auction.objects.values('title')
        auctions_user = Auction.objects.values('user')
        
        # Verificamos: Si el mismo user ya creó una auction con ese título le salta error.
        for i in range(len(auctions_title)):
            if title == auctions_title[i]["title"] and current_user.id == auctions_user[i]["user"]:
                return render(request, "auctions/create.html", {
                    "message": "You already publish this item.",
                })
        
        # Guardamos el form de la nueva auction y guardamos la categoría en el otro form aparte.
        auction_save.save()
        try:
            categoria = Categoria.objects.get(categoria = request.POST["categoria"])
            categoria.list.add(auction_save)
        except (ObjectDoesNotExist):
            categoria = ""
        return HttpResponseRedirect(f"listing/{title}")

    else:
        # Si no es method POST, guardamos las categorias y renderizamos la página.
        categorias = Categoria.objects.all()
        return render(request, "auctions/create.html", {
            "categorias": categorias,
        })



def auction(request, name):
    if request.method == "POST":
        # Vamos a guardar los datos de la auction donde concuerde el name.
        auction_dates = Auction.objects.get(title=name)
        # Vamos a guardar la categoria.
        categoria = Categoria.objects.filter(list=auction_dates)
        # Guardamos los datos de todos los comentarios de esa auction.
        comments = Comments.objects.filter(auction=auction_dates)
        # Vamos a guardar los datos enviados por el form.
        auction = request.POST

        # Si la información enviada por el formulario es "Close Auction":
        if 'close' in request.POST:
            if auction["close"] == "Close Auction":
                # Guardamos todas las bids que concuerden con esta auction
                auction_bids = Bids.objects.filter(auction=auction_dates)
                # Revisamos en las bids si alguna bid concuerda con la strongest bid de la auction.
                for auction_bid in auction_bids:
                    if auction_dates.strongest_bid == auction_bid.bid:
                        # Guardamos el usuario ganador.
                        auction_dates.winner = User.objects.get(id=auction_bid.user_id)
                # Cambiamos el estado de la auction a inactivo y guardamos los cambios.
                auction_dates.active = False
                auction_dates.save()
                # Renderizamos la página.
                return render(request, "auctions/auction.html", {
                            "auction": auction_dates,
                            "comments": comments,
                            "categorias": categoria,
                        })

        # Si la información enviada por el formulario es "Re-open Auction":
        if 'reopen' in request.POST:
            if auction["reopen"] == "Re-open Auction":
                # Cambiamos el estado a activa, borramos al ganador y guardamos.
                auction_dates.active = True
                auction_dates.winner = request.user
                auction_dates.save()
                # Renderizamos la página.
                return render(request, "auctions/auction.html", {
                        "auction": auction_dates,
                        "comments": comments,
                        "categorias": categoria,
                        })
        
        # Si lo que se envió en el formulario es un comentario:
        if 'comment' in request.POST:
            # Guardamos el comentario en un form.
            comment = Comments(user = request.user, auction = auction_dates, comment = request.POST["comment"])
            comment.save()
            # Conseguimos todos los comentarios de esa auction (con el comentario nuevo incluido).
            comments = Comments.objects.filter(auction=auction_dates)
            # Renderizamos la página.
            return render(request, "auctions/auction.html", {
                "auction": auction_dates,
                "comments": comments,
                "categorias": categoria,
                "message": "Comment sucessfully added",
                })
        
        # Buscamos si se dió respuesta a algun comentario:
        for comment in comments:
            if f'{comment.id}' in request.POST:
                # Guardamos la respuesta a ese comentario.
                comment.response = request.POST[f'{comment.id}']
                comment.save()
                # Renderizamos la página.
                return render(request, "auctions/auction.html", {
                    "auction": auction_dates,
                    "comments": comments,
                    "categorias": categoria,
                    "message": "Response sucessfully added",
                    })

        # Si lo que se envió en el form es una newbid:
        if 'newbid' in request.POST:
            # Si la bid que ofrecí no supera la starting_bid, tira un mensaje de error.
            if int(auction["newbid"]) < auction_dates.starting_bid:
                return render(request, "auctions/auction.html", {
                    "auction": auction_dates,
                    "comments": comments,
                    "categorias": categoria,
                    "message": "Bid not high enought"
                })

            # Vamos a guardar todas las bids de esa auction.
            auction_bids = Bids.objects.filter(auction=auction_dates)
            # Si nuestra bid es menor a alguna otra bid, nos va a tirar un mensaje de error.
            for auction_bid in auction_bids:
                if int(auction["newbid"]) <= auction_bid.bid:
                    return render(request, "auctions/auction.html", {
                        "auction": auction_dates,
                        "comments": comments,
                        "categorias": categoria,
                        "message": "Bid not high enought"
                    })

            # Si nuestra bid es mayor a las otras, se va a guardar la strongest_bid
            auction_dates.strongest_bid = int(auction["newbid"])
            auction_dates.save()
            # Y se va a crear un form con esta nueva bid.
            auction_save = Bids(user = request.user, auction = auction_dates, bid = int(auction["newbid"]))
            auction_save.save()
            
            # Finalmente, renderizamos la página.
            return render(request, "auctions/auction.html", {
                "auction": auction_dates,
                "comments": comments,
                "categorias": categoria,
                "message": "Bid sucessfully placed."
                }) 

        # Si con el form queremos agregar a la watchlist:
        if 'watchlist' in request.POST:
            # Probamos conseguir la watchlist correspondiente a este user y, si existe, guardamos esta auction. 
            try:
                watch = Watchlist.objects.get(user = request.user)
                watch.list.add(auction_dates)
            except (ObjectDoesNotExist):
                # Si no existe creamos una nueva watchlist para este user, y le agregamos esta auction.
                watch = Watchlist(user = request.user)
                watch.save()
                watch.list.add(auction_dates)
            # Guardamos y renderizamos la página.
            watch.save()
            return render(request, "auctions/auction.html", {
                    "auction": auction_dates,
                    "comments": comments,
                    "categorias": categoria,
                    "watchlist": watch,
                    "message": "Se guardó en la Watchlist"
                    })
        
        # Si con el form queremos remover una auction de la watchlist:
        if 'watchremove' in request.POST:
            # Probamos conseguir esta auction que tiene guardada este user en su watchlist y la borramos.
            try:
                watch = Watchlist.objects.get(user = request.user, list=auction_dates)
                watch.list.remove(auction_dates)
            # Si no existe, que es poco probable, le asignamos un valor vacio a la variable.
            except (ObjectDoesNotExist):
                watch = ""
            # Renderizamos la página.
            return render(request, "auctions/auction.html", {
                    "auction": auction_dates,
                    "comments": comments,
                    "categorias": categoria,
                    "watchlist": watch,
                    "message": "Se borró de la Watchlist"
                    })

    if request.method == "GET":
        # Vamos a obtener todas las auctions.
        auctions = Auction.objects.values()      

        # Vamos a buscar la auction que concuerda con el nombre.
        for i in range(len(auctions)):
                if name == auctions[i]["title"]:
                    # Cuando la encontramos la guardamos.
                    auction = Auction.objects.get(title=name)

                    # Vamos a guardar la categoria.
                    categoria = Categoria.objects.filter(list=auction)
                    # Guardamos los comentarios que corresponden a esta auction.
                    comments = Comments.objects.filter(auction=auction)

                    # Buscamos si la auction está en la watchlist del user.
                    if request.user.is_authenticated:
                        try:
                            watch = Watchlist.objects.get(user = request.user, list=auction)
                        except (ObjectDoesNotExist):
                            watch = ""
                    else:
                        watch = ""
                    # Renderizamos la página.
                    return render(request, "auctions/auction.html", {
                        "auction": auction,
                        "comments": comments,
                        "categorias": categoria,
                        "watch": watch,
                    })

        # Si no la encontramos, tira un mensaje de Not Found.
        return render(request, "auctions/index.html", {
            "auctions": auctions,
            "message": f"Not Found: {name}"
        })


@login_required(login_url='login')
def watchlist(request):   
    # Probamos conseguir todas las auctions dentro de la watchlists de este usuario.
    try:
        watchs = Watchlist.objects.get(user = request.user).list.all()
    # Si no tiene una watchlist, guarda un valor vacio en la variable watch.
    except (ObjectDoesNotExist):
        watchs = ""
    # Renderiza la página.
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchs,
        })


def categories(request):
    categories = Categoria.objects.all()

    # Creamos una lista vacia, y vamos a agregar todas las auction donde el user creador sea el user logueado.
    categoria = []
    for categorie in categories:
        categoria.append(categorie.categoria)

    # Renderizamos la página y pasamos los nombres de las categorias.
    return render(request, "auctions/categories.html", {
        "categorias": categoria,
    })

def category(request, categoria):
    # Probamos conseguir todas las auctions dentro de la categoria señalada.
    try:
        auctions = Categoria.objects.get(categoria = categoria).list.filter(active=True)
    # Si no hay auctions en esa categoria, guarda un valor vacio en la variable.
    except (ObjectDoesNotExist):
        auctions = ""
    # Renderizamos la página.
    return render(request, "auctions/category.html", {
        "auctions": auctions,
        "categoria": categoria,
    })


@login_required(login_url='login')
def mylisting(request):
    # Guardamos el id del user que esta logueado, y también guardamos los valores de todas las auctions.
    actualuser = request.user.id
    auctions = Auction.objects.values()

    # Creamos una lista vacia, y vamos a agregar todas las auction donde el user creador sea el user logueado.
    mylist = []
    for auction in auctions:
        if auction["user_id"] == actualuser:
            mylist.append(auction)

    # Renderizamos la página y pasamos los valores de mylist.
    return render(request, "auctions/mylisting.html", {
        "auctions": mylist,
    })