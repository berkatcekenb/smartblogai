from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User  # User modelini ekledik
from .models import Post, Comment
from .utils import generate_summary_and_tags, generate_chatbot_response, client  # client ekledik
from .forms import UserRegistrationForm, CommentForm, PasswordResetForm, UserLoginForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.contrib.auth import login

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-created_date']
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        summary, tags = generate_summary_and_tags(form.instance.content, "openai/gpt-4o-mini")
        form.instance.summary = summary
        form.instance.tags = tags
        self.object = form.save()
        messages.success(self.request, '✨ Blog yazınız başarıyla oluşturuldu!')
        return redirect('blog-home')

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        # İçerik güncellendiğinde özet ve etiketleri yeniden oluştur
        summary, tags = generate_summary_and_tags(form.instance.content, "openai/gpt-4o-mini")
        form.instance.summary = summary
        form.instance.tags = tags
        self.object = form.save()
        messages.info(self.request, '✏️ Blog yazınız güncellendi!')
        return redirect('post-detail', pk=self.object.pk)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.warning(request, '🗑️ Blog yazısı silindi!')
        return super().delete(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save security question and answer to UserProfile
            user.userprofile.security_question = form.cleaned_data.get('security_question')
            user.userprofile.security_answer = form.cleaned_data.get('security_answer')
            user.userprofile.save()
            messages.success(request, '🎉 Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'blog/register.html', {'form': form})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post-detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form, 'pk': pk})  # pk'yı context'e ekledik

@login_required
def profile(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile
        user_profile.bio = request.POST.get('bio', '')
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']
        user_profile.save()
        messages.success(request, '👤 Profil bilgileriniz güncellendi!')
        return redirect('profile')
    return render(request, 'blog/profile.html')

def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
                if user.userprofile.security_answer == form.cleaned_data['security_answer']:
                    user.password = make_password(form.cleaned_data['new_password'])
                    user.save()
                    messages.success(request, '🔐 Şifreniz başarıyla sıfırlandı!')
                    return redirect('login')
                else:
                    messages.error(request, 'Invalid security answer')
            except User.DoesNotExist:
                messages.error(request, '❌ Kullanıcı bulunamadı!')
    else:
        form = PasswordResetForm()
    return render(request, 'blog/reset_password.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'🎉 Hoş geldiniz, {user.username}!')
            return redirect('blog-home')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    else:
        form = UserLoginForm()
    return render(request, 'blog/login.html', {'form': form})

@csrf_exempt
@require_POST
def chatbot_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        try:
            # Test et - client çalışıyor mu?
            print("Client test:", client.base_url, client.api_key)
            
            # Chatbot yanıtı ve ilgili postları al
            bot_response, related_posts = generate_chatbot_response(user_message)
            
            return JsonResponse({
                'response': bot_response,
                'related_posts': related_posts
            })
            
        except Exception as e:
            print("OpenAI Error:", str(e))  # Hata loglaması ekledik
            return JsonResponse({
                'error': f'OpenAI API error: {str(e)}'
            }, status=500)
            
    except Exception as e:
        print("General Error:", str(e))  # Genel hata loglaması
        return JsonResponse({'error': str(e)}, status=500)
