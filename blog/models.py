from django.db import models

class Post(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    date = models.DateField()
    tags = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField()

    def __str__(self):
        return self.title
