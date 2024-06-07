from flask import Flask, render_template

app = Flask(__name__)

@app.route('/main')
def main():
    return render_template("main.html")

def start():
    app.run(debug=True,port=80)

if __name__== '__start__':
    start()