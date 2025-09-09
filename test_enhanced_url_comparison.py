"""
Тест для проверки улучшенного сравнения URL с query-параметрами.
"""

import tempfile
import os
import model


def test_enhanced_url_comparison():
    """Тест улучшенного сравнения URL с query-параметрами."""
    
    # Создаем временный CSV файл с тестовыми данными
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='')
    temp_file.write('URL,Status,Response Code,Protocol,Method,Content-Type,Client Address,Client Port,Remote Address,Remote Port,Exception,Request Start Time,Request End Time,Response Start Time,Response End Time,Duration (ms),DNS Duration (ms),Connect Duration (ms),SSL Duration (ms),Request Duration (ms),Response Duration (ms),Latency (ms),Speed (KB/s),Request Speed (KB/s),Response Speed (KB/s),Request Handshake Size (bytes),Request Header Size (bytes),Request Body Size (bytes),Response Handshake Size (bytes),Response Header Size (bytes),Response Body Size (bytes),Request Compression,Response Compression\n')
    
    # Добавляем фиктивную первую строку, которая будет пропущена
    temp_file.write('dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy,dummy\n')
    
    # Тестовые данные для проверки сравнения URL
    test_data = [
        # Группа 1: Одинаковые URL с одинаковыми параметрами в разном порядке (должны быть дублями)
        'https://ads.adfox.ru/285963/event?hash=004fe8d1737&param=value,COMPLETE,404,HTTP,GET,text/html,127.0.0.1,8080,ads.adfox.ru,443,,2025-01-01 10:00:00,2025-01-01 10:00:01,2025-01-01 10:00:01,2025-01-01 10:00:01,100,0,50,0,25,25,50,1000,500,500,100,200,300,,',
        'https://ads.adfox.ru/285963/event?param=value&hash=004fe8d1737,COMPLETE,404,HTTP,GET,text/html,127.0.0.1,8080,ads.adfox.ru,443,,2025-01-01 10:00:05,2025-01-01 10:00:06,2025-01-01 10:00:06,2025-01-01 10:00:06,100,0,50,0,25,25,50,1000,500,500,100,200,300,,',
        
        # Группа 2: Одинаковые URL с разными значениями параметров (не должны быть дублями)
        'https://ads.adfox.ru/285963/event?hash=004fe8d1737,COMPLETE,404,HTTP,GET,text/html,127.0.0.1,8080,ads.adfox.ru,443,,2025-01-01 10:00:10,2025-01-01 10:00:11,2025-01-01 10:00:11,2025-01-01 10:00:11,100,0,50,0,25,25,50,1000,500,500,100,200,300,,',
        'https://ads.adfox.ru/285963/event?hash=different_value,COMPLETE,404,HTTP,GET,text/html,127.0.0.1,8080,ads.adfox.ru,443,,2025-01-01 10:00:15,2025-01-01 10:00:16,2025-01-01 10:00:16,2025-01-01 10:00:16,100,0,50,0,25,25,50,1000,500,500,100,200,300,,',
        
        # Группа 3: Разные URL (не должны быть дублями)
        'https://ads.adfox.ru/285963/event?hash=unique1,COMPLETE,404,HTTP,GET,text/html,127.0.0.1,8080,ads.adfox.ru,443,,2025-01-01 10:00:20,2025-01-01 10:00:21,2025-01-01 10:00:21,2025-01-01 10:00:21,100,0,50,0,25,25,50,1000,500,500,100,200,300,,',
        'https://different-domain.com/285963/event?hash=unique1,COMPLETE,404,HTTP,GET,text/html,127.0.0.1,8080,different-domain.com,443,,2025-01-01 10:00:25,2025-01-01 10:00:26,2025-01-01 10:00:26,2025-01-01 10:00:26,100,0,50,0,25,25,50,1000,500,500,100,200,300,,',
    ]
    
    for data in test_data:
        temp_file.write(data + '\n')
    
    temp_file.close()
    
    try:
        # Читаем данные из файла
        rows = model.read_csv(temp_file.name)
        print(f"Прочитано строк: {len(rows)}")
        
        # Ищем дубликаты
        duplicates = model.find_duplicates(rows)
        print(f"Найдено групп дубликатов: {len(duplicates)}")
        
        # Выводим информацию о дубликатах
        for key, count in duplicates.items():
            print(f"Группа дубликатов ({count} элементов):")
            # Извлекаем URL из ключа для лучшей читаемости
            url_part = key.split('-')[0]
            print(f"  URL: {url_part}")
            print("---")
            
        # Проверяем результаты
        # Ожидаем 1 группу дубликатов (первые две строки с одинаковыми параметрами в разном порядке)
        if len(duplicates) == 1 and list(duplicates.values())[0] == 2:
            print("ТЕСТ ПРОЙДЕН: Улучшенное сравнение URL работает корректно")
            print("Результаты теста:")
            print("  ✓ URL с одинаковыми параметрами в разном порядке считаются дублями")
            print("  ✓ URL с разными значениями параметров не считаются дублями")
            print("  ✓ Разные домены не считаются дублями")
        else:
            print("ТЕСТ НЕ ПРОЙДЕН: Ошибка в улучшенном сравнении URL")
            print("Подробности:")
            print(f"  Количество групп дубликатов: {len(duplicates)}")
            if duplicates:
                print(f"  Размеры групп: {list(duplicates.values())}")
            
    except Exception as e:
        print(f"Ошибка при выполнении теста: {e}")
    finally:
        # Удаляем временный файл
        os.unlink(temp_file.name)


if __name__ == "__main__":
    test_enhanced_url_comparison()