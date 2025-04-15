from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomForm(forms.Form):
    name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=225)
    password = forms.CharField(max_length=225)

    # パスワードのバリデーション機能
    def validate_user_password(password):
        try:
            validate_password(password)
            print("パスワードが有効です！")
        except ValidationError as e:
            print("エラー:", e.messages)

    # バリデーション
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # 名前とメール両方を要求
        if not name or not email or not password:
            raise forms.ValidationError("名前とメールアドレスは必須です。")
        
        # パスワードのバリデーション
        try:
            self.validate_user_password(password)
        except ValidationError as e:
            raise forms.ValidationError({"password": e.messages})

        return cleaned_data