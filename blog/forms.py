from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Comment, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    security_question = forms.CharField(help_text='Enter a security question for password reset')
    security_answer = forms.CharField(help_text='Enter the answer to your security question')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'security_question', 'security_answer']

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = {
            'invalid_login': '❌ Kullanıcı adı veya şifre hatalı!',
            'inactive': '⚠️ Bu hesap aktif değil.',
        }
    
    class Meta:
        model = User
        fields = ['username', 'password']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4})
        }

class PasswordResetForm(forms.Form):
    username = forms.CharField()
    security_answer = forms.CharField()
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data
