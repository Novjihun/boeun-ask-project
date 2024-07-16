from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Flash 메시지 사용을 위한 시크릿 키 설정

def check_credentials(username, password):
    # 로그인 정보를 저장한 텍스트 파일 경로
    file_path = os.path.join(os.path.dirname(__file__), 'user-account.txt')
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                stored_username, stored_password = line.strip().split(',')
                if username == stored_username and password == stored_password:
                    return True
        return False
    except FileNotFoundError:
        return False

@app.route('/sign_in', methods=['POST'])
def sign_in():
    username = request.form.get("username")
    password = request.form.get("password")
    if check_credentials(username, password):
        return redirect(url_for('main'))  # 로그인 성공 시 메인 페이지로 리다이렉트
    else:
        flash("Invalid credentials. Please try again.")
        return redirect(url_for('login'))

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/leader_board')
def leader_board():
    return render_template('leader_board.html')

@app.route('/information')
def information():
    return render_template('information.html')

if __name__ == '__main__':
    app.run(debug=True)
