from django.contrib import admin
from django.utils.html import format_html

from .models import MutedPost, User


class MutedPostInline(admin.TabularInline):
    model = MutedPost
    extra = 0
    readonly_fields = ("created_at", "hn_link")

    @admin.display(description="HN post")
    def hn_link(self, obj):
        if not obj.post_id:
            return ""
        url = f"https://news.ycombinator.com/item?id={obj.post_id}"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)


class UserAdmin(admin.ModelAdmin):
    inlines = [MutedPostInline]


admin.site.register(User, UserAdmin)
