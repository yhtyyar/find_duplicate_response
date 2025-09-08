"""Модель данных для обработки CSV файлов и поиска дубликатов."""

import csv
import urllib.parse
from typing import List, Dict, Any, TextIO, Tuple


def read_csv(file_path: str, skip_header: bool = True) -> List[Dict[str, Any]]:
    """
    Чтение CSV файла и возврат списка строк в виде словарей.
    
    Аргументы:
        file_path: Путь к CSV файлу
        skip_header: Пропустить ли строку заголовка
        
    Возвращает:
        Список словарей строк
        
    Выбрасывает:
        ValueError: Если чтение файла не удалось или отсутствуют обязательные поля
    """
    required_fields = ['URL', 'Method', 'Response Code', 'Status']
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            return _read_csv_file(file, skip_header, required_fields)
    except FileNotFoundError:
        raise ValueError(f"Файл не найден: {file_path}")
    except Exception as e:
        raise ValueError(f"Ошибка чтения файла: {str(e)}")


def read_csv_from_string(file_buffer: TextIO, skip_header: bool = True) -> List[Dict[str, Any]]:
    """
    Чтение CSV данных из строкового буфера и возврат списка строк в виде словарей.
    
    Аргументы:
        file_buffer: Строковый буфер с CSV данными
        skip_header: Пропустить ли строку заголовка
        
    Возвращает:
        Список словарей строк
        
    Выбрасывает:
        ValueError: Если чтение файла не удалось или отсутствуют обязательные поля
    """
    required_fields = ['URL', 'Method', 'Response Code', 'Status']
    return _read_csv_file(file_buffer, skip_header, required_fields)


def _read_csv_file(file_obj: TextIO, skip_header: bool, required_fields: List[str]) -> List[Dict[str, Any]]:
    """
    Внутренняя функция для чтения CSV из объекта файла.
    
    Аргументы:
        file_obj: Объект файла для чтения
        skip_header: Пропустить ли строку заголовка
        required_fields: Список обязательных полей
        
    Возвращает:
        Список словарей строк
    """
    csv_reader = csv.DictReader(file_obj)
    
    # Пропустить заголовок, если требуется
    if skip_header:
        try:
            next(csv_reader)
        except StopIteration:
            return []  # Пустой файл

    rows = []
    for idx, row in enumerate(csv_reader, 1):
        if not row:
            continue
            
        # Проверка наличия обязательных полей
        if not all(field in row for field in required_fields):
            raise ValueError(f"Строка {idx}: Отсутствуют обязательные поля")
            
        rows.append(row)
        
    return rows


def _normalize_url_for_comparison(url: str) -> str:
    """
    Нормализация URL для сравнения, включая упорядочение query-параметров.
    
    Аргументы:
        url: URL для нормализации
        
    Возвращает:
        Нормализованный URL с упорядоченными query-параметрами
    """
    try:
        # Разбираем URL на компоненты
        parsed = urllib.parse.urlparse(url)
        
        # Если есть query-параметры, сортируем их для консистентного сравнения
        if parsed.query:
            # Парсим query-параметры
            query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            # Сортируем параметры по ключу
            sorted_params = sorted(query_params.items())
            # Формируем отсортированную query-строку
            normalized_query = urllib.parse.urlencode(sorted_params, doseq=True)
            # Собираем нормализованный URL
            normalized_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                normalized_query,
                parsed.fragment
            ))
            return normalized_url
        else:
            # Если нет query-параметров, возвращаем оригинальный URL
            return url
    except Exception:
        # В случае ошибки возвращаем оригинальный URL
        return url


def _create_comparison_key(row: Dict[str, Any]) -> str:
    """
    Создание ключа для сравнения записей.
    
    Аргументы:
        row: Словарь с данными строки
        
    Возвращает:
        Ключ для сравнения записей
    """
    # Нормализуем URL для точного сравнения с учетом query-параметров
    normalized_url = _normalize_url_for_comparison(row['URL'])
    
    # Создаем ключ из всех критических полей
    key_parts = [
        normalized_url,
        str(row['Method']),
        str(row['Response Code']),
        str(row['Status'])
    ]
    
    return '-'.join(key_parts)


def find_duplicates(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Поиск дублирующихся записей на основе URL, метода, кода ответа и статуса.
    При сравнении URL учитываются query-параметры с нормализацией.
    
    Аргументы:
        rows: Список словарей строк
        
    Возвращает:
        Словарь с ключами дубликатов и их количеством
    """
    count = {}
    
    for row in rows:
        # Создаем нормализованный ключ для сравнения
        key = _create_comparison_key(row)
        count[key] = count.get(key, 0) + 1
        
    return {k: v for k, v in count.items() if v > 1}


def get_stats(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Получение статистики по кодам ответов и методам.
    
    Аргументы:
        rows: Список словарей строк
        
    Возвращает:
        Словарь с количеством кодов и методов
    """
    code_counts = {}
    method_counts = {}
    
    for row in rows:
        code = row.get('Response Code', 'Нет кода')
        method = row.get('Method', 'Нет метода')
        
        code_counts[code] = code_counts.get(code, 0) + 1
        method_counts[method] = method_counts.get(method, 0) + 1
        
    return {'codes': code_counts, 'methods': method_counts}