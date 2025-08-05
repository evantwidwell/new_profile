from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "tags")
    list_filter = ("date", "tags")
    search_fields = ("title", "content", "tags")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "date"
