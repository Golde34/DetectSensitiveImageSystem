from django.db import models
from django.contrib.auth.models import User


class Child(models.Model):
    key = models.CharField(max_length=12, primary_key=True)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    option = models.JSONField()


class Requests(models.Model):
    time = models.DateTimeField(auto_now=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=50)
    nude = models.IntegerField()
    sexy = models.IntegerField()
    safe = models.IntegerField()


class DomainStatistic(models.Model):
    requestNumber = models.IntegerField()
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=50)
    nude = models.IntegerField()
    sexy = models.IntegerField()
    safe = models.IntegerField()
    blocked = models.BooleanField(default=False)


class BrowserStatistic(models.Model):
    time = models.DateTimeField()
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    requestNumber = models.IntegerField()


class Notification(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    sensitivePercentage = models.FloatField()
    requestUrl = models.CharField(max_length=200)
    readed = models.BooleanField(default=False)
