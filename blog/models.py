# blog/models.py

import secrets
from django.db import models
from django.conf import settings # settings'i import et
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.postgres.search import SearchVectorField

class CustomUser(AbstractUser):
    # email alanı zaten AbstractUser'da var ama unique=True yapmak için override edebiliriz
    # veya AbstractUser kullanıyorsanız ve ekstra alan yoksa buna gerek olmayabilir.
    # Eğer AbstractUser'dan miras alıyorsanız ve sadece email'i unique yapmak istiyorsanız:
    email = models.EmailField(unique=True, blank=False, null=False) # unique ve zorunlu yapalım
    # İsteğe bağlı: Profil için ekstra alanlar buraya eklenebilir
    # bio = models.TextField(blank=True)
    # avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # USERNAME_FIELD ve REQUIRED_FIELDS AbstractUser'dan gelir,
    # Eğer email'i USERNAME_FIELD yapıyorsanız belirtin:
    USERNAME_FIELD = "email"
    # email USERNAME_FIELD ise, username REQUIRED_FIELDS'da olmalı
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        # email unique ve ana alan olduğu için onu döndürmek daha mantıklı olabilir
        return self.email


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    # HATA BURADAYDI: User yerine settings.AUTH_USER_MODEL kullan
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    summary = models.CharField(max_length=250, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # URL ismi doğruysa bu kalabilir
        return reverse('post-detail', kwargs={'pk': self.pk})

    def to_search_format(self):
            """Arama için post içeriğini formatla"""
            return {
            'id': self.id,
            'title': self.title,
            'content': self.content[:200],  # İlk 200 karakter
            'summary': self.summary,
            'tags': self.tags,
            'url': f'/post/{self.id}/' # Veya get_absolute_url() kullan
        }

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    # HATA BURADAYDI: User yerine settings.AUTH_USER_MODEL kullan
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Yazarın email'ini veya username'ini göstermek daha iyi olabilir
        return f'Comment by {self.author} on {self.post}'

class VerificationCode(models.Model):
    # BURAYI DA GÜNCELLE: User yerine settings.AUTH_USER_MODEL kullan
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="verification_codes")
    code = models.CharField(max_length=6, default=secrets.token_hex(3))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        # Yazarın email'ini veya username'ini göstermek daha iyi olabilir
        return f'Verification code for {self.user}' # Kullanıcıyı referans alalım