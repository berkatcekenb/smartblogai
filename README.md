# SmartBlog AI 🤖

Yapay zeka destekli modern blog platformu.

## 🌟 Özellikler

### AI Destekli Özellikler
- **Otomatik İçerik Analizi**: Blog yazılarınız için otomatik özet çıkarma
- **Akıllı Etiketleme**: İçeriğe göre otomatik etiket önerileri
- **AI Asistan**: Blog yazarken size yardımcı olacak ChatGPT benzeri asistan
- **İçerik Arama**: Gelişmiş yapay zeka destekli içerik arama sistemi

### Blog Özellikleri
- Kullanıcı kayıt ve giriş sistemi
- Blog yazısı oluşturma, düzenleme ve silme
- Yorum sistemi
- Kullanıcı profilleri ve avatar sistemi
- Mobil uyumlu modern tasarım

## 🛠️ Teknolojiler

### Backend
- Python 3.8+
- Django 4.2+
- PostgreSQL
- OpenAI API/OpenRouter API

### Frontend
- HTML5 & CSS3
- JavaScript (Pure JS)
- Bootstrap 5
- Font Awesome Icons

## 📝 Kurulum

1. Repo'yu klonlayın
```bash
git clone https://github.com/yourusername/smartblog.git
cd smartblog
```

2. Virtual environment oluşturun ve aktifleştirin
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

4. .env dosyasını oluşturun ve gerekli değişkenleri ayarlayın
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
OPENROUTER_API_KEY=your-api-key-here

DB_NAME=smartblog
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

5. PostgreSQL veritabanını oluşturun
```bash
# PostgreSQL komut satırında:
createdb smartblog
```

6. Migrasyonları uygulayın
```bash
python manage.py migrate
```

7. Geliştirme sunucusunu başlatın
```bash
python manage.py runserver
```

## 🗂️ Proje Yapısı

```
smartblog/
├── blog/                   # Ana uygulama
│   ├── api/               # API views ve serializers
│   ├── migrations/        # Veritabanı migrasyonları
│   ├── templates/         # Blog template'leri
│   └── static/           # Statik dosyalar
├── templates/             # Genel template'ler
├── static/               # Genel statik dosyalar
│   ├── css/             # Stil dosyaları
│   └── js/              # JavaScript dosyaları
└── smartblog/           # Proje ayarları
```

## 🔧 Arayüz Bileşenleri

### Chatbot
- Real-time AI asistan
- İlgili blog yazılarını önerme
- Mesaj geçmişi
- Karakter sayacı

### Blog Yazıları
- Zengin metin editörü
- Otomatik özet oluşturma
- Etiket önerileri
- Mobil uyumlu görünüm

### Kullanıcı Profilleri
- Avatar yükleme
- Biyografi düzenleme
- Yazı ve yorum geçmişi
- İstatistikler

## 📱 Responsive Tasarım
- Bootstrap grid sistemi
- Mobil öncelikli yaklaşım
- Esnek UI bileşenleri
- Touch-friendly etkileşimler

## 🔒 Güvenlik

- CSRF koruması
- Authentication sistemi
- Güvenli parola yönetimi
- API rate limiting

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit'leyin (`git commit -m 'feat: Add amazing feature'`)
4. Branch'i push'layın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Katkıda Bulunanlar

- [Adınız](https://github.com/yourusername)
