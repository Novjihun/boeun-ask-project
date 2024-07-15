from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/leader-board')
def leader_board():
    return render_template('leaderboard.html')

if __name__ == '__main__':
    app.run(debug=True) 