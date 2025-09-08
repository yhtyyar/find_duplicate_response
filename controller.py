"""Основной контроллер для приложения поиска дубликатов."""

import argparse
import logging
import sys
import os

import model
import view

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к файлу по умолчанию - используем относительный путь для переносимости
DEFAULT_CSV_FILE_PATH = os.path.join("res", "requests_08_26_06.06.2025.csv")


def main(file_path: str = None) -> None:
    """
    Основная функция приложения.
    
    Аргументы:
        file_path: Путь к CSV файлу для обработки
    """
    # Используем путь по умолчанию, если не указан другой
    if file_path is None:
        file_path = DEFAULT_CSV_FILE_PATH
    
    try:
        rows = model.read_csv(file_path)
        
        # Проверка на пустые данные
        if not rows:
            print("Ошибка: Файл пуст")
            return

        total = len(rows)
        duplicates_info = model.find_duplicates(rows)
        stats = model.get_stats(rows)
        duplicates_count = sum(v - 1 for v in duplicates_info.values())

        # Группировка дублирующихся строк
        duplicates_full = {}
        for row in rows:
            # Используем ту же функцию создания ключа, что и в модели, для правильной группировки
            key = model._create_comparison_key(row)
            if key in duplicates_info:
                if key not in duplicates_full:
                    duplicates_full[key] = []
                duplicates_full[key].append(row)

        view.print_results(total, duplicates_count, duplicates_full, stats)

    except ValueError as e:
        print(f"Ошибка данных: {str(e)}")
        logger.error(f"Ошибка данных: {str(e)}")
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        logger.error(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")


if __name__ == "__main__":
    # Разбор аргументов командной строки
    parser = argparse.ArgumentParser(description="Поиск дублирующихся записей в CSV файлах логов")
    parser.add_argument(
        "file_path", 
        nargs="?", 
        default=DEFAULT_CSV_FILE_PATH,
        help="Путь к CSV файлу для обработки"
    )
    
    args = parser.parse_args()
    main(args.file_path)