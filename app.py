from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_restx import Api, Resource, fields
import os

app = Flask(__name__)
api = Api(
    app, title='Sentiment Analysis API', version='1.0',
    description='API для анализа тональности отзывов'
)

DATABASE = 'reviews.db'

review_model = api.model(
    'Review', {
        'text': fields.String(required=True, description='Текст отзыва'),
        'sentiment': fields.String(description='Тональность (auto-detected)'),
        'created_at': fields.String(description='Дата создания')
    }
)


def get_db_connection():
    """Создаём соединение с БД"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализация БД с проверкой существования таблицы"""
    with get_db_connection() as conn:
        conn.execute(
            '''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        '''
        )
        conn.commit()


if not os.path.exists(DATABASE):
    init_db()


def analyze_sentiment(text):
    text = text.lower()
    positive_words = ['хорош', 'отличн', 'прекрасн', 'любл', 'нравит', 'супер', 'класс']
    negative_words = ['плох', 'ужасн', 'ненавиж', 'отвратительн', 'кошмар', 'разочарован']

    if any(word in text for word in positive_words):
        return 'positive'
    if any(word in text for word in negative_words):
        return 'negative'
    return 'neutral'


@api.route('/reviews')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Отзыв добавлен')
    @api.response(500, 'Ошибка сервера')
    def post(self):
        """Добавить новый отзыв"""
        try:
            data = api.payload
            if not data or 'text' not in data:
                return {'message': 'Необходим текст отзыва'}, 400

            text = data['text']
            sentiment = analyze_sentiment(text)
            created_at = datetime.utcnow().isoformat()

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
                    (text, sentiment, created_at)
                )
                review_id = cursor.lastrowid
                conn.commit()

            return {
                'id': review_id,
                'text': text,
                'sentiment': sentiment,
                'created_at': created_at
            }, 201
        except Exception as e:
            return {'message': f'Ошибка сервера: {str(e)}'}, 500

    @api.doc(params={'sentiment': 'Фильтр по тональности (positive/negative/neutral)'})
    @api.response(200, 'Успешный запрос')
    @api.response(500, 'Ошибка сервера')
    def get(self):
        """Получить список отзывов"""
        try:
            sentiment_filter = request.args.get('sentiment')

            query = 'SELECT id, text, sentiment, created_at FROM reviews'
            params = ()

            if sentiment_filter:
                query += ' WHERE sentiment = ?'
                params = (sentiment_filter,)

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                reviews = cursor.fetchall()

            return [dict(row) for row in reviews]
        except Exception as e:
            return {'message': f'Ошибка сервера: {str(e)}'}, 500


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
