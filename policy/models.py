from django.db import models

# Create your models here.
class Policy(models.Model):
    name = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255, default="null")
    file_path = models.CharField(max_length=500)
    description = models.CharField(max_length=1000)
    is_active = models.SmallIntegerField(default=1)