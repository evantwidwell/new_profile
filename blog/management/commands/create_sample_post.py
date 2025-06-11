from django.core.management.base import BaseCommand
from blog.models import Post
from datetime import date


class Command(BaseCommand):
    help = 'Creates a sample blog post'

    def handle(self, *args, **kwargs):
        if not Post.objects.exists():
            Post.objects.create(
                slug='welcome',
                title='Welcome to My Blog',
                date=date.today(),
                tags='welcome, first-post',
                summary='This is my first blog post.',
                content='''
# Welcome to My Blog

This is my first blog post. I'm excited to share my thoughts and experiences with you.

## What to Expect

- Technical tutorials
- Project updates
- Personal insights

Stay tuned for more content!
                '''
            )
            self.stdout.write(self.style.SUCCESS('Successfully created sample post'))
        else:
            self.stdout.write(self.style.WARNING('Posts already exist, skipping sample post creation')) 