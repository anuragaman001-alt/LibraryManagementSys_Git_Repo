from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),

    path('books/', views.book_list, name='books'),
    path('issue/<int:book_id>/', views.issue_book, name='issue_book'),
    path('return/<int:issue_id>/', views.return_book, name='return_book'),

    path('add-book/', views.add_book, name='add_book'),
    path('update-book/<int:book_id>/', views.update_book, name='update_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),

    path('delete-member/<int:member_id>/', views.delete_member, name='delete_member'),
]
