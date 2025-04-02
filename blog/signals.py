from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Post, VerificationCode
from django.contrib.postgres.search import SearchVector
from django.utils import timezone
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        get_user_model().objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=Post)
def update_search_vector(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector('title', 'content', 'summary', 'tags', config='turkish')
    )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            VerificationCode.objects.create(user=instance, expires_at=timezone.now() + timezone.timedelta(minutes=5))
            instance.is_active=False
            instance.save()

        #email credentials
        verification_code = VerificationCode.objects.filter(user=instance).last()
        subject="E-posta Doğrulama"
        message = f"""
        Sayın {instance.username},  

        E-posta doğrulamanız için gerekli kod: {verification_code.code}  
        Bu kodun geçerlilik süresi 5 dakikadır.  
        Aşağıdaki bağlantıyı kullanarak doğrulama işlemini tamamlayabilirsiniz:  

        http://127.0.0.1:8000/verify-email/{instance.username}  

        İyi günler dileriz.  
        """

        sender = "berkatcekenn@gmail.com"
        receiver = [instance.email, ]

        #send email
        send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )
