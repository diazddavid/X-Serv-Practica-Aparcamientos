from django.contrib import admin
from aparcamientos.models import Parking, Comment, User, Colour, AggregatedParking
# Register your models here.

admin.site.register(Parking)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Colour)
admin.site.register(AggregatedParking)
