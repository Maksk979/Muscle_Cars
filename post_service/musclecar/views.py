from django.shortcuts import render, redirect
import requests
from django.conf import settings


def index(request):
    return render(request, 'musclecar/index.html')


def gallery(request):
    return render(request, 'musclecar/gallery.html')


def history(request):
    return render(request, 'musclecar/history.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        resp = requests.post('http://user_service:5001/register', json={
            'username': username,
            'email': email,
            'password1': password1,
            'password2': password2
        })
        if resp.status_code == 201:
            return redirect('login')
        else:
            error = resp.json().get('error', 'Ошибка регистрации')
            return render(request, 'musclecar/register.html', {'error': error})
    return render(request, 'musclecar/register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        resp = requests.post('http://user_service:5001/login', json={
            'username': username,
            'password': password
        })
        if resp.status_code == 200:
            request.session['username'] = username
            return redirect('profile')
        else:
            error = resp.json().get('error', 'Ошибка входа')
            return render(request, 'musclecar/login.html', {'error': error})
    return render(request, 'musclecar/login.html')


def profile(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    resp = requests.get(f'http://user_service:5001/profile/{username}')
    if resp.status_code == 200:
        user = resp.json()
        return render(request, 'musclecar/profile.html', {'user': user})
    else:
        return redirect('login')


def logout_view(request):
    request.session.flush()
    return redirect('login')
