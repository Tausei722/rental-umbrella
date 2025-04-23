from django import forms
from .models import CustomUser, STATUS_FACULTY, STATUS_GRADE, STATUS_SEX
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# 学部等の情報を入れさせるとこまで
class CustomForm(forms.ModelForm):
    name = forms.CharField(label='名前',widget=forms.TextInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    email = forms.EmailField(label='メール',widget=forms.TextInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    password = forms.CharField(label='パスワード',widget=forms.TextInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    faculty = forms.ChoiceField(choices=STATUS_FACULTY, label='学部',widget=forms.Select(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px] px-4'}))
    grade = forms.ChoiceField(choices=STATUS_GRADE, label='学年',widget=forms.Select(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px] px-4'}))
    sex = forms.ChoiceField(choices=STATUS_SEX, label='性別',widget=forms.Select(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px] px-4'}))

    # パスワードのバリデーション機能(パスワードだけバリデーションを分ける)
    def clean_password(self, password):
        try:
            validate_password(password)
            return password
        except ValidationError as e:
            
            raise forms.ValidationError(e.message)

    # バリデーション
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # 名前とメール両方を要求
        if not name or not email:
            raise forms.ValidationError("名前とメールアドレスとパスワードは必須です。")
        
        # パスワードのバリデーション
        password = self.clean_password(password)

        return cleaned_data
    
    # オーバーライドしてsava()関数をログインフォーム用に上書き
    # パスワードをハッシュ化する処理を追加
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password', 'faculty', 'grade', 'sex']