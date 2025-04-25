from django.contrib import admin
from .models import CustomUser, Umbrellas, RentalLog

# Register your models here.
class CustomAdminSite(admin.AdminSite):
    site_header = "☔シェア傘管理画面☔"
    index_title = "傘レンタルシステム管理ページ"

admin_site = CustomAdminSite(name='custom_admin')

admin.site = admin_site
admin.site.register(CustomUser)
admin.site.register(Umbrellas)
admin.site.register(RentalLog)