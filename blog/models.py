from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, default='')  # default='' ekledik
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    security_question = models.CharField(max_length=200, blank=True, default='')  # default='' ekledik
    security_answer = models.CharField(max_length=200, blank=True, default='')  # default='' ekledik

    def __str__(self):
        return self.user.username

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    summary = models.CharField(max_length=250, blank=True)  # TextField yerine CharField ve max_length eklendi
    tags = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('post-detail', kwargs={'pk': self.pk})  # API URL'i yerine blog detay URL'i

    def to_search_format(self):
        """Arama için post içeriğini formatla"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content[:200],  # İlk 200 karakter
            'summary': self.summary,
            'tags': self.tags,
            'url': f'/post/{self.id}/'
        }

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
