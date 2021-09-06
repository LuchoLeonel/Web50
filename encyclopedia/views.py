from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from random import randrange
import markdown2


from . import util


class NewTaskForm(forms.Form):
    name = forms.CharField(label="search")


class Title(forms.Form):
    title = forms.CharField(label="", min_length = 3, max_length = 20)
    
class Body(forms.Form):
    body = forms.CharField(label="", widget=forms.Textarea, min_length = 2)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "form": NewTaskForm(),
        "entries": util.list_entries()
    })


def search(request, name):
    if util.get_entry(name):
        pag = util.get_entry(name)
        pages = markdown2.Markdown()
        return render(request, "encyclopedia/search.html", {
            "form": NewTaskForm(),
            "name": name.upper(),
            "pages": pages.convert(pag),
            "namenormal": name,
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "form": NewTaskForm(),
            "name": name.upper(),
    })


def similar(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            if util.get_entry(name):
                return HttpResponseRedirect(f"/wiki/{name}")
            else:
                listado = []
                listas = util.list_entries()
                for lista in listas:
                    lista2 = lista.casefold()
                    lista3 = lista2.capitalize()
                    if lista.find(name) >= 0 or lista2.find(name) >= 0 or lista3.find(name) >= 0:
                        listado.append(lista)
                if len(listado) > 0:
                    return render(request, "encyclopedia/similar_search.html", {
                    "form": form,
                    "name": name.upper(),
                    "entries": listado
                })
                else:
                    return render(request, "encyclopedia/error.html", {
                    "form": form,
                    "name": name.upper(),
                    })
    else:
        return render(request, "encyclopedia/index.html", {
                "form": NewTaskForm()
                })


def create(request):
    if request.method == "POST":
        title = Title(request.POST)
        title = title["title"].value()
        body = Body(request.POST)
        body = "#" + title + "\n\n" + body["body"].value()
        if util.get_entry(title):
            return render(request, "encyclopedia/noguardo.html", {
                "form": NewTaskForm(),
                "name": title.upper(),
            })
        else:
            util.save_entry(title, body)
            return HttpResponseRedirect(f"/wiki/{title}")

    else:
        return render(request, "encyclopedia/create.html", {
            "form": NewTaskForm(),
            "title": Title(),
            "body": Body(),
    })


def modify(request, name):
    
    if request.method == "POST":
        title = request.POST["title"]
        body = "#" + title + "\n\n" + request.POST["body"]
        util.save_entry(title, body)
        return HttpResponseRedirect(f"/wiki/{title}")
    else:
        if util.get_entry(name):
            pages = util.get_entry(name)
            largo = len(name) + 4
            pages = pages[largo:len(pages)]
            return render(request, "encyclopedia/modify.html", {
                "form": NewTaskForm(),
                "name": name,
                "body": pages,
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "form": NewTaskForm(),
                "name": name.upper(),
        })



def random(request):
    listas = util.list_entries()
    ran = randrange(0, len(listas))
    for i in range(len(listas)):
        if i == ran:
            name = listas[i]
    
    return HttpResponseRedirect(f"/wiki/{name}")