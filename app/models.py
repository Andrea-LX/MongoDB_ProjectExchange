from django.db import models
from django.contrib.auth.models import User
from djongo.models.fields import ObjectIdField, Field


class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    btcAmount = models.FloatField(default=0)
    btcBalance = models.FloatField(default=0)
    profit = models.FloatField(default=0)

class purchaseOrder(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()

    def updateStatus(self):
        self.active = False

class saleOrder(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()

    def updateStatus(self):
        self.active = False

