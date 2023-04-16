from flask import Flask
app = Flask(__name__)

@app.route('/')
def get_text():
    return 'Welcome to social capital toolkit'

if __name__ == '__main__':
    app.run(debug=True)
