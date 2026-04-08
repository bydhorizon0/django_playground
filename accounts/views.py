from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render, redirect

from accounts.forms import CustomUserCreationForm, CustomLoginForm


def home_view(request: HttpRequest):
    return render(request, "home.html")


def signup_view(request: HttpRequest):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "회원가입이 완료되었습니다!")
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request: HttpRequest):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            # DB 조회를 다시 할 필요 없이 이미 검증된 유저 객체를 바로 반환
            user = form.get_user()
            login(request, user)
            messages.info(request, f"{user.get_username()}님, 환영합니다.")
            return redirect("home")
    else:
        form = CustomLoginForm()
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request: HttpRequest):
    logout(request)
    return redirect("login")
