from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class UserCredentials(models.Model):
    user_credential_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True)
    user_role = models.CharField(max_length=32, default='client')
    password = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, related_name='user_credentials', blank=True)

    class Meta:
        managed = False
        db_table = 'user_credentials'