def print_results(total, duplicates_count, duplicates):
    reset = '\033[0m'
    color = '\033[92m' if duplicates_count == 0 else '\033[91m'

    print(f"{color}Обработано строк: {total}{reset}")
    print(f"{color}Обнаружено дублей: {duplicates_count}{reset}")

    if duplicates:
        print("Дублирующиеся строки:")
        for key, val in duplicates.items():
            print(f"- {key} (повторяется {val} раз{reset})")
    else:
        print(f"{color}Дубликаты отсутствуют{reset}")