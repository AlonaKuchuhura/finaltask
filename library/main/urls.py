from django.urls import path
from . import views


urlpatterns = [
    path('', views.greeting),
    path('createGenres', views.create_genres, name='createGenres'),
    path('edit_genre/<int:genre_id>/', views.edit_genre, name='edit_genre'),
    path('delete_genre/<int:genre_id>/', views.delete_genre, name='delete_genre'),
    path('update_genre_name/', views.update_genre_name, name='update_genre_name'),
    path('save_book/<int:genre_id>/', views.SaveBookView.as_view(), name='save_book'),
    path('delete_book/<int:book_id>/', views.DeleteBookView.as_view(), name='delete_book'),
    path('update_book/<int:book_id>/', views.UpdateBookView.as_view(), name='update_book'),
    path('login', views.LoginPage, name='login'),
    path('signup', views.SignupPage, name='signup'),
    path('logout/', views.LogoutPage, name='logout'),
    path('editUsers/', views.edit_users, name='editUsers'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('editAccount', views.edit_account, name='editAccount'),
    path('change_username', views.change_username, name='change_username'),
    path('change_password', views.change_password, name='change_password'),
    path('list/', views.list, name='list'),
]
