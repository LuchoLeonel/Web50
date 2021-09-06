from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass


class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_user")
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=400)
    image = models.URLField(blank=True)
    starting_bid = models.IntegerField()
    strongest_bid = models.IntegerField()
    winner = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="auction_winner")
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'ID {self.id} - User {self.user} - Title: {self.title} - Starting Bid: {self.starting_bid} - Strongest Bid: {self.strongest_bid} - Winner: {self.winner} - Active: {self.active} - Descripción: "{self.description}"'


class Bids(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bid_auction")
    bid = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"N°{self.id} - ${self.bid} offered by {self.user} for {self.auction.title} (ID {self.auction.id})"


class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comment_auction")
    comment = models.CharField(max_length=200)
    response = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'N°{self.id} - {self.user} comments {self.auction.title}: "{self.comment}"'


class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_user")
    list = models.ManyToManyField(Auction)

    def __str__(self):
        return f" N°{self.id}: {self.user} watchlist"


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    categoria = models.CharField(max_length=20)
    list = models.ManyToManyField(Auction)

    def __str__(self):
        return f"{self.categoria}"