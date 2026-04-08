from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    UserCreationForm을 상속받으면, fields에 명시하지 않아도 password1와 password2 필드는 Django가 내부적으로 자동으로 추가해 준다.
    """

    class Meta:
        model = User
        fields = ("email",)


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="이메일 주소")
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)
