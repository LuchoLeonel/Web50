
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:page>", views.pagination, name="pagination"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("usuario/<str:name>/<int:page>", views.usuario, name="usuario"),
    path("following/<int:page>", views.following, name="following"),
    path("follow/<str:name>", views.follow_unfollow, name="follow_unfollow"),
    path("post/<int:post_id>", views.edit, name="edit"),
    path("like/<int:post_id>", views.like, name="like"),
    path("likes/<int:post_id>", views.likes_inicial, name="likes"),
    path("comments/<int:post_id>", views.comments, name="comments"),
]
