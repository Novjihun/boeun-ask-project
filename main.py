from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import datetime


app = Flask(__name__)
app.secret_key = 'supersecretkey'

def check_credentials(username, password):
    file_path = os.path.join(os.path.dirname(__file__), 'user-account.txt')
    try:
        with open(file_path, 'r') as file:
            for line in file:
                stored_username, stored_password, role = line.strip().split(',')
                if username == stored_username and password == stored_password:
                    return role
        return None
    except FileNotFoundError:
        return None
    
@app.route('/post_comment/<filename>', methods=['POST'])
def post_comment(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    post_username = filename.split('_')[0]
    if session.get('username') != post_username and session.get('role') != 'admin':
        return "댓글 작성 권한이 없습니다.", 403

    comment_content = request.form.get('comment')
    username = session.get('username')

    save_comment(filename, username, comment_content)
    return redirect(url_for('view_article', filename=filename))


def save_comment(post_id, username, content):
    comments_folder = os.path.join(os.path.dirname(__file__), 'comments')
    if not os.path.exists(comments_folder):
        os.makedirs(comments_folder)

    comment_filename = f"{post_id}_{username}_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
    comment_path = os.path.join(comments_folder, comment_filename)

    with open(comment_path, 'w') as file:
        file.write(f"작성자: {username}\n")
        file.write(f"작성일: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"내용: {content}\n")

def load_comments(post_id):
    comments_folder = os.path.join(os.path.dirname(__file__), 'comments')
    comments = []

    if os.path.exists(comments_folder):
        for filename in os.listdir(comments_folder):
            if filename.startswith(post_id):
                try:
                    with open(os.path.join(comments_folder, filename), 'r') as file:
                        lines = file.readlines()
                        comments.append({
                            'username': lines[0].strip().split(': ')[1],
                            'date': datetime.datetime.strptime(lines[1].strip().split(': ')[1], '%Y-%m-%d %H:%M:%S'),
                            'content': lines[2].strip().split(': ')[1]
                        })
                except Exception as e:
                    print(f"Error reading comment file {filename}: {e}")

    return sorted(comments, key=lambda c: c['date'], reverse=True)

@app.route('/view_article/<filename>', methods=['GET'])
def view_article(filename):
    data_folder = os.path.join(os.path.dirname(__file__), 'data')
    file_path = os.path.join(data_folder, filename)
    
    if not os.path.exists(file_path):
        return "파일을 찾을 수 없습니다.", 404
    
    try:
        filename_without_ext = filename[:-4]
        username, date_str = filename_without_ext.rsplit('_', 1)
        
        # 날짜 형식 파싱
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d-%H-%M-%S')
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
            title = lines[0].replace("제목: ", "").strip()
            content = lines[1].replace("내용: ", "").strip()
    except (IndexError, ValueError, IOError) as e:
        return f"파일을 읽는 중 오류 발생: {e}", 500
    
    post = {
        'filename': filename,  # 파일 이름
        'username': username,  # 파일 이름에서 추출한 사용자 이름
        'date': date_obj,      # 파일 이름에서 추출한 날짜
        'title': title,
        'content': content
    }
    
    comments = load_comments(filename)
    
    return render_template('article.html', post=post, comments=comments)




@app.route('/sign_in', methods=['POST'])
def sign_in():
    username = request.form.get("username")
    password = request.form.get("password")

    # 간단한 사용자 검증 (사용자 이름과 비밀번호가 저장된 파일로 대체 가능)
    file_path = os.path.join(os.path.dirname(__file__), 'user-account.txt')
    role = None
    try:
        with open(file_path, 'r') as file:
            for line in file:
                stored_username, stored_password = line.strip().split(',')
                if username == stored_username and password == stored_password:
                    if username == 'bhs2048':
                        role = 'admin'
                    else:
                        role = 'user'
                    break
    except FileNotFoundError:
        flash("로그인 정보가 일치하지 않습니다. 다시 시도해주세요.")
        return redirect(url_for('login'))

    if role:
        session['logged_in'] = True
        session['username'] = username
        session['role'] = role  # 사용자 역할 설정
        return redirect(url_for('main'))  # Redirect to main page after successful login
    else:
        flash("로그인 정보가 일치하지 않습니다. 다시 시도해주세요.")  # Flash message for incorrect login
        return redirect(url_for('login'))


@app.route('/article_post', methods=['POST'])
def article_post():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    username = session.get('username')
    
    # 데이터 폴더 생성
    data_folder = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # 파일 이름 생성 (날짜와 시간 포함)
    date_str = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    filename = f"{username}_{date_str}.txt"
    file_path = os.path.join(data_folder, filename)
    
    # 파일에 제목과 내용 작성
    with open(file_path, 'w') as file:
        file.write(f"제목: {title}\n") 
        file.write(f"내용: {content}\n")
    
    return redirect(url_for('leader_board'))


@app.route('/write', methods=['GET', 'POST'])
def write():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        return article_post()
    
    return render_template('write-page.html')

@app.route('/leader_board')
def leader_board():
    posts = []
    data_folder = os.path.join(os.path.dirname(__file__), 'data')
    
    if os.path.exists(data_folder):
        for filename in os.listdir(data_folder):
            if filename.endswith('.txt'):
                try:
                    file_path = os.path.join(data_folder, filename)
                    with open(file_path, 'r') as file:
                        lines = file.readlines()
                        title = lines[0].replace("제목: ", "").strip()
                        content = lines[1].replace("내용: ", "").strip()
                        
                        # Extract username and date_str from filename
                        try:
                            # Remove .txt and split by the last dash
                            filename_without_ext = filename[:-4]
                            username, date_str = filename_without_ext.rsplit('_', 1)
                            
                            # Extract only the date part (YYYY-MM-DD)
                            date_part = date_str.split('_')[0]
                            
                            # Print debug information
                            print(f"Filename: {filename}")
                            print(f"Extracted username: {username}")
                            print(f"Extracted date_part: {date_part}")
                            
                            # Convert date_part to datetime object (with time set to 00:00:00)
                            date_obj = datetime.datetime.strptime(date_part, '%Y-%m-%d-%H-%M-%S')
                            
                            post = {
                                'title': title,
                                'content': content,
                                'username': username,
                                'date': date_obj
                            }
                            posts.append(post) 
                        except ValueError as e:
                            print(f"Invalid date format in file: {filename}")
                            print(f"Error details: {e}")
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
    
    posts.sort(key=lambda x: x['date'], reverse=True)
    return render_template('leader-board.html', login=session.get('logged_in'), username=session.get('username'), posts=posts)

@app.route('/')
def main():
    return render_template('main.html', login=session.get('logged_in'), username=session.get('username'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/information')
def information():
    return render_template('information.html', login=session.get('logged_in'), username=session.get('username'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('main'))

@app.route('/my_info')
def my_info():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('my_info.html', username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)