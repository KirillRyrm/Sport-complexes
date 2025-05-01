from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class UserCredentials(models.Model):
    user_credential_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True)
    user_role = models.CharField(max_length=32, default='client')
    password = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group,
                                    related_name='user_credentials',
                                    blank=True,
                                    through='UserCredentialsGroups'
                                    )
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'user_credentials'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return self.user_role == 'admin'

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.username


class UserCredentialsGroups(models.Model):
    user_credentials = models.ForeignKey(
        'UserCredentials',
        on_delete=models.CASCADE,
        db_column='usercredentials_id'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        db_column='group_id'
    )

    class Meta:
        managed = False
        db_table = 'auth_app_usercredentials_groups'