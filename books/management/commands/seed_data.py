from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import AgeCategory, Author, Genre, Publisher, Book
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данных...')

        # 1. Создаем возрастные категории
        self.stdout.write('Создание возрастных категорий...')
        categories = [
            ('0+', 'Для всех возрастов', 0),
            ('6+', 'Для детей старше 6 лет', 6),
            ('12+', 'Для детей старше 12 лет', 12),
            ('16+', 'Для детей старше 16 лет', 16),
            ('18+', 'Только для взрослых', 18),
        ]

        created_categories = []
        for code, name, min_age in categories:
            obj, created = AgeCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'min_age': min_age}
            )
            created_categories.append(obj)
            if created:
                self.stdout.write(f'  ✓ Создана категория: {code} - {name}')
            else:
                self.stdout.write(f'  • Категория уже существует: {code} - {name}')

        # 2. Создаем жанры
        self.stdout.write('\nСоздание жанров...')
        genres_data = [
            'Роман',
            'Поэзия',
            'Детектив',
            'Фантастика',
            'Научная литература',
            'Детская литература',
            'Приключения',
            'Историческая проза',
        ]

        genres = []
        for genre_name in genres_data:
            obj, created = Genre.objects.get_or_create(name=genre_name)
            genres.append(obj)
            if created:
                self.stdout.write(f'  ✓ Создан жанр: {genre_name}')
            else:
                self.stdout.write(f'  • Жанр уже существует: {genre_name}')

        # 3. Создаем издательства
        self.stdout.write('\nСоздание издательств...')
        publishers_data = [
            {'name': 'Эксмо', 'address': 'Москва, ул. Эксмо, д. 1', 'email': 'info@eksmo.ru',
             'phone': '+7 (495) 123-45-67'},
            {'name': 'АСТ', 'address': 'Москва, ул. АСТ, д. 2', 'email': 'info@ast.ru', 'phone': '+7 (495) 234-56-78'},
            {'name': 'Дрофа', 'address': 'Москва, ул. Дрофа, д. 3', 'email': 'info@drofa.ru',
             'phone': '+7 (495) 345-67-89'},
            {'name': 'Просвещение', 'address': 'Москва, ул. Просвещения, д. 4', 'email': 'info@prosv.ru',
             'phone': '+7 (495) 456-78-90'},
        ]

        publishers = []
        for pub_data in publishers_data:
            obj, created = Publisher.objects.get_or_create(
                name=pub_data['name'],
                defaults=pub_data
            )
            publishers.append(obj)
            if created:
                self.stdout.write(f'  ✓ Создано издательство: {pub_data["name"]}')
            else:
                self.stdout.write(f'  • Издательство уже существует: {pub_data["name"]}')

        # 4. Создаем авторов
        self.stdout.write('\nСоздание авторов...')
        authors_data = [
            {'first_name': 'Александр', 'last_name': 'Пушкин', 'middle_name': 'Сергеевич',
             'birth_date': date(1799, 6, 6), 'death_date': date(1837, 2, 10),
             'biography': 'Великий русский поэт, драматург и прозаик.'},
            {'first_name': 'Лев', 'last_name': 'Толстой', 'middle_name': 'Николаевич',
             'birth_date': date(1828, 9, 9), 'death_date': date(1910, 11, 20),
             'biography': 'Один из величайших писателей мира.'},
            {'first_name': 'Фёдор', 'last_name': 'Достоевский', 'middle_name': 'Михайлович',
             'birth_date': date(1821, 11, 11), 'death_date': date(1881, 2, 9),
             'biography': 'Великий русский писатель, мыслитель.'},
            {'first_name': 'Антон', 'last_name': 'Чехов', 'middle_name': 'Павлович',
             'birth_date': date(1860, 1, 29), 'death_date': date(1904, 7, 15),
             'biography': 'Великий русский писатель, драматург.'},
            {'first_name': 'Михаил', 'last_name': 'Булгаков', 'middle_name': 'Афанасьевич',
             'birth_date': date(1891, 5, 15), 'death_date': date(1940, 3, 10),
             'biography': 'Русский писатель советского периода.'},
            {'first_name': 'Николай', 'last_name': 'Гоголь', 'middle_name': 'Васильевич',
             'birth_date': date(1809, 4, 1), 'death_date': date(1852, 3, 4),
             'biography': 'Великий русский прозаик, драматург, поэт.'},
            {'first_name': 'Иван', 'last_name': 'Тургенев', 'middle_name': 'Сергеевич',
             'birth_date': date(1818, 11, 9), 'death_date': date(1883, 9, 3),
             'biography': 'Русский писатель-реалист.'},
        ]

        authors = []
        for author_data in authors_data:
            obj, created = Author.objects.get_or_create(
                last_name=author_data['last_name'],
                first_name=author_data['first_name'],
                defaults=author_data
            )
            authors.append(obj)
            if created:
                self.stdout.write(f'  ✓ Создан автор: {obj.full_name()}')
            else:
                self.stdout.write(f'  • Автор уже существует: {obj.full_name()}')

        # 5. Создаем книги
        self.stdout.write('\nСоздание книг...')

        # Получаем ссылки на объекты
        age_cat_0 = AgeCategory.objects.get(code='0+')
        age_cat_6 = AgeCategory.objects.get(code='6+')
        age_cat_12 = AgeCategory.objects.get(code='12+')
        age_cat_16 = AgeCategory.objects.get(code='16+')
        age_cat_18 = AgeCategory.objects.get(code='18+')

        publisher_eksmo = Publisher.objects.get(name='Эксмо')
        publisher_ast = Publisher.objects.get(name='АСТ')
        publisher_drofa = Publisher.objects.get(name='Дрофа')
        publisher_prosv = Publisher.objects.get(name='Просвещение')

        genre_roman = Genre.objects.get(name='Роман')
        genre_poetry = Genre.objects.get(name='Поэзия')
        genre_detective = Genre.objects.get(name='Детектив')
        genre_fantasy = Genre.objects.get(name='Фантастика')
        genre_science = Genre.objects.get(name='Научная литература')
        genre_children = Genre.objects.get(name='Детская литература')
        genre_adventure = Genre.objects.get(name='Приключения')
        genre_history = Genre.objects.get(name='Историческая проза')

        # Создаем книги
        books_data = [
            {
                'title': 'Война и мир',
                'authors': [authors[1]],  # Толстой
                'publisher': publisher_eksmo,
                'genre': genre_roman,
                'age_category': age_cat_16,
                'publication_year': 1869,
                'pages': 1225,
                'isbn': '978-5-699-12345-6',
                'description': 'Роман-эпопея о событиях наполеоновских войн. История нескольких семей на фоне великих исторических событий.',
                'quantity_total': 5,
                'quantity_available': 5,
            },
            {
                'title': 'Евгений Онегин',
                'authors': [authors[0]],  # Пушкин
                'publisher': publisher_ast,
                'genre': genre_poetry,
                'age_category': age_cat_12,
                'publication_year': 1833,
                'pages': 320,
                'isbn': '978-5-699-23456-7',
                'description': 'Роман в стихах о жизни русского общества XIX века. История разочарованного молодого человека.',
                'quantity_total': 8,
                'quantity_available': 8,
            },
            {
                'title': 'Преступление и наказание',
                'authors': [authors[2]],  # Достоевский
                'publisher': publisher_eksmo,
                'genre': genre_roman,
                'age_category': age_cat_16,
                'publication_year': 1866,
                'pages': 672,
                'isbn': '978-5-699-34567-8',
                'description': 'Роман о моральных дилеммах, преступлении и искуплении. История студента Раскольникова.',
                'quantity_total': 4,
                'quantity_available': 4,
            },
            {
                'title': 'Сказка о рыбаке и рыбке',
                'authors': [authors[0]],  # Пушкин
                'publisher': publisher_ast,
                'genre': genre_children,
                'age_category': age_cat_6,
                'publication_year': 1835,
                'pages': 32,
                'isbn': '978-5-699-45678-9',
                'description': 'Сказка о старике и старухе, о жадности и благодарности.',
                'quantity_total': 10,
                'quantity_available': 10,
            },
            {
                'title': 'Вишневый сад',
                'authors': [authors[3]],  # Чехов
                'publisher': publisher_eksmo,
                'genre': genre_roman,
                'age_category': age_cat_12,
                'publication_year': 1904,
                'pages': 128,
                'isbn': '978-5-699-56789-0',
                'description': 'Комедия в четырех действиях о судьбе дворянского имения.',
                'quantity_total': 6,
                'quantity_available': 6,
            },
            {
                'title': 'Мастер и Маргарита',
                'authors': [authors[4]],  # Булгаков
                'publisher': publisher_ast,
                'genre': genre_fantasy,
                'age_category': age_cat_18,
                'publication_year': 1967,
                'pages': 480,
                'isbn': '978-5-699-67890-1',
                'description': 'Роман о дьяволе, любви и искусстве. Мистическая история в Москве 1930-х годов.',
                'quantity_total': 7,
                'quantity_available': 7,
            },
            {
                'title': 'Анна Каренина',
                'authors': [authors[1]],  # Толстой
                'publisher': publisher_drofa,
                'genre': genre_roman,
                'age_category': age_cat_16,
                'publication_year': 1877,
                'pages': 864,
                'isbn': '978-5-699-78901-2',
                'description': 'Роман о трагической любви замужней женщины к офицеру.',
                'quantity_total': 4,
                'quantity_available': 4,
            },
            {
                'title': 'Мертвые души',
                'authors': [authors[5]],  # Гоголь
                'publisher': publisher_ast,
                'genre': genre_roman,
                'age_category': age_cat_12,
                'publication_year': 1842,
                'pages': 352,
                'isbn': '978-5-699-89012-3',
                'description': 'Поэма о похождениях Чичикова, скупавшего мертвые души.',
                'quantity_total': 6,
                'quantity_available': 6,
            },
            {
                'title': 'Отцы и дети',
                'authors': [authors[6]],  # Тургенев
                'publisher': publisher_drofa,
                'genre': genre_roman,
                'age_category': age_cat_12,
                'publication_year': 1862,
                'pages': 288,
                'isbn': '978-5-699-90123-4',
                'description': 'Роман о конфликте поколений и нигилизме.',
                'quantity_total': 5,
                'quantity_available': 5,
            },
            {
                'title': 'Ревизор',
                'authors': [authors[5]],  # Гоголь
                'publisher': publisher_prosv,
                'genre': genre_roman,
                'age_category': age_cat_12,
                'publication_year': 1836,
                'pages': 112,
                'isbn': '978-5-699-01234-5',
                'description': 'Комедия о чиновниках, принявших проезжего за ревизора.',
                'quantity_total': 7,
                'quantity_available': 7,
            },
            {
                'title': 'Три сестры',
                'authors': [authors[3]],  # Чехов
                'publisher': publisher_eksmo,
                'genre': genre_roman,
                'age_category': age_cat_12,
                'publication_year': 1901,
                'pages': 96,
                'isbn': '978-5-699-12345-7',
                'description': 'Драма о жизни трех сестер в провинциальном городе.',
                'quantity_total': 5,
                'quantity_available': 5,
            },
            {
                'title': 'Капитанская дочка',
                'authors': [authors[0]],  # Пушкин
                'publisher': publisher_ast,
                'genre': genre_history,
                'age_category': age_cat_12,
                'publication_year': 1836,
                'pages': 224,
                'isbn': '978-5-699-23456-8',
                'description': 'Исторический роман о пугачевском восстании.',
                'quantity_total': 8,
                'quantity_available': 8,
            },
        ]

        for book_data in books_data:
            obj, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults={
                    'publisher': book_data['publisher'],
                    'genre': book_data['genre'],
                    'age_category': book_data['age_category'],
                    'publication_year': book_data['publication_year'],
                    'pages': book_data['pages'],
                    'isbn': book_data.get('isbn', ''),
                    'description': book_data['description'],
                    'quantity_total': book_data['quantity_total'],
                    'quantity_available': book_data['quantity_available'],
                    'status': 'available',
                }
            )

            if created:
                obj.authors.set(book_data['authors'])
                self.stdout.write(f'  ✓ Создана книга: {book_data["title"]}')
            else:
                self.stdout.write(f'  • Книга уже существует: {book_data["title"]}')

        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена начальными данными!'))
        self.stdout.write('\nТеперь вы можете:')
        self.stdout.write('  - Зайти в админ-панель: http://127.0.0.1:8000/admin/')
        self.stdout.write('  - Добавлять новые книги, авторов, жанры через админку')
        self.stdout.write('  - Управлять читателями и выдачами')
        self.stdout.write('\nТестовые данные:')
        self.stdout.write(f'  - Книг добавлено: {len(books_data)}')
        self.stdout.write(f'  - Авторов добавлено: {len(authors_data)}')
        self.stdout.write(f'  - Жанров добавлено: {len(genres_data)}')
        self.stdout.write(f'  - Издательств добавлено: {len(publishers_data)}')