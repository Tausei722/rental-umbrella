from django.db import models

# Create your models here.
class Umbrellas(models.Model):
    id = models.AutoField(primary_key=True)
    unique_number = models.IntegerField(unique=True)
    prace = models.CharField(max_length=50)


# ユーザーDB(ユーザの基本情報と今時点でどの傘をレンタルしているかを記録)
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=225)
    password = models.CharField(max_length=225)
    umbrells = models.ForeignKey(Umbrellas, on_delete=models.PROTECT, null=True)
