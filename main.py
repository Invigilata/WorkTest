import os
import csv


class PriceMachine():

    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 0

    def load_prices(self, directory='.'):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
        '''
        # Определяет допустимые названия столбцов
        product_names = {"товар", "название", "наименование", "продукт"}
        price_names = {"розница", "цена"}
        weight_names = {"вес", "масса", "фасовка"}

        # Сканирует каталог
        try:
            files = os.listdir(directory)
        except FileNotFoundError:
            print(f"Каталог {directory} не найден.")
            return

        for file in files:
            if "price" not in file.lower():
                continue  # Игнорирует файлы без "price" в названии
            file_path = os.path.join(directory, file)
            if not os.path.isfile(file_path):
                continue  # Игнорирует, если не файл
            try:
                with open(file_path, encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=',')
                    headers = next(reader)
                    # Приводит заголовки к нижнему регистру для сравнения
                    headers_lower = [h.strip().lower() for h in headers]
                    # Поиск индексов нужных столбцов
                    try:
                        product_idx = self._search_column(headers_lower, product_names)
                        price_idx = self._search_column(headers_lower, price_names)
                        weight_idx = self._search_column(headers_lower, weight_names)
                    except ValueError as e:
                        print(f"В файле {file} пропущены необходимые столбцы: {e}")
                        continue  # Пропускает файл, если столбцы не найдены
                    # Чтение данных
                    for row in reader:
                        if len(row) < max(product_idx, price_idx, weight_idx) + 1:
                            continue  # Пропускает строки с недостаточным количеством столбцов
                        product = row[product_idx].strip()
                        try:
                            price = float(row[price_idx].replace(',', '.'))
                            weight = float(row[weight_idx].replace(',', '.'))
                        except ValueError:
                            continue  # Пропускает строки с некорректными числами
                        if weight == 0:
                            continue  # Избегает деления на ноль
                        price_per_kg = price / weight
                        self.data.append({
                            "name": product,
                            "price": price,
                            "weight": weight,
                            "file": file,
                            "price_per_kg": price_per_kg
                        })
            except Exception as e:
                print(f"Ошибка при обработке файла {file}: {e}")
                continue  # Продолжает с другими файлами
        print(f"Загружено {len(self.data)} позиций из прайс-листов.")

    def _search_column(self, headers, possible_names):
        '''
            Возвращает индекс столбца, если найден, иначе выбрасывает исключение
        '''
        for idx, header in enumerate(headers):
            if header in possible_names:
                return idx
        raise ValueError(f"Не найден столбец из {possible_names}")

    def export_to_html(self, fname='output.html'):
        '''
            Экспортирует все данные в HTML файл
        '''
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Позиции продуктов</title>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: left;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <h2>Позиции продуктов</h2>
            <table>
                <tr>
                    <th>№</th>
                    <th>Наименование</th>
                    <th>Цена</th>
                    <th>Вес (кг)</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for idx, item in enumerate(self.data, start=1):
            html_content += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item["name"]}</td>
                    <td>{item["price"]}</td>
                    <td>{item["weight"]}</td>
                    <td>{item["file"]}</td>
                    <td>{round(item["price_per_kg"], 2)}</td>
                </tr>
            '''
        html_content += '''
            </table>
        </body>
        </html>
        '''
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Данные успешно экспортированы в {fname}")
        except Exception as e:
            print(f"Ошибка при экспорте в HTML: {e}")

    def find_text(self, text):
        '''
            Ищет позиции, содержащие текст в названии продукта (независимо от регистра)
            Возвращает отсортированный список по цене за кг.
        '''
        text_lower = text.lower()
        filtered = [item for item in self.data if text_lower in item["name"].lower()]
        # Сортировка по цене за кг.
        sorted_filtered = sorted(filtered, key=lambda x: x["price_per_kg"])
        return sorted_filtered


if __name__ == "__main__":
    pm = PriceMachine()
    pm.load_prices()

    while True:
        user_input = input("Введите текст для поиска или 'exit' для выхода: ").strip()
        if user_input.lower() == "exit":
            print("Работа завершена.")
            break
        results = pm.find_text(user_input)
        if not results:
            print("Ничего не найдено.")
            continue
        # Вывод результатов в консоль
        print(f"{'№':<5} {'Наименование':<40} {'Цена':<10} {'Вес':<10} {'Файл':<20} {'Цена за кг.':<15}")
        for idx, item in enumerate(results, start=1):
            print(
                f"{idx:<5} {item['name']:<40} {item['price']:<10} {item['weight']:<10} {item['file']:<20} {round(item['price_per_kg'], 2):<15}")

    # Экспорт всех данных в HTML по завершении работы
    pm.export_to_html()
