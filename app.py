from flask import Flask, render_template, request, jsonify
from parser import WildberriesParser
from excel_handler import ExcelHandler
import os
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search_products():
    try:
        query = request.form.get('query')

        if not query:
            return jsonify({'error': 'Введите поисковый запрос'})

        # Парсинг данных
        parser = WildberriesParser()
        products = parser.search_products(query)

        if not products:
            return jsonify({'error': 'Товары не найдены'})

        # Сохранение в Excel
        excel_handler = ExcelHandler()
        filename = f"wildberries_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = excel_handler.save_to_excel(products, filename)

        # Статистика для отображения
        stats = {
            'total_products': len(products),
            'min_price': min(p['price'] for p in products),
            'max_price': max(p['price'] for p in products),
            'avg_price': sum(p['price'] for p in products) // len(products),
            'filename': filename
        }

        return jsonify({
            'success': True,
            'products': products[:10],  # Показываем первые 10 товаров
            'stats': stats
        })

    except Exception as e:
        return jsonify({'error': f'Ошибка при поиске: {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)