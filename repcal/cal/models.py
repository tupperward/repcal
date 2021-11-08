from django.db import models
from django.db.models.fields.related import ForeignKey

# Create your models here.
class Calendar(models.Model):
    id = models.IntegerField(primary_key=True)
    month = models.CharField(max_length=200)
    month_of = models.CharField(max_length=200)
    week = models.IntegerField()
    day = models.IntegerField()
    sansculottides = models.BooleanField()
    item = models.CharField(max_length=200)
    item_url = models.CharField(max_length=200)

class LastTen(models.Model):
    index = models.IntegerField(primary_key=True)
    month = models.CharField(max_length=200)
    month_of = models.CharField(max_length=200)
    week = models.IntegerField()
    day = models.IntegerField()
    sansculottides = models.BooleanField()
    item = models.CharField(max_length=200)
    item_url = models.CharField(max_length=200)    