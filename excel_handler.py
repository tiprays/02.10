import pandas as pd
from datetime import datetime
import os


class ExcelHandler:
    def __init__(self):
        self.output_dir = "exports"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_to_excel(self, products, filename):
        """Сохранение данных в Excel файл"""
        try:
            # Подготовка данных
            data = []
            for i, product in enumerate(products, 1):
                row = {
                    '№': i,
                    'Название': product.get('name', ''),
                    'Бренд': product.get('brand', ''),
                    'Цена': product.get('price', 0),
                    'Рейтинг': product.get('rating', ''),
                    'Количество отзывов': product.get('reviews_count', ''),
                    'Ссылка': product.get('url', ''),
                    'Дата парсинга': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                data.append(row)

            # Создание DataFrame
            df = pd.DataFrame(data)

            # Сохранение в Excel
            filepath = os.path.join(self.output_dir, filename)

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Товары', index=False)

                # Настройка ширины колонок
                worksheet = writer.sheets['Товары']
                worksheet.column_dimensions['A'].width = 8
                worksheet.column_dimensions['B'].width = 50
                worksheet.column_dimensions['C'].width = 20
                worksheet.column_dimensions['D'].width = 15
                worksheet.column_dimensions['E'].width = 12
                worksheet.column_dimensions['F'].width = 18
                worksheet.column_dimensions['G'].width = 60
                worksheet.column_dimensions['H'].width = 20

            print(f"Файл сохранен: {filepath}")
            return filepath

        except Exception as e:
            print(f"Ошибка при сохранении в Excel: {e}")
            return None

    def get_file_info(self, filename):
        """Получение информации о сохраненном файле"""
        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            stats = os.stat(filepath)
            return {
                'filename': filename,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            }
        return None