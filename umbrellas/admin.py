from django.contrib import admin
from .models import CustomUser, Umbrellas, RentalLog, UmbrellaLog
from umbrellas.management.commands.createUmbrella import Command

from django.urls import path
from .forms import UmbrellaCreationForm
from django.shortcuts import render, redirect

# Register your models here.
class CustomAdminSite(admin.AdminSite):
    site_header = "☔シェア傘管理画面☔"
    index_title = "傘レンタルシステム管理ページ"

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "faculty", "grade", "sex") 
    search_fields = ("username__icontains",)
    list_filter = ("faculty", "grade", "sex")

class UmbrellaAdmin(admin.ModelAdmin):
    list_display = ("umbrella_name", "borrower", "place", "last_lend", "create_at", "update_at")
    search_fields = ("borrower__icontains",)
    list_filter = ("place", "last_lend")

    # 管理画面にカスタムURLを追加して、フォームを表示
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create_umbrella/', self.create_umbrella_view, name="create_umbrella"),
        ]
        return custom_urls + urls

    # 管理画面からフォームの入力値で `handle()` を実行
    def create_umbrella_view(self, request):
        if request.method == "POST":
            form = UmbrellaCreationForm(request.POST)
            if form.is_valid():
                new_umbrellas = form.cleaned_data["new_umbrellas"]
                place = form.cleaned_data["place"]

                command = Command()
                command.handle(new_umbrellas=new_umbrellas, place=place)

                self.message_user(request, f"✅ {new_umbrellas} 本の傘を {place} に作成しました！")
                return redirect("/admin_share_kasa/umbrellas/")
        else:
            form = UmbrellaCreationForm()

        return render(request, "admin/create_umbrella.html", {"form": form})

    create_umbrella_view.short_description = "傘作成"

class UmbrellaLogAdmin(admin.ModelAdmin):
    list_display = ("umbrella_log", "create_at")
    search_fields = ("umbrella_log__icontains",)
    list_filter = ("create_at",)

admin_site = CustomAdminSite(name='custom_admin')

admin.site = admin_site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Umbrellas, UmbrellaAdmin)
admin.site.register(RentalLog)
admin.site.register(UmbrellaLog, UmbrellaLogAdmin)
