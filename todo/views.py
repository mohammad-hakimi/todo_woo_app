from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from todo.forms import TodoForm
from todo.models import Todo


def home(request):
    return render(request, 'todo/home.html')


def signup_user(request):
    form = UserCreationForm()
    if request.method == 'GET':
        return render(request, 'todo/signup_user.html', {'form': form})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('current')
            except IntegrityError:
                return render(request, 'todo/signup_user.html',
                              {'form': form, 'error': 'This username has already been taken. Choose another one.'})
        else:
            return render(request, 'todo/signup_user.html',
                          {'form': form, 'error': 'Your password does not match with confirmation.'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/login_user.html',
                          {'form': AuthenticationForm(), 'error': 'Either username or password is wrong'})
        else:
            login(request, user)
            return redirect('current')


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def current(request):
    todos = Todo.objects.filter(user=request.user, do_date__isnull=True)
    return render(request, 'todo/current.html', {'todos': todos})


@login_required
def create(request):
    if request.method == 'POST':
        try:
            todo_form = TodoForm(request.POST)
            temp_todo = todo_form.save(commit=False)
            temp_todo.user = request.user
            temp_todo.save()
            return redirect('current')
        except ValueError:
            return render(request, 'todo/create.html', {'form': TodoForm(), 'error': 'Invalid data. Try again.'})

    else:
        return render(request, 'todo/create.html', {'form': TodoForm()})


@login_required
def completed(request):
    todos = Todo.objects.filter(user=request.user, do_date__isnull=False).order_by('-do_date')
    return render(request, 'todo/completed.html', {'todos': todos})


@login_required
def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    form = TodoForm(instance=todo)
    return render(request, 'todo/view_todo.html', {'todo': todo, 'form': form})


@login_required
def update_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        form = TodoForm(request.POST, instance=todo)
        form.save()
        return redirect('current')


@login_required
def complete_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.do_date = timezone.now()
        todo.save()
        return redirect('current')


@login_required
def delete_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.delete()
        return redirect('current')
