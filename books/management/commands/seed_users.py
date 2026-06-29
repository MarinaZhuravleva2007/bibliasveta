from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает тестовых пользователей'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых пользователей...')

        # Создаем взрослого читателя
        adult, created = User.objects.get_or_create(
            username='adult_reader',
            defaults={
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'ivan@example.com',
                'role': 'adult',
                'birth_date': date(1990, 1, 1),
                'phone': '+7 (999) 123-45-67',
                'address': 'г. Москва, ул. Примерная, д. 1',
                'is_staff': False,
            }
        )
        if created:
            adult.set_password('reader123')
            adult.save()
            self.stdout.write(f'  ✓ Создан взрослый читатель: {adult.username}')

        # Создаем школьника 10 лет
        schoolchild, created = User.objects.get_or_create(
            username='schoolchild_10',
            defaults={
                'first_name': 'Мария',
                'last_name': 'Иванова',
                'email': 'masha@example.com',
                'role': 'schoolchild',
                'birth_date': date(2016, 3, 24),
                'phone': '+7 (999) 987-65-43',
                'address': 'г. Москва, ул. Школьная, д. 10',
                'is_staff': False,
            }
        )
        if created:
            schoolchild.set_password('reader123')
            schoolchild.save()
            self.stdout.write(f'  ✓ Создан школьник (10 лет): {schoolchild.username}')

        # Создаем школьника 15 лет
        schoolchild2, created = User.objects.get_or_create(
            username='schoolchild_15',
            defaults={
                'first_name': 'Алексей',
                'last_name': 'Сидоров',
                'email': 'alex@example.com',
                'role': 'schoolchild',
                'birth_date': date(2011, 5, 15),
                'phone': '+7 (999) 111-22-33',
                'address': 'г. Москва, ул. Молодежная, д. 5',
                'is_staff': False,
            }
        )
        if created:
            schoolchild2.set_password('reader123')
            schoolchild2.save()
            self.stdout.write(f'  ✓ Создан школьник (15 лет): {schoolchild2.username}')

        self.stdout.write(self.style.SUCCESS('\n✅ Тестовые пользователи созданы!'))
        self.stdout.write('Пароль для всех: reader123')