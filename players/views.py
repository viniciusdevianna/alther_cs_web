from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from players.forms import LoginForm, SignupForm
from sheet.models import Character

def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form['username'].value()
            password = form['password'].value()

            user = auth.authenticate(
                request,
                username=username,
                password=password
            )
            if user is not None:
                auth.login(request, user)
                messages.success(request, f'{username} logado com sucesso')
                return redirect('pick_character')
            else:
                messages.error(request, 'Informações erradas de login')
                return redirect('login')

    return render(request, 'players/login.html', {"form": form})

def signup(request):
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            password = form['password'].value()
            player_name = form['player_name'].value()
            username = form['username'].value()
            user_mail = form['user_mail'].value()

            if User.objects.filter(username=username).exists():
                messages.error(request, "Usuário já existe!")
                return redirect('signup')

            user = User.objects.create_user(
                username=username,
                email=user_mail,
                password=password
            )
            user.save()
            messages.success(request, f"{username} registrado com sucesso")
            return redirect('login')

    return render(request, 'players/signup.html', {"form": form})

@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, f"Logout realizado com sucesso")
    return redirect('home')

@login_required
def pick_character(request):        
    player = request.user
    characters = Character.objects.filter(player_ID=player)

    return render(request, 'players/char.html', {'characters': characters})