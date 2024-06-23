from django.db import models
from django.utils import timezone

# Create your models here.


class User(models.Model):
    hn_username = models.CharField(max_length=100, db_index=True, unique=True)
    email = models.EmailField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.hn_username
