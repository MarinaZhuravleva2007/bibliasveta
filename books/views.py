from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q, Sum, Avg
from datetime import date, timedelta
import random
from .models import CustomUser, Book, Author, Publisher, Genre, AgeCategory, BookCopy, Loan, Fine, Review, Favorite, \
    WantToRead
from .forms import UserRegistrationForm, UserProfileForm, ReviewForm

# Словарь ссылок на книги (Google Drive)
BOOK_LINKS = {
    'Анна Каренина': 'https://drive.google.com/file/d/1BWxCa3IuebC3aWgAFcz7jUNNV-hGLZOv/view?usp=drive_link',
    'Вишневый сад': 'https://drive.google.com/file/d/1QYRGX-INAlQBQ6VAWfukKIiOnfABDk9t/view?usp=drive_link',
    'Война и мир': 'https://drive.google.com/file/d/1si2PnUvq2Sdk1oRTh-ggrt368jK5B-JR/view?usp=drive_link',
    'Евгений Онегин': 'https://drive.google.com/file/d/1cmXIXh8q2Zi54Hu1ifJwqS9zPx0A77dB/view?usp=drive_link',
    'Капитанская дочка': 'https://drive.google.com/file/d/1zD-MqCTk2_1UGxBDLpynwQjec3shB7GS/view?usp=drive_link',
}


def get_book_url(book_title):
    return BOOK_LINKS.get(book_title, None)


def index(request):
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    total_publishers = Publisher.objects.count()
    available_books = Book.objects.filter(status='available').count()

    if request.user.is_authenticated and request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        recent_books = Book.objects.filter(
            status='available',
            age_category__min_age__lte=user_age
        ).order_by('-created_at')[:6]
    else:
        recent_books = Book.objects.filter(status='available').order_by('-created_at')[:6]

    # Случайная книга дня
    random_book = None
    if Book.objects.exists():
        random_book = random.choice(Book.objects.all())

    age_categories = AgeCategory.objects.all()

    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_publishers': total_publishers,
        'available_books': available_books,
        'recent_books': recent_books,
        'age_categories': age_categories,
        'random_book': random_book,
    }
    return render(request, 'books/index.html', context)


def book_list(request):
    books = Book.objects.all()

    if request.user.is_authenticated and request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        books = books.filter(age_category__min_age__lte=user_age)

    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__last_name__icontains=query) |
            Q(authors__first_name__icontains=query)
        ).distinct()

    genre_id = request.GET.get('genre')
    if genre_id:
        books = books.filter(genre_id=genre_id)

    age_id = request.GET.get('age')
    if age_id:
        books = books.filter(age_category_id=age_id)

    genres = Genre.objects.all()
    age_categories = AgeCategory.objects.all()

    context = {
        'books': books,
        'genres': genres,
        'age_categories': age_categories,
        'query': query,
    }
    return render(request, 'books/book_list.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.user.is_authenticated and request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        if book.age_category and user_age < book.age_category.min_age:
            messages.error(request, 'Эта книга недоступна для вашего возраста')
            return redirect('books:book_list')

    book_url = get_book_url(book.title)

    # Проверяем, в избранном ли книга
    is_favorite = False
    is_want_to_read = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, book=book).exists()
        is_want_to_read = WantToRead.objects.filter(user=request.user, book=book).exists()

    context = {
        'book': book,
        'book_url': book_url,
        'is_favorite': is_favorite,
        'is_want_to_read': is_want_to_read,
    }
    return render(request, 'books/book_detail.html', context)


@login_required
def read_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        if book.age_category and user_age < book.age_category.min_age:
            messages.error(request, 'Эта книга недоступна для вашего возраста')
            return redirect('books:book_list')

    book_url = get_book_url(book.title)

    if book_url:
        return redirect(book_url)
    else:
        messages.error(request, f'Ссылка на книгу "{book.title}" не найдена')
        return redirect('books:book_detail', pk=pk)


@login_required
def add_review(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            book.update_rating()
            messages.success(request, 'Ваш отзыв сохранен!')
            return redirect('books:book_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'books/add_review.html', {'form': form, 'book': book})


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    book = review.book

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            book.update_rating()
            messages.success(request, 'Ваш отзыв обновлен!')
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'books/edit_review.html', {'form': form, 'review': review, 'book': book})


@login_required
def reply_review(request, review_id):
    parent_review = get_object_or_404(Review, pk=review_id)
    book = parent_review.book

    if request.method == 'POST':
        comment = request.POST.get('comment')
        if comment:
            Review.objects.create(
                book=book,
                user=request.user,
                parent=parent_review,
                comment=comment,
                rating=None
            )
            messages.success(request, 'Ваш ответ добавлен!')
        else:
            messages.error(request, 'Введите текст ответа')
        return redirect('books:book_detail', pk=book.pk)

    return render(request, 'books/reply_review.html', {'parent_review': parent_review, 'book': book})


@login_required
def my_reviews(request):
    """Мои отзывы в личном кабинете"""
    if request.user.is_staff:
        return redirect('books:admin_dashboard')

    reviews = Review.objects.filter(user=request.user).select_related('book').order_by('-created_at')
    total_reviews = reviews.count()
    avg_rating = reviews.exclude(rating__isnull=True).aggregate(avg=Avg('rating'))['avg'] or 0

    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'books/my_reviews.html', context)


@login_required
def add_to_favorites(request, pk):
    """Добавить книгу в избранное"""
    book = get_object_or_404(Book, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
    if created:
        messages.success(request, f'Книга "{book.title}" добавлена в избранное')
    else:
        messages.info(request, f'Книга "{book.title}" уже в избранном')
    return redirect('books:book_detail', pk=pk)


@login_required
def remove_from_favorites(request, pk):
    """Удалить книгу из избранного"""
    book = get_object_or_404(Book, pk=pk)
    Favorite.objects.filter(user=request.user, book=book).delete()
    messages.success(request, f'Книга "{book.title}" удалена из избранного')
    return redirect('books:book_detail', pk=pk)


@login_required
def my_favorites(request):
    """Мои избранные книги"""
    if request.user.is_staff:
        return redirect('books:admin_dashboard')

    favorites = Favorite.objects.filter(user=request.user).select_related('book')

    context = {
        'items': favorites,
        'title': 'Избранное',
        'empty_message': 'У вас пока нет избранных книг. Добавляйте книги, которые вам понравились!',
        'remove_url_name': 'books:remove_from_favorites'
    }
    return render(request, 'books/my_favorites.html', context)


@login_required
def add_to_want_to_read(request, pk):
    """Добавить книгу в хочу прочитать"""
    book = get_object_or_404(Book, pk=pk)
    want, created = WantToRead.objects.get_or_create(user=request.user, book=book)
    if created:
        messages.success(request, f'Книга "{book.title}" добавлена в список "Хочу прочитать"')
    else:
        messages.info(request, f'Книга "{book.title}" уже в списке "Хочу прочитать"')
    return redirect('books:book_detail', pk=pk)


@login_required
def remove_from_want_to_read(request, pk):
    """Удалить книгу из хочу прочитать"""
    book = get_object_or_404(Book, pk=pk)
    WantToRead.objects.filter(user=request.user, book=book).delete()
    messages.success(request, f'Книга "{book.title}" удалена из списка "Хочу прочитать"')
    return redirect('books:book_detail', pk=pk)


@login_required
def my_want_to_read(request):
    """Мои книги - хочу прочитать"""
    if request.user.is_staff:
        return redirect('books:admin_dashboard')

    want_to_read = WantToRead.objects.filter(user=request.user).select_related('book')

    context = {
        'items': want_to_read,
        'title': 'Хочу прочитать',
        'empty_message': 'У вас пока нет книг в списке "Хочу прочитать". Добавляйте книги, которые хотите прочитать!',
        'remove_url_name': 'books:remove_from_want_to_read'
    }
    return render(request, 'books/my_favorites.html', context)


@login_required
def reserve_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    unpaid_fines = Fine.objects.filter(user=request.user, status='unpaid')
    if unpaid_fines.exists():
        total_fine = unpaid_fines.aggregate(total=Sum('amount'))['total']
        messages.error(request, f'У вас есть неоплаченные штрафы: {total_fine} руб.')
        return redirect('books:profile')

    if request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        if book.age_category and user_age < book.age_category.min_age:
            messages.error(request, 'Эта книга недоступна для вашего возраста')
            return redirect('books:book_detail', pk=pk)

    if book.quantity_available <= 0:
        messages.error(request, 'Нет доступных экземпляров')
        return redirect('books:book_detail', pk=pk)

    if request.user.role == 'schoolchild':
        active_loans = Loan.objects.filter(user=request.user, is_returned=False).count()
        if active_loans >= 3:
            messages.error(request, 'Школьник может взять не более 3 книг')
            return redirect('books:book_list')

    book_copy = BookCopy.objects.filter(book=book, status='available').first()

    if not book_copy:
        count = BookCopy.objects.filter(book=book).count()
        inventory_number = f"INV-{book.id:04d}-{count + 1:03d}"
        book_copy = BookCopy.objects.create(
            book=book,
            inventory_number=inventory_number,
            status='available',
            location='Основное хранилище'
        )

    loan = Loan.objects.create(
        book_copy=book_copy,
        user=request.user,
        issued_by=request.user if request.user.is_staff else None,
        due_date=date.today() + timedelta(days=14),
        is_returned=False
    )

    book_copy.status = 'borrowed'
    book_copy.save()

    book.quantity_available -= 1
    if book.quantity_available == 0:
        book.status = 'borrowed'
    book.save()

    messages.success(request, f'Книга "{book.title}" выдана! Вернуть до {loan.due_date.strftime("%d.%m.%Y")}')
    return redirect('books:profile')


@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id, is_returned=False)

    if not request.user.is_staff and loan.user != request.user:
        messages.error(request, 'Вы можете вернуть только свои книги')
        return redirect('books:profile')

    book = loan.book_copy.book

    loan.return_date = date.today()
    loan.is_returned = True
    loan.save()

    book_copy = loan.book_copy
    book_copy.status = 'available'
    book_copy.save()

    book.quantity_available += 1
    if book.quantity_available > 0:
        book.status = 'available'
    book.save()

    overdue_days = 0
    if loan.return_date > loan.due_date:
        overdue_days = (loan.return_date - loan.due_date).days

    if overdue_days > 0:
        amount = overdue_days * 10
        Fine.objects.create(
            loan=loan,
            user=loan.user,
            amount=amount,
            days_overdue=overdue_days,
            status='unpaid'
        )
        messages.warning(request, f'Просрочка {overdue_days} дней. Штраф: {amount} руб.')
    else:
        messages.success(request, f'Книга "{book.title}" возвращена')

    return redirect('books:profile')


@login_required
def pay_fine(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id, user=request.user, status='unpaid')
    fine.status = 'paid'
    fine.paid_at = date.today()
    fine.save()
    messages.success(request, f'Штраф {fine.amount} руб. оплачен')
    return redirect('books:profile')


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('books:index')

    total_books = Book.objects.count()
    total_users = CustomUser.objects.count()
    active_loans = Loan.objects.filter(is_returned=False).count()
    overdue_loans = Loan.objects.filter(is_returned=False, due_date__lt=date.today()).count()
    total_fines_unpaid = Fine.objects.filter(status='unpaid').aggregate(total=Sum('amount'))['total'] or 0

    recent_loans = Loan.objects.all().select_related('user', 'book_copy__book').order_by('-issue_date')[:10]

    all_users = CustomUser.objects.filter(is_staff=False)
    users_with_debt = []
    for user in all_users:
        unpaid = Fine.objects.filter(user=user, status='unpaid').aggregate(total=Sum('amount'))['total'] or 0
        active = Loan.objects.filter(user=user, is_returned=False).count()
        users_with_debt.append({
            'user': user,
            'debt': unpaid,
            'active_loans': active
        })

    context = {
        'total_books': total_books,
        'total_users': total_users,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'total_fines_unpaid': total_fines_unpaid,
        'recent_loans': recent_loans,
        'users_with_debt': users_with_debt,
    }
    return render(request, 'books/admin_dashboard.html', context)


@login_required
def admin_all_loans(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('books:index')

    loans = Loan.objects.all().select_related('user', 'book_copy__book').order_by('-issue_date')
    context = {'loans': loans}
    return render(request, 'books/admin_loans.html', context)


@login_required
def admin_all_fines(request):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('books:index')

    fines = Fine.objects.all().select_related('user', 'loan__book_copy__book').order_by('-created_at')
    context = {'fines': fines}
    return render(request, 'books/admin_fines.html', context)


def author_list(request):
    authors = Author.objects.all()
    letter = request.GET.get('letter')
    if letter:
        authors = authors.filter(last_name__istartswith=letter)

    letters = Author.objects.values_list('last_name', flat=True)
    letters = sorted(set([l[0].upper() for l in letters if l]))

    context = {
        'authors': authors,
        'letters': letters,
        'current_letter': letter,
    }
    return render(request, 'books/author_list.html', context)


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = author.books.all()

    if request.user.is_authenticated and request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        books = books.filter(age_category__min_age__lte=user_age)

    context = {'author': author, 'books': books}
    return render(request, 'books/author_detail.html', context)


def publisher_list(request):
    publishers = Publisher.objects.all()
    context = {'publishers': publishers}
    return render(request, 'books/publisher_list.html', context)


def publisher_detail(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    books = publisher.books.all()

    if request.user.is_authenticated and request.user.role == 'schoolchild' and request.user.birth_date:
        user_age = date.today().year - request.user.birth_date.year
        books = books.filter(age_category__min_age__lte=user_age)

    context = {'publisher': publisher, 'books': books}
    return render(request, 'books/publisher_detail.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False

            last_card = CustomUser.objects.filter(library_card_number__isnull=False).order_by(
                '-library_card_number').first()
            if last_card and last_card.library_card_number:
                try:
                    last_num = int(last_card.library_card_number.replace('LIB', ''))
                    user.library_card_number = f"LIB{last_num + 1:06d}"
                except:
                    user.library_card_number = "LIB000001"
            else:
                user.library_card_number = "LIB000001"

            user.save()
            messages.success(request, 'Регистрация успешна!')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'books/register.html', {'form': form})


@login_required
def profile(request):
    if request.user.is_staff:
        return redirect('books:admin_dashboard')

    current_loans = Loan.objects.filter(user=request.user, is_returned=False).select_related('book_copy__book')
    loan_history = Loan.objects.filter(user=request.user, is_returned=True).select_related('book_copy__book').order_by(
        '-return_date')[:10]
    unpaid_fines = Fine.objects.filter(user=request.user, status='unpaid')
    total_unpaid = unpaid_fines.aggregate(total=Sum('amount'))['total'] or 0

    # Статистика избранного и хочу прочитать
    favorites_count = Favorite.objects.filter(user=request.user).count()
    want_to_read_count = WantToRead.objects.filter(user=request.user).count()

    for loan in current_loans:
        loan.overdue = loan.is_overdue()
        loan.overdue_days = loan.get_overdue_days()

    context = {
        'current_loans': current_loans,
        'loan_history': loan_history,
        'unpaid_fines': unpaid_fines,
        'total_unpaid': total_unpaid,
        'favorites_count': favorites_count,
        'want_to_read_count': want_to_read_count,
    }
    return render(request, 'books/profile.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен')
            return redirect('books:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'books/profile_edit.html', {'form': form})


@login_required
def admin_assign_fine(request, loan_id):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('books:index')

    loan = get_object_or_404(Loan, pk=loan_id, is_returned=False)

    existing_fine = Fine.objects.filter(loan=loan).first()

    if request.method == 'POST':
        days = int(request.POST.get('days', 0))
        amount = days * 10

        if existing_fine:
            existing_fine.days_overdue = days
            existing_fine.amount = amount
            existing_fine.status = 'unpaid'
            existing_fine.save()
            messages.success(request, f'Штраф обновлен: {amount} руб.')
        else:
            Fine.objects.create(
                loan=loan,
                user=loan.user,
                amount=amount,
                days_overdue=days,
                status='unpaid'
            )
            messages.success(request, f'Штраф {amount} руб. назначен')
        return redirect('books:admin_all_loans')


    overdue_days = loan.get_overdue_days()
    current_amount = overdue_days * 10 if overdue_days > 0 else 0

    context = {
        'loan': loan,
        'existing_fine': existing_fine,
        'overdue_days': overdue_days,
        'current_amount': current_amount,
    }
    return render(request, 'books/admin_assign_fine.html', context)


@login_required
def admin_cancel_fine(request, fine_id):
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('books:index')

    fine = get_object_or_404(Fine, pk=fine_id)
    fine.status = 'cancelled'
    fine.save()
    messages.success(request, f'Штраф {fine.amount} руб. отменен')
    return redirect('books:admin_all_fines')

def custom_logout(request):
    logout(request)
    return redirect('/')