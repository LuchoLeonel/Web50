from django.contrib import admin

from .models import User, Posts, Like, Follow, Comments

# Register your models here.
admin.site.register(User)
admin.site.register(Posts)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Comments)