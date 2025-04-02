from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User  # User modelini ekledik
from .models import Post, Comment, VerificationCode
from .utils import generate_summary_and_tags, generate_chatbot_response, client  # client ekledik
from .forms import UserRegistrationForm, CommentForm, PasswordResetForm, UserLoginForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.contrib.auth import login, get_user_model, authenticate
from django.utils import timezone



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
            # Kullanıcıyı kaydet (ancak henüz aktif etme, sinyal halledecek)
            user = form.save(commit=False)
            # Şifre hashlenir vs. form.save() bunu yapar.
            # Sinyalimiz User modeli kaydedildiğinde zaten çalışacak
            # ve is_active=False yapıp doğrulama kodu gönderecek.
            # Bu yüzden burada tekrar is_active=False yapmaya gerek yok.
            user.save()

            # Başarı mesajı güncellendi - doğrulama gerekli
            messages.success(request, '🎉 Hesabınız oluşturuldu! Lütfen e-postanızı kontrol ederek hesabınızı doğrulayın.')

            # Doğrulama sayfasına yönlendir. Kullanıcı adını formdan almak daha güvenli.
            # username = form.cleaned_data.get('username') # forms.py'deki UserCreationForm'da username alanı varsa
            # Eğer CustomUser modelinde USERNAME_FIELD = 'email' ise email'i kullanmak gerekebilir.
            # Şimdilik POST verisinden alalım ama formdan almak daha iyi.
            username_from_post = request.POST.get('username') # forms.py'deki forma göre 'username' veya 'email' olabilir
            return redirect('verify-email', username=username_from_post)
        else:
            # Form geçerli değilse, hatalarla birlikte formu tekrar göster
            # Context'te anahtar olarak 'forms' yerine 'form' kullanmak daha yaygın
            context = {'form': form}
            return render(request, 'blog/register.html', context)
    else:  # GET isteği ise (sayfa ilk açıldığında)
        form = UserRegistrationForm()  # Boş bir form oluştur
        context = {'form': form}       # Boş formu contexte ekle
        # Kayıt sayfasını boş formla birlikte render et ve döndür
        return render(request, 'blog/register.html', context)

def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    code = VerificationCode.objects.filter(user=user).last()

    if request.method == "POST":
        # valid token
        if code.code == request.POST['code']:

            # checking for expired token
            if code.expires_at > timezone.now():
                user.is_active=True
                user.save()
                messages.success(request, "Hesabınız başarıyla doğrulandı. Giriş yapabilirsiniz.")
                return redirect("blog/home")

            # expired token
            else:
                messages.warning(request, "Doğrulama kodunun süresi dolmuş. Yeni bir doğrulama kodu isteyin.")
                return redirect("verify-email", username=user.username)

        # invalid verification code
        else:
            messages.warning(request, "Doğrulama kodu geçerisiz, Doğru kodu girin!")
            return redirect("verify-email", username=user.username)
    context = {}
    return render(request, "verify_token.html", context)

def resend_verification_code(request):
    if request.method == 'POST':
        user_email = request.POST["code_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            code = VerificationCode.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(minutes=5))

            # email variables
            subject = "E-posta Doğrulama"
            message = f"""
                    Sayın {user.username},  

                    E-posta doğrulamanız için gerekli kod: {code.code}  
                    Bu kodun geçerlilik süresi 5 dakikadır.  
                    Aşağıdaki bağlantıyı kullanarak doğrulama işlemini tamamlayabilirsiniz:  

                    http://127.0.0.1:8000/verify-email/{user.username}  

                    İyi günler dileriz.  
                    """

            sender = "berkatcekenn@gmail.com"
            receiver = [user.email, ]

            # send email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )

            messages.success(request, "Yeni doğrulama kodu e-posta adresinize gönderilmiştir.")
            return redirect("verify-email", username=user.username)

        else:
            messages.warning(request, "Sisteme kayıtlı böyle bir e-posta bulunamadı.")
            return redirect("resend-token")




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

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, f'🎉 Hoş geldiniz, {request.user.username}!')
            return redirect('blog-home')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
                return redirect('login')
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
