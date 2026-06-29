import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(__file__))

# Запускаем бота
from books.bot import main

if __name__ == "__main__":
    main()