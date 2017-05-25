from django.db import models
import django.contrib.auth.models as modelsAuth

# Create your models here.

class Parking(models.Model):
    name = models.CharField(max_length = 128)
    neighborhood = models.CharField(max_length = 64)
    district = models.CharField(max_length = 64)
    email = models.CharField(max_length = 64)
    address = models.CharField(max_length = 64)
    tlf = models.CharField(max_length = 64)
    city = models.CharField(max_length = 64)
    latitude = models.FloatField()
    longitude = models.FloatField()
    Ncomments = models.IntegerField()
    points = models.IntegerField()
    access = models.IntegerField()
    descrip = models.TextField()
    url = models.TextField()

class Colour(models.Model):
    colorName = models.CharField(max_length = 64, default='sinColor')

class User(models.Model):
    user = models.OneToOneField(modelsAuth.User)
    colour = models.ForeignKey(Colour)
    fontSize = models.IntegerField(default=0)
    pageName = models.CharField(max_length = 64)

class AggregatedParking(models.Model):
    aggregationDate = models.DateField(auto_now_add=True)
    parking = models.ForeignKey(Parking)
    user = models.ForeignKey(User)

class Comment(models.Model):
    user = models.ForeignKey(modelsAuth.User)
    comment = models.TextField()
    parking = models.ForeignKey(Parking)
