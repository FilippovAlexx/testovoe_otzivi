from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put aapplication's code here
    return 'Hello World!'

a
if __name__ == '__main__':
    app.run()
