from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Author, Publisher, Genre, AgeCategory, Book, BookCopy, Loan, Fine


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'last_name', 'first_name', 'role', 'library_card_number', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'library_card_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'address', 'birth_date', 'library_card_number')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'phone', 'address', 'birth_date', 'library_card_number')
        }),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'birth_date']
    search_fields = ['last_name', 'first_name']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(AgeCategory)
class AgeCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'min_age']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_authors_display', 'publisher', 'status', 'quantity_available']
    list_filter = ['status', 'genre', 'age_category']
    search_fields = ['title', 'isbn']
    filter_horizontal = ['authors']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'authors', 'publisher', 'genre', 'age_category')
        }),
        ('Библиографические данные', {
            'fields': ('publication_year', 'isbn', 'pages', 'description')
        }),
        ('Обложка и ссылка', {
            'fields': ('cover_image', 'yandex_link')
        }),
        ('Учёт', {
            'fields': ('quantity_total', 'quantity_available', 'status')
        }),
    )

    def get_authors_display(self, obj):
        return obj.get_authors_display()

    get_authors_display.short_description = 'Авторы'


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ['book', 'inventory_number', 'status', 'location']
    list_filter = ['status']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['book_copy', 'user', 'issue_date', 'due_date', 'is_returned']
    list_filter = ['is_returned', 'issue_date']
    search_fields = ['user__last_name', 'book_copy__inventory_number']


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'days_overdue', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__last_name']