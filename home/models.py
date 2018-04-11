from django.db import models
from django.utils import timezone


# Create your models here.
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(blank=True , null = True)
    contact=models.CharField(max_length=13)
    subject=models.CharField(max_length=200, blank=True, null=True)  
    message=models.TextField(max_length=300, blank=True, null=True)
    datetime=models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name

    class Meta:
    	verbose_name_plural = "Contact us entries"
