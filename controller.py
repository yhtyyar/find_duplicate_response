import argparse
import model
import view

def main():
    file_path = "/home/tester/PycharmProjects/find_duplicate_text/res/requests_07:08_06.06.2025.csv"

    try:
        rows = model.read_csv(file_path)
        total = len(rows)
        duplicates = model.find_duplicates(rows)
        duplicates_count = sum(v - 1 for v in duplicates.values())

        view.print_results(total, duplicates_count, duplicates)

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()