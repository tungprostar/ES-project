from django.db import models

# Create your models here.

class Result:
    image = models.ImageField(upload_to='images/')
