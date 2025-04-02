# blog/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView
)
from . import views

# Not: Şablonlarınızın dosya yollarının (template_name) doğru olduğundan emin olun.
# Örneğin: 'blog/password_reset.html'

urlpatterns = [
    # Post URL'leri
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),

    # Kullanıcı Profili ve Chatbot
    path('profile/', views.profile, name='profile'),
    path('chatbot/message/', views.chatbot_message, name='chatbot-message'),

    # Kayıt ve Doğrulama URL'leri
    path('register/', views.register, name='register'),
    path('verify-email/<str:username>/', views.verify_email, name='verify-email'), # Eksikti, eklendi
    path('resend-token/', views.resend_verification_code, name='resend-token'),    # Eksikti, eklendi

    # Giriş / Çıkış URL'leri
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='blog/logout.html'), name='logout'),

    # Standart Django Parola Sıfırlama URL'leri
    # (Özel reset_password view'ı yerine bunları kullanmak daha yaygındır)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='blog/password_reset.html',
             email_template_name='blog/password_reset_email.html', # E-posta şablonu
             subject_template_name='blog/password_reset_subject.txt' # E-posta konu şablonu
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='blog/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='blog/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='blog/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

# Önemli Not: Parola sıfırlama için yukarıdaki standart Django view'larını
# kullanıyorsanız, ilgili şablonları (password_reset.html,
# password_reset_done.html, password_reset_confirm.html,
# password_reset_complete.html, password_reset_email.html,
# password_reset_subject.txt) 'templates/blog/' klasörünüzde oluşturmanız
# veya mevcutları bu isimlerle güncellemeniz gerekir.