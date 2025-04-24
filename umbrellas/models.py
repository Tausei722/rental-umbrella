from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, BaseUserManager

# ユーザーDB(ユーザの基本情報と今時点でどの傘をレンタルしているかを記録)
STATUS_FACULTY = [
        ('Engineering', '工学部'),
        ('Agriculture', '農学部'),
        ('Science','理学部'),
        ('Humanities and Social', '人文社会学部'),
        ('International Regional Revitalization', '国際地域創生学部'),
        ('Education', '教育学部'),
        ('Medical', '医学部'),
        ('Graduate school', '大学院'),
        ('Parties involved', '関係者'),
        ('other', '学外者'),
    ]

STATUS_GRADE = [
        ('first', '学部1年'),
        ('second', '学部2年'),
        ('third', '学部3年'),
        ('fourth', '学部4年'),
        ('fifth', '院1年'),
        ('sixth', '院2年'),
    ]

STATUS_SEX = [
        ('male', '男性'),
        ('female', '女性'),
        ('no answer', '解答しない'),
    ]

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        # create_user と create_superuser の共通処理
        if not email:
            raise ValueError('email must be set')
        if not username:
            raise ValueError('username must be set')
 
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
 
        return user
 
    def create_user(self, username, email=None, password=None, **extra_fields):
 
        if not email:
            raise ValueError('email must be set')
        if not username:
            raise ValueError('username must be set')
 
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
 
        return self._create_user(email, username, password, **extra_fields)
 
    def create_superuser(self, username, email=None, password=None, **extra_fields):
 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
 
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
 
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
 
        return self._create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=225)
    password = models.CharField(max_length=225)
    faculty = models.CharField(max_length=225,choices=STATUS_FACULTY)
    grade = models.CharField(max_length=225,choices=STATUS_GRADE)
    sex = models.CharField(max_length=225,choices=STATUS_SEX)
    create_at = models.DateField(auto_now_add=True, null=True)
    update_at = models.DateField(auto_now=True, null=True)

    # related_nameを指定して衝突を回避(djangoのデフォルトの設定のauth.Userモデルと競合しているらしい)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.name

class Umbrellas(models.Model):
    STATUS_PRACE = [
        ('Library', '図書館'),
        ('North cafeteria', '北食堂'),
        ('Central cafeteria', '中央食堂'),
        ('Engineering faculty', '工学部棟'),
        ('Agriculture faculty', '農学部棟'),
        ('Sience faculty', '理系複合棟'),
        ('Literal faculty', '文系複合棟'),
        ('Senbaru domitory', '千原寮共用棟'),
    ]

    id = models.AutoField(primary_key=True)
    umbrella_name = models.CharField(max_length=225)
    borrower = models.ForeignKey(CustomUser,null=True,on_delete=models.SET_NULL,related_name='borrowed_user')
    prace = models.CharField(max_length=225,choices=STATUS_PRACE)
    last_lend = models.DateField()
    create_at = models.DateField(auto_now_add=True, null=True)
    update_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return self.umbrella_name


class Prace(models.Model):
    STATUS_PRACE = [
        ('Library', '図書館'),
        ('North cafeteria', '北食堂'),
        ('Central cafeteria', '中央食堂'),
        ('Engineering faculty', '工学部棟'),
        ('Agriculture faculty', '農学部棟'),
        ('Sience faculty', '理系複合棟'),
        ('Literal faculty', '文系複合棟'),
        ('Senbaru domitory', '千原寮共用棟'),
    ]

    id = models.AutoField(primary_key=True)
    prace_name = models.CharField(max_length=225,choices=STATUS_PRACE)
    return_umbrellas = models.ManyToManyField(Umbrellas,related_name='prace_return_umbrellas')
    create_at = models.DateField(auto_now_add=True, null=True)
    update_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return self.prace
    
# どの傘が誰にいつ借りられたか（返されたか）を記録するDB
class RentalLog(models.Model):
    id = models.AutoField(primary_key=True)
    create_at = models.DateField(auto_now=True, null=True)
    user = models.ForeignKey(CustomUser,null=False,on_delete=models.DO_NOTHING,related_name='active_user')
    umbrella = models.ForeignKey(Umbrellas,null=False,on_delete=models.DO_NOTHING,related_name='rentaled_umbrella')
    is_rental = models.BooleanField(default=False)