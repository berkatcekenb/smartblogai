# blog/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# forms modülü zaten yukarıda import edilmiş, bu satır gereksiz.
# from django import forms

# Comment modelini models dosyasından import et:
from .models import Comment

class UserRegistrationForm(UserCreationForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={"placeholder": "E-posta adresinizi girin", "class":"form-control"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Kullanıcı adınızı girin", "class":"form-control"}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Şİfrenizi girin", "class":"form-control"}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder": "Şİfrenizi doğrulayın", "class":"form-control"}))

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = {
            'invalid_login': '❌ Kullanıcı adı veya şifre hatalı!',
            'inactive': '⚠️ Bu hesap aktif değil.',
        }

    # UserLoginForm için Meta sınıfı aslında gerekli değil,
    # AuthenticationForm bunu kendi hallediyor ama zarar vermez.
    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment  # Artık 'Comment' tanımlı olacak
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class':'form-control', 'placeholder': 'Yorumunuzu buraya yazın...'}) # Stil ekledim
        }

# Not: Bu PasswordResetForm önceki incelemede belirtildiği gibi
# standart Django akışına uymuyor. Eğer kullanacaksanız,
# ilgili view (views.reset_password) ve mantığın olduğundan emin olun.
class PasswordResetForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    security_answer = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"})) # Güvenlik sorusu?
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Şifreler eşleşmiyor!") # Türkçe mesaj
        return cleaned_data