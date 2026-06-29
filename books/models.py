from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from datetime import date


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('adult', 'Взрослый читатель'),
        ('schoolchild', 'Школьник'),
    ]

    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='adult')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    library_card_number = models.CharField('Номер читательского билета', max_length=20, unique=True, null=True,
                                           blank=True)

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_role_display()})"

    def is_librarian(self):
        return self.is_staff


class Author(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    death_date = models.DateField('Дата смерти', null=True, blank=True)
    biography = models.TextField('Биография', blank=True)
    photo = models.ImageField('Фото', upload_to='authors/', null=True, blank=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()


class Publisher(models.Model):
    name = models.CharField('Название', max_length=200)
    address = models.TextField('Адрес', blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    email = models.EmailField('Email', blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Издательство'
        verbose_name_plural = 'Издательства'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class AgeCategory(models.Model):
    code = models.CharField('Код', max_length=3, unique=True)
    name = models.CharField('Название', max_length=50)
    min_age = models.IntegerField('Минимальный возраст')
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Возрастная категория'
        verbose_name_plural = 'Возрастные категории'
        ordering = ['min_age']

    def __str__(self):
        return f"{self.code} ({self.name})"


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступна'),
        ('borrowed', 'Выдана'),
        ('reserved', 'Зарезервирована'),
        ('repair', 'На ремонте'),
        ('lost', 'Утеряна'),
    ]

    title = models.CharField('Название', max_length=200)
    authors = models.ManyToManyField(Author, verbose_name='Авторы', related_name='books')
    publisher = models.ForeignKey(Publisher, verbose_name='Издательство', on_delete=models.SET_NULL, null=True,
                                  blank=True, related_name='books')
    genre = models.ForeignKey(Genre, verbose_name='Жанр', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='books')
    age_category = models.ForeignKey(AgeCategory, verbose_name='Возрастная категория', on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='books')
    publication_year = models.IntegerField('Год издания', null=True, blank=True)
    isbn = models.CharField('ISBN', max_length=13, blank=True, null=True)
    pages = models.IntegerField('Количество страниц', null=True, blank=True)
    description = models.TextField('Описание', blank=True)
    cover_image = models.ImageField('Обложка', upload_to='covers/', null=True, blank=True)
    yandex_link = models.URLField('Ссылка на Яндекс.Диск', blank=True, null=True)
    quantity_total = models.IntegerField('Общее количество', default=1)
    quantity_available = models.IntegerField('Доступно', default=1)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    avg_rating = models.FloatField('Средний рейтинг', default=0)
    reviews_count = models.IntegerField('Количество отзывов', default=0)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('books:book_detail', args=[str(self.id)])

    def get_authors_display(self):
        return ", ".join([str(author) for author in self.authors.all()])

    def update_rating(self):
        from django.db.models import Avg
        avg = self.reviews.all().aggregate(Avg('rating'))['rating__avg']
        self.avg_rating = avg if avg else 0
        self.reviews_count = self.reviews.count()
        self.save()


class BookCopy(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступен'),
        ('borrowed', 'Выдан'),
        ('reserved', 'Зарезервирован'),
        ('repair', 'На ремонте'),
        ('lost', 'Утерян'),
    ]

    book = models.ForeignKey(Book, verbose_name='Книга', on_delete=models.CASCADE, related_name='copies')
    inventory_number = models.CharField('Инвентарный номер', max_length=50, unique=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='available')
    purchase_date = models.DateField('Дата поступления', null=True, blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField('Место хранения', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книг'

    def __str__(self):
        return f"{self.book.title} - {self.inventory_number}"


class Loan(models.Model):
    book_copy = models.ForeignKey(BookCopy, verbose_name='Экземпляр книги', on_delete=models.CASCADE,
                                  related_name='loans')
    user = models.ForeignKey(CustomUser, verbose_name='Читатель', on_delete=models.CASCADE, related_name='loans')
    issued_by = models.ForeignKey(CustomUser, verbose_name='Выдал', on_delete=models.SET_NULL, null=True,
                                  related_name='issued_loans')
    issue_date = models.DateTimeField('Дата выдачи', auto_now_add=True)
    due_date = models.DateField('Срок возврата')
    return_date = models.DateField('Дата возврата', null=True, blank=True)
    is_returned = models.BooleanField('Возвращена', default=False)
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Выдача'
        verbose_name_plural = 'Выдачи'
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.book_copy} - {self.user}"

    def is_overdue(self):
        if not self.is_returned and date.today() > self.due_date:
            return True
        return False

    def get_overdue_days(self):
        if not self.is_returned and date.today() > self.due_date:
            return (date.today() - self.due_date).days
        if self.is_returned and self.return_date and self.return_date > self.due_date:
            return (self.return_date - self.due_date).days
        return 0


class Fine(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Не оплачен'),
        ('paid', 'Оплачен'),
    ]

    loan = models.OneToOneField(Loan, verbose_name='Выдача', on_delete=models.CASCADE, related_name='fine')
    user = models.ForeignKey(CustomUser, verbose_name='Читатель', on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField('Сумма штрафа', max_digits=10, decimal_places=2, default=0)
    days_overdue = models.IntegerField('Дней просрочки', default=0)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    paid_at = models.DateTimeField('Дата оплаты', null=True, blank=True)

    class Meta:
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафы'

    def __str__(self):
        return f"Штраф {self.user} - {self.amount} руб."

    def mark_as_paid(self):
        from django.utils import timezone
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()


class Review(models.Model):
    book = models.ForeignKey(Book, verbose_name='Книга', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, verbose_name='Читатель', on_delete=models.CASCADE, related_name='reviews')
    parent = models.ForeignKey('self', verbose_name='Ответ на', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='replies')
    rating = models.IntegerField('Оценка', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], null=True,
                                 blank=True)
    comment = models.TextField('Комментарий', max_length=1000)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        if self.parent:
            return f"Ответ {self.user} на {self.parent.user}"
        return f"{self.user} - {self.book} - {self.rating}★"


class Favorite(models.Model):
    """Избранное (понравившиеся книги)"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user} - {self.book}"


class WantToRead(models.Model):
    """Хочу прочитать (список желаний)"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='want_to_read')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='wanted_by')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Хочу прочитать'
        verbose_name_plural = 'Хочу прочитать'
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user} хочет прочитать {self.book}"