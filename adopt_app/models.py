from django.db import models


# Create your models here


class Pet(models.Model):
    petfinder_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)