from flask import Flask, render_template, request, send_file, jsonify
from parser import JazzShopParser
import os
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()

        if not query:
            return render_template('index.html', error="Введите поисковый запрос")

        print(f"Поисковый запрос: {query}")

        # Создаем парсер и выполняем поиск
        parser = JazzShopParser()

        # Поиск товаров
        products = parser.search_products(query)
        print(f"Найдено товаров: {len(products)}")

        # Получаем детальную информацию для товаров (ограничим для скорости)
        detailed_products = []
        max_detailed = min(3, len(products))  # Ограничиваем до 3 товаров для детального парсинга

        for i, product in enumerate(products):
            if i < max_detailed and product.get('Ссылка'):
                print(f"Получение детальной информации для товара {i + 1}")
                detailed_info = parser.get_detailed_info(product['Ссылка'])
                product.update(detailed_info)
            detailed_products.append(product)

        # Сохраняем в Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(x for x in query if x.isalnum() or x in (' ', '-', '_')).rstrip()
        filename = f"jazz_shop_{safe_query}_{timestamp}.xlsx"

        success = parser.save_to_excel(detailed_products, filename)

        # Статистика
        stats = {
            'total_found': len(products),
            'detailed_processed': max_detailed,
            'in_stock': len([p for p in products if p.get('Наличие') == 'В наличии']),
            'filename': filename if success else None
        }

        return render_template('index.html',
                               products=detailed_products,
                               query=query,
                               stats=stats,
                               success=success)

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание файла Excel"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка загрузки файла: {e}"


@app.route('/api/search/<query>')
def api_search(query):
    """API endpoint для поиска"""
    parser = JazzShopParser()
    products = parser.search_products(query)
    return jsonify(products)


@app.route('/cleanup')
def cleanup():
    """Очистка временных файлов (опционально)"""
    try:
        for file in os.listdir('.'):
            if file.startswith('jazz_shop_') and file.endswith('.xlsx'):
                os.remove(file)
        return "Файлы очищены"
    except Exception as e:
        return f"Ошибка очистки: {e}"


if __name__ == '__main__': #Запуск
    # Создаем папку для шаблонов если её нет
    if not os.path.exists('templates'):
        os.makedirs('templates')

    app.run(debug=True, host='0.0.0.0', port=5000)