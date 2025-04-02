# blog/admin.py

from django.contrib import admin
# UserAdmin'i import ediyoruz, CustomUser adminini özelleştirmek için kullanışlıdır.
from django.contrib.auth.admin import UserAdmin
# Modellerimizi import ediyoruz: UserProfile yerine CustomUser geldi.
from .models import CustomUser, Post, Comment

# CustomUser modelini admin paneline kaydediyoruz.
# UserAdmin'i kullanarak standart kullanıcı yönetimi özelliklerini (şifre, gruplar, izinler vb.) sağlıyoruz.
# Eğer CustomUser modeline özel alanlar eklediyseniz (örn. bio, avatar),
# bu alanları da admin panelinde göstermek için UserAdmin'den miras alan
# özel bir admin sınıfı (örn. CustomUserAdmin) oluşturup onu burada kullanabilirsiniz.
# Şimdilik temel UserAdmin yeterli olacaktır.
admin.site.register(CustomUser, UserAdmin)

# Diğer modelleri kaydediyoruz.
admin.site.register(Post)
admin.site.register(Comment)

# Eğer CustomUserAdmin'i özelleştirmek isterseniz örnek:
# class CustomUserAdmin(UserAdmin):
#     # UserAdmin'in fieldset'lerini kopyalayıp kendi alanlarınızı ekleyin
#     fieldsets = UserAdmin.fieldsets + (
#         ('Ekstra Profil Bilgileri', {'fields': ('bio', 'avatar')}), # Varsayılan CustomUser'da yok, eklenirse...
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         ('Ekstra Profil Bilgileri', {'fields': ('bio', 'avatar')}), # Varsayılan CustomUser'da yok, eklenirse...
#     )
# admin.site.register(CustomUser, CustomUserAdmin) # Yukarıdaki yerine bunu kullanırsınız