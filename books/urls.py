from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/my-reviews/', views.my_reviews, name='my_reviews'),
    path('profile/favorites/', views.my_favorites, name='my_favorites'),
    path('profile/want-to-read/', views.my_want_to_read, name='my_want_to_read'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/read/', views.read_book, name='read_book'),
    path('books/<int:pk>/reserve/', views.reserve_book, name='reserve_book'),
    path('books/<int:pk>/add-review/', views.add_review, name='add_review'),
    path('books/<int:pk>/favorite/add/', views.add_to_favorites, name='add_to_favorites'),
    path('books/<int:pk>/favorite/remove/', views.remove_from_favorites, name='remove_from_favorites'),
    path('books/<int:pk>/want-to-read/add/', views.add_to_want_to_read, name='add_to_want_to_read'),
    path('books/<int:pk>/want-to-read/remove/', views.remove_from_want_to_read, name='remove_from_want_to_read'),
    path('reviews/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:review_id>/reply/', views.reply_review, name='reply_review'),
    path('loans/<int:loan_id>/return/', views.return_book, name='return_book'),
    path('fines/<int:fine_id>/pay/', views.pay_fine, name='pay_fine'),
    path('librarian/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('librarian/loans/', views.admin_all_loans, name='admin_all_loans'),
    path('librarian/fines/', views.admin_all_fines, name='admin_all_fines'),
    path('librarian/loans/<int:loan_id>/assign-fine/', views.admin_assign_fine, name='admin_assign_fine'),
    path('librarian/fines/<int:fine_id>/cancel/', views.admin_cancel_fine, name='admin_cancel_fine'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/<int:pk>/', views.publisher_detail, name='publisher_detail'),
]