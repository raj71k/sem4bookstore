from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/new')
def new():
    return '<h2>This is a new page</h2>'


@app.route('/profile/<username>')
def profile(username):
    return render_template('profile.html',username=username)


app.run(debug=True)
