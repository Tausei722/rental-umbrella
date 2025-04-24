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
    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            print(password,"dsfgdhtyfjgj")
            validate_password(password)
        except ValidationError as e:
            self.errors.password = e.messages
            print(self.errors.password,"axscfdgfh")
            raise forms.ValidationError(e.messages)
        return password

    # バリデーション
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        faculty = cleaned_data.get('faculty')
        grade = cleaned_data.get('grade')
        sex = cleaned_data.get('sex')

        # 名前とメール両方を要求
        if not name or not email or not password :
            raise forms.ValidationError("名前とメールアドレスとパスワードは必須です。")

        password = self.clean_password()

        if not faculty or not grade or not sex:
            raise forms.ValidationError('学部、年齢、性別を入力してください')
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