from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Genre, Book
from datetime import datetime
from django.utils.translation import gettext as _
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages


def greeting(request):
    return render(request, 'main/greeting.html')


@user_passes_test(lambda u: u.is_superuser)
def create_genres(request):
    if request.method == 'POST':
        genre_name = request.POST.get('genreName')
        new_genre = Genre(name=genre_name)
        new_genre.save()
        return redirect('createGenres')
    genres = Genre.objects.all()
    return render(request, 'main/createGenres.html', {'genres': genres})


@user_passes_test(lambda u: u.is_superuser)
def edit_genre(request, genre_id):
    genre = Genre.objects.get(id=genre_id)
    books = Book.objects.filter(genre=genre)
    context = {'books': books, 'genre': genre}
    return render(request, 'main/editGenre.html', context)


@user_passes_test(lambda u: u.is_superuser)
def delete_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    if request.method == 'POST':
        genre.delete()
        return redirect('createGenres')
    return redirect('createGenres')


@user_passes_test(lambda u: u.is_superuser)
def update_genre_name(request):
    if request.method == 'POST':
        genre_id = request.POST.get('genreId')
        updated_name = request.POST.get('updatedName')
        genre = get_object_or_404(Genre, id=genre_id)
        genre.name = updated_name
        genre.save()
        return redirect('createGenres')


class SaveBookView(View):
    def post(self, request, genre_id):
        title = request.POST.get('bookTitle')
        author = request.POST.get('bookAuthor')
        publication_date_str = request.POST.get('publicationDate')

        try:
            publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD.")

        genre = get_object_or_404(Genre, id=genre_id)
        book = Book(
            title=title,
            author=author,
            publication_date=publication_date,
            genre=genre
        )
        book.save()
        return redirect('edit_genre', genre_id=genre_id)


class DeleteBookView(View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        genre_id = book.genre.id
        book.delete()
        return redirect('edit_genre', genre_id=genre_id)


class UpdateBookView(View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        title = request.POST.get('bookTitleUpdate')
        author = request.POST.get('bookAuthorUpdate')
        publication_date_str = request.POST.get('publicationDateUpdate')

        try:
            publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseBadRequest("Invalid date format. Use YYYY-MM-DD.")

        book.title = title
        book.author = author
        book.publication_date = publication_date
        book.save()
        return redirect('edit_genre', genre_id=book.genre.id)


def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if User.objects.filter(username=uname).exists():
            messages.warning(request, _("Username already exists! Please choose a different one."))
        elif User.objects.filter(email=email).exists():
            messages.warning(request, _("Email already exists! Please use a different one."))
        elif pass1 != pass2:
            messages.warning(request, _("Your password and confirm password are not the same!!"))
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            user = authenticate(request, username=uname, password=pass1)
            login(request, user)
            return redirect('/')

    return render(request, 'main/signup.html')


def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.warning(request, _("Username or Password is incorrect!!!"))
    return render(request, 'main/login.html')


@login_required(login_url='login')
def LogoutPage(request):
    logout(request)
    return redirect('login')


@user_passes_test(lambda u: u.is_superuser)
def edit_users(request):
    users = User.objects.annotate()
    return render(request, 'main/editUsers.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.delete()
        messages.success(request, f"{user.username} deleted successfully")
        return redirect('editUsers')


@login_required(login_url='login')
def edit_account(request):
    return render(request, 'main/editAccount.html')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current-password')
        if user.check_password(current_password):
            new_password = request.POST.get('new-password')
            if current_password == new_password:
                messages.warning(request, _("Your new password is the same as your current password."))
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, _("Your password has been successfully updated!"))
        else:
            messages.warning(request, _("Current password is incorrect!"))

    return redirect('editAccount')


@login_required(login_url='login')
def change_username(request):
    if request.method == 'POST':
        current_username = request.user.username
        new_username = request.POST.get('new-username')
        if current_username == new_username:
            messages.warning(request, _("Your new username is similar to your current!"))
        elif User.objects.filter(username=new_username).exists():
            messages.warning(request, _("Username already exists! Please choose a different one."))
        else:
            user = request.user
            user.username = new_username
            user.save()
            update_session_auth_hash(request, user)
            messages.warning(request, f"Success! Your changed your username on {new_username}")
        return redirect('editAccount')


@login_required(login_url='login')
def list(request):
    genres = Genre.objects.prefetch_related('book_set').all()
    context = {
        'genres': genres,
    }
    return render(request, 'main/list.html', context)
