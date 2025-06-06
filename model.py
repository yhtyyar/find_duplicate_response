import csv

def read_csv(file_path, skip_header=True):
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            if skip_header:
                next(csv_reader)  # Пропускаем заголовок
            rows = []
            for row in csv_reader:
                if not row:  # Пропускаем пустые строки
                    continue
                rows.append(','.join(row))
            return rows
    except Exception as e:
        raise ValueError(f"Ошибка чтения файла: {e}")

def find_duplicates(rows):
    count = {}
    for row in rows:
        count[row] = count.get(row, 0) + 1
    duplicates = {k: v for k, v in count.items() if v > 1}
    return duplicates