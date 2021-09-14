from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass


class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_user")
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    
    def __str__(self):
        return f'ID {self.id} - User {self.user} - Descripción: "{self.content}"'


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ManyToManyField(User)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="like_post")

    def __str__(self):
        return f'ID {self.id} - User {self.user} liked post {self.post.id}'


class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_user")
    followed = models.ManyToManyField(User)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ID {self.id} - User {self.follow} follow {self.followed}'


class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="comment_post")
    comment = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'N°{self.id} - {self.user} comments {self.post}: "{self.comment}"'

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "post": self.post.id,
            "comment": self.comment,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }