from django import forms
from .models import CustomUser, STATUS_FACULTY, STATUS_GRADE, STATUS_SEX
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

# 学部等の情報を入れさせるとこまで
class CustomForm(forms.ModelForm):
    username = forms.CharField(label='名前',widget=forms.TextInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    email = forms.EmailField(label='メール',widget=forms.TextInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    password = forms.CharField(label='パスワード',widget=forms.PasswordInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    password_confirm = forms.CharField(label='パスワード確認',widget=forms.PasswordInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    faculty = forms.ChoiceField(choices=STATUS_FACULTY, label='学部',widget=forms.Select(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px] px-4'}))
    grade = forms.ChoiceField(choices=STATUS_GRADE, label='学年',widget=forms.Select(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px] px-4'}))
    sex = forms.ChoiceField(choices=STATUS_SEX, label='性別',widget=forms.Select(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px] px-4'}))

    # フォームデータのセット
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'faculty', 'grade', 'sex']

    # パスワードのバリデーション機能(パスワードだけバリデーションを分ける)
    def clean_password(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError('パスワードが確認と違います')

        try:
            validate_password(password)
        except ValidationError as e:
            # エラーがでたらエラーのプロパティに入れる
            self.add_error("password", e.messages)
            raise forms.ValidationError(e.messages)
        return password

    # バリデーション
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        faculty = cleaned_data.get('faculty')
        grade = cleaned_data.get('grade')
        sex = cleaned_data.get('sex')

        # 名前とメール両方を要求
        if not username or not email or not password :
            raise forms.ValidationError("名前とメールアドレスとパスワードは必須です。")

        password = self.clean_password()

        if not faculty or not grade or not sex:
            raise forms.ValidationError('学部、年齢、性別を入力してください')
        return cleaned_data

    # オーバーライドしてsava()関数をログインフォーム用に上書き
    # パスワードをハッシュ化する処理を追加
    def save(self, commit=True):
        user = super().save(commit=False)

        # パスワードをハッシュ化
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            
            user.save()

        return user

# ログインフォームのフォーム作成
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='名前',widget=forms.TextInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    password = forms.CharField(label='パスワード',widget=forms.PasswordInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        # 名前とメール両方を要求
        if not username or not password :
            raise forms.ValidationError("名前とパスワードは必須です。")
        
        try:
            validate_password(password)
        except ValidationError as e:
            # エラーがでたらエラーのプロパティに入れる
            self.add_error("password", e.messages)
            raise forms.ValidationError(e.messages)
        return cleaned_data

# 傘の入荷フォーム(管理画面)
class UmbrellaCreationForm(forms.Form):
    new_umbrellas = forms.IntegerField(label="作成する傘の数", min_value=1, required=True,widget=forms.NumberInput(attrs={'class': 'border border-[#808080] rounded-full px-2 bg-white w-full h-[50px]'}))
    place = forms.ChoiceField(label="傘の場所", choices=[
        ('Library', '図書館'),
        ('North cafeteria', '北食堂'),
        ('Central cafeteria', '中央食堂'),
        ('Engineering faculty', '工学部棟'),
        ('Agriculture faculty', '農学部棟'),
        ('Sience faculty', '理系複合棟'),
        ('Literal faculty', '文系複合棟'),
        ('Senbaru domitory', '千原寮共用棟'),
    ], required=True)
