from django.conf import settings
from openai import OpenAI
import re
from .models import Post
from django.db.models import Q

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

def clean_markdown(text):
    # Markdown işaretlerini temizle
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)  # ** ve * işaretlerini temizle
    text = re.sub(r'#{1,6}\s?', '', text)  # Başlık işaretlerini temizle
    text = text.replace('`', '')  # Kod bloğu işaretlerini temizle
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Linkleri temizle
    text = text.strip()
    return text

def generate_summary_and_tags(content, model_name="openai/gpt-4o-mini"):
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_SITE_NAME,
            },
            extra_body={},
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": """Lütfen aşağıdaki içeriğin özetini ve etiketlerini çıkar. 
                    Özet maksimum 250 karakter olmalı ve anlamlı bir şekilde bitmelidir.
                    Etiketler maksimum 5 tane olmalı ve blog içeriğiyle doğrudan ilgili olmalıdır.
                    
                    Yanıt formatı:
                    Önce özet (250 karakteri geçmemeli), sonra 'Etiketler:' başlığı altında en fazla 5 etiket.

                    İçerik:
                    """ + content
                }
            ]
        )
        response = completion.choices[0].message.content.strip()
        
        # Özet ve etiketleri ayır
        summary, _, tags = response.partition('\nEtiketler:')
        
        # Özeti temizle ve kısıtla
        summary = clean_markdown(summary)
        summary = summary.replace('Özet:', '').replace('ÖZET:', '').strip()
        if len(summary) > 250:
            summary = summary[:247] + '...'
        
        # Etiketleri temizle ve sınırla
        tags = clean_markdown(tags)
        tags_list = [tag.strip() for tag in tags.split() if tag.strip()][:5]
        tags = ' '.join(tags_list)
        
        return summary, tags.strip()
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return "Özet kullanılamıyor.", "#hata"

def search_related_posts(query, limit=3):
    """Verilen sorguyla ilgili blog postlarını ara"""
    # Gereksiz kelimeleri temizle
    stop_words = ['mı', 'mi', 'var', 've', 'veya', 'bir', 'bu', 'şu', 'nasıl', 'hakkında']
    words = [word.lower() for word in query.split() if word.lower() not in stop_words]
    
    # Eğer hiç kelime kalmazsa orijinal sorguyu kullan
    if not words:
        words = [query.lower()]
    
    print(f"Filtrelenmiş arama kelimeleri: {words}")  # Debug için
    
    # OR sorgusu oluştur
    q_objects = Q()
    
    for word in words:
        q_objects |= (
            Q(title__icontains=word) |
            Q(content__icontains=word) |
            Q(tags__icontains=word) |
            Q(summary__icontains=word)
        )
    
    try:
        # Arama yap ve benzerlik skoruna göre sırala
        posts = Post.objects.filter(q_objects).distinct()
        
        # Sonuçları puanla
        scored_posts = []
        for post in posts:
            score = 0
            post_text = f"{post.title.lower()} {post.content.lower()} {post.tags.lower()} {post.summary.lower()}"
            
            # Her kelime için puan hesapla
            for word in words:
                if word in post.title.lower():
                    score += 3  # Başlıkta bulunma
                if word in post.tags.lower():
                    score += 2  # Etiketlerde bulunma
                if word in post_text:
                    score += 1  # Genel içerikte bulunma
            
            scored_posts.append((post, score))
        
        # Skorlara göre sırala ve en yüksek puanlıları al
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        top_posts = [post for post, score in scored_posts[:limit]]
        
        print("\nBulunan postlar ve skorları:")
        for post, score in scored_posts[:limit]:
            print(f"- {post.title} (ID: {post.id}, Skor: {score})")
        
        return [post.to_search_format() for post in top_posts]
        
    except Exception as e:
        print(f"Arama hatası: {str(e)}")
        return []

def generate_chatbot_response(user_message, model_name="openai/gpt-4o-mini"):
    """Chatbot yanıtı ve ilgili postları oluştur"""
    try:
        # İlgili blog postlarını ara
        related_posts = search_related_posts(user_message)
        
        # Context'e blog postlarını ekle
        if related_posts:
            context = f"""Kullanıcının sorusu: {user_message}
            
Blog yazılarında bu konuyla ilgili içerik bulundu. Kullanıcıya kısa ve nazik bir şekilde yanıt ver."""
            
            system_prompt = """Sen SmartBlog AI asistanısın. Kullanıcıya kibar ve kısa bir yanıt ver. 
            İlgili blog yazılarından bahsetmene gerek yok, onlar zaten ayrıca listelenecek."""
            
        else:
            context = f"Kullanıcının sorusu: {user_message}"
            system_prompt = """Sen SmartBlog AI asistanısın. Kullanıcıya kısa ve faydalı bir yanıt ver. 
            Bu konuda henüz blog yazısı olmadığını nazikçe belirt ve yeni bir yazı oluşturmayı önerebilirsin."""

        print(f"\nSystem Prompt: {system_prompt}")
        print(f"Context: {context}")

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_SITE_NAME,
            },
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": context
                }
            ]
        )
        
        response = completion.choices[0].message.content.strip()
        return response, related_posts
            
    except Exception as e:
        print(f"Chatbot Error: {str(e)}")
        return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin.", []
