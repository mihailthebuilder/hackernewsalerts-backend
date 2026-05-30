from django.db import models
from django.utils import timezone

# Create your models here.


class User(models.Model):
    hn_username = models.CharField(max_length=100, db_index=True, unique=True)
    email = models.EmailField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.hn_username


class MutedPost(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="muted_posts"
    )
    post_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post_id")

    def __str__(self):
        return f"{self.user.hn_username} muted {self.post_id}"
