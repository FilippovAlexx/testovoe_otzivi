pip install flask
python app.py



curl -X GET http://localhost:5000/reviews

curl -X GET "http://localhost:5000/reviews?sentiment=positive"
curl -X GET "http://localhost:5000/reviews?sentiment=negative"

curl -X POST -H "Content-Type: application/json" -d "{\"text\":\"Мне нравится этот сервис, он отличный!\"}" http://localhost:5000/reviews
