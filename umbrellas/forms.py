from django import forms
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# 学部等の情報を入れさせるとこまで
class CustomForm(forms.ModelForm):
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

    name = forms.CharField(label='名前')
    email = forms.EmailField(label='メール')
    password = forms.CharField(label='パスワード')
    faculty = forms.ChoiceField(choices=STATUS_FACULTY, label='学部')
    grade = forms.ChoiceField(choices=STATUS_GRADE, label='学年')
    sex = forms.ChoiceField(choices=STATUS_SEX, label='性別')

    # パスワードのバリデーション機能
    def validate_user_password(self, password):
        try:
            validate_password(password)
            print("パスワードが有効です！")
        except ValidationError as e:
            print("エラー:", e.messages)
            raise ValidationError(e.messages)

    # バリデーション
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # 名前とメール両方を要求
        if not name or not email or not password:
            raise forms.ValidationError("名前とメールアドレスとパスワードは必須です。")
        
        # パスワードのバリデーション
        self.validate_user_password(password)

        return cleaned_data
    
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password', 'faculty', 'grade', 'sex']