from django.contrib import admin
from .models import CustomUser, Umbrellas, RentalLog

# Register your models here.
class CustomAdminSite(admin.AdminSite):
    site_header = "☔シェア傘管理画面☔"
    index_title = "傘レンタルシステム管理ページ"

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "faculty", "grade", "sex") 
    search_fields = ("name__icontains",)
    list_filter = ("faculty", "grade", "sex")

class UmbrellaAdmin(admin.ModelAdmin):
    list_display = ("umbrella_name", "borrower", "prace", "last_lend", "create_at", "update_at")
    search_fields = ("borrower__icontains",)
    list_filter = ("prace", "last_lend")

admin_site = CustomAdminSite(name='custom_admin')

admin.site = admin_site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Umbrellas, UmbrellaAdmin)
admin.site.register(RentalLog)