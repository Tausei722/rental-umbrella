from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, BaseUserManager

# ユーザーDB(ユーザの基本情報と今時点でどの傘をレンタルしているかを記録)
STATUS_FACULTY = [
        ('Engineering', '工学部'),
        ('Agriculture', '農学部'),
        ('Science','理学部'),
        ('Humanities and Social', '人文社会学部'),
        ('International Regional Revitalization', '国際地域創造学部'),
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

    def _create_user(self, username, email, password, **extra_fields):
        # create_user と create_superuser の共通処理
        if not username:
            raise ValueError('username must be set')
        if not email:
            raise ValueError('email must be set')
 
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
 
        return user
 
    def create_user(self, username, email=None, password=None, **extra_fields):
 
        if not username:
            raise ValueError('username must be set')
        if not email:
            raise ValueError('email must be set')

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
 
        return self._create_user(username, email, password, **extra_fields)
 
    def create_superuser(self, username, email=None, password=None, **extra_fields):
 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
 
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
 
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
 
        return self._create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("名前",max_length=50,unique=True)
    email = models.EmailField("メールアドレス",max_length=225,unique=True)
    password = models.CharField("パスワード",max_length=225)
    faculty = models.CharField("学部",max_length=225,choices=STATUS_FACULTY)
    grade = models.CharField("学年",max_length=225,choices=STATUS_GRADE)
    sex = models.CharField("性別",max_length=225,choices=STATUS_SEX)
    create_at = models.DateField("登録日",auto_now_add=True, null=True)
    update_at = models.DateField("変更された日",auto_now=True, null=True)
    borrowed_umbrella = models.ForeignKey(
        "Umbrellas",
        verbose_name="借りている傘",
        null=True,  # 🔥 `null=True` で傘を借りていない状態を許容！
        blank=True,
        on_delete=models.SET_NULL,  # ✅ ユーザーが削除されても傘情報は残す！
        related_name="current_borrower"
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

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

    objects = CustomUserManager()

    def set_password(self, raw_password):
        super().set_password(raw_password) 

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "アカウント"
        verbose_name_plural = "アカウント画面"

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

    umbrella_name = models.CharField("傘整理番号",max_length=225)
    borrower = models.ForeignKey(CustomUser,verbose_name="貸出者",null=True,blank=True,on_delete=models.SET_NULL,related_name='borrowed_user')
    place = models.CharField("場所",max_length=225,choices=STATUS_PRACE)
    is_lost = models.BooleanField("紛失してるか",default=False)
    last_lend = models.DateField("最後に貸出(返却)した日", null=True)
    create_at = models.DateField("入荷日",auto_now_add=True, null=True)
    update_at = models.DateField("最後に貸出(返却)した日",auto_now=True, null=True)

    def __str__(self):
        return self.umbrella_name

    class Meta:
        verbose_name = "傘"
        verbose_name_plural = "傘の情報"

class UmbrellaLog(models.Model):
    umbrella_log = models.JSONField("傘の入荷ログ", default=dict)
    create_at = models.DateField("入荷日",auto_now_add=True, null=True)

    def __str__(self):
        return self.umbrella_log
    
    class Meta:
        verbose_name = "傘入荷ログ"
        verbose_name_plural = "傘の入荷ログ"

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

    prace_name = models.CharField(max_length=225,choices=STATUS_PRACE)
    return_umbrellas = models.ManyToManyField(Umbrellas,related_name='prace_return_umbrellas')
    create_at = models.DateField(auto_now_add=True, null=True)
    update_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return self.prace_name
    
# どの傘が誰にいつ借りられたか（返されたか）を記録するDB
class RentalLog(models.Model):
    create_at = models.DateField("ログ",auto_now=True, null=True)
    user = models.ForeignKey(CustomUser,verbose_name="ユーザー",null=False,on_delete=models.DO_NOTHING,related_name='active_user')
    umbrella = models.ForeignKey(Umbrellas,verbose_name="傘",null=False,on_delete=models.DO_NOTHING,related_name='rentaled_umbrella')
    is_rental = models.BooleanField("貸出または返却",default=False)

    class Meta:
        verbose_name = "履歴"
        verbose_name_plural = "レンタルログ画面"

class LostComments(models.Model):
    reason = models.CharField("失くした理由",max_length=225)
    where_lost = models.CharField("どこで失くした",max_length=225)
    other = models.CharField('その他',max_length=225)
    who_lost = models.ForeignKey(CustomUser,verbose_name="誰が失くしたか",on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "紛失届け"
        verbose_name_plural = "紛失届け"

class Contacts(models.Model):
    username = models.ForeignKey(CustomUser,verbose_name="送信者",on_delete=models.DO_NOTHING)
    email = models.EmailField("メールアドレス",max_length=225)
    message = models.CharField(max_length=225)
    creaste_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = "ご意見"
        verbose_name_plural = "お問い合わせのご意見"