import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import mysql.connector
import secrets


# kết nối với database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345678",
  database="mydatabase"
)

# Hàm kiểm tra đăng nhập
def check_login(username, password):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM persons WHERE username = %s AND password = %s", (username, password))
    user_login = cursor.fetchone()
    cursor.close()
    return user_login

# Hàm kiểm tra người dùng tồn tại
def check_user(username):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM persons WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

# Hàm thêm người dùng mới (đăng ký)
def insert_user(name,phone,username,password):
    cursor = mydb.cursor()
    sql = "INSERT INTO persons (name, phone, userName, password) VALUES (%s, %s,%s,%s)"
    val = (name,phone,username,password)
    cursor.execute(sql, val)
    mydb.commit() # Xác nhận và áp dụng các thay đổi vào cơ sở dữ liệu
    cursor.close()

def insert_task(nameTask, descriptions,estimate,progress):
    cursor = mydb.cursor()
    sql = "INSERT INTO tasks (nameTask, descriptions, estimate, progress) VALUES (%s, %s,%s,%s)"
    val = (nameTask, descriptions, estimate, progress)
    cursor.execute(sql, val)
    mydb.commit() # Xác nhận và áp dụng các thay đổi vào cơ sở dữ liệu
    cursor.close()

def get_tasks_html():
    cursor = mydb.cursor()
    cursor.execute("SELECT idTask, nameTask, descriptions, estimate, progress FROM tasks")
    tasks = cursor.fetchall()

    task_html = "<table>"
    # Thêm header cho bảng
    task_html += "<tr><th>ID</th><th>Name</th><th>Description</th><th>Estimate</th><th>Progress</th><th>Action</th></tr>"
    for task in tasks:
        task_html += "<tr>"
        task_html += f"<td>{task[0]}</td>"  # ID
        task_html += f"<td>{task[1]}</td>"  # Name
        task_html += f"<td>{task[2]}</td>"  # Description
        task_html += f"<td>{task[3]}</td>"  # Estimate
        task_html += f"<td>{task[4]}</td>"  # Progress
        task_html += f'<td><a href="/delete-task/{task[0]}">Delete</a></td>'  # Delete
        task_html += '<td><canvas id="progressCanvas" width="100" height="20"></canvas></td>'
        task_html += "</tr>"
    task_html += "</table>"
    html = read_file("taskmanager.html", "style.css")
    html = html.replace('<task_table>', task_html)
    return html

# tạo phiên
sessions = {}
def generate_session_token():
    # Sử dụng secrets token_urlsafe để tạo ra một session token ngẫu nhiên
    return secrets.token_urlsafe(16)  # Độ dài token là 16 ký tự

# Class xử lý các yêu cầu HTTP
class MyHandler(BaseHTTPRequestHandler):
       
    # Hàm xử lý yêu cầu GET
    def do_GET(self):
        if self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(read_file("login.html", "style.css"), 'utf-8'))

        elif self.path.startswith('/taskmanager'):
            # Kiểm tra phiên
            # Trích xuất session token từ cookie (nếu tồn tại)
            cookie_header = self.headers.get('Cookie', '')
            cookie_parts = cookie_header.split('=')
            if len(cookie_parts) >= 2:
                session_token = cookie_parts[1]
            else:
                # Xử lý trường hợp không tìm thấy session token trong cookie
                session_token = None 
            if session_token in sessions:
                # Người dùng đã đăng nhập, hiển thị trang quản lý công việc
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes(get_tasks_html(), 'utf-8'))
            else:
                # Chưa đăng nhập, chuyển hướng đến trang đăng nhập
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()


        elif self.path =='/register':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(read_file("register.html", "style.css"), 'utf-8'))
        
        elif self.path.startswith('/delete-task/'):
            task_id = self.path.split('/')[-1]
            cursor = mydb.cursor()
            cursor.execute(f"DELETE from tasks WHERE idTask = {task_id}")
            mydb.commit() # Xác nhận và áp dụng các thay đổi vào cơ sở dữ liệu
            cursor.close()
            self.send_response(303)  
            self.send_header('Location', '/taskmanager')
            self.end_headers()

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)

        if self.path == '/login':
            username_login = parsed_data['user'][0]
            password_login = parsed_data['pass'][0]
            
            # Kiểm tra xem username và password có trùng khớp trong cơ sở dữ liệu không
            user_login = check_login(username_login, password_login)
            if user_login:

                # Tạo một session token duy nhất
                session_token = generate_session_token()
            
                # Lưu thông tin người dùng vào session
                sessions[session_token] = {'username': username_login}
                self.send_response(303)  
                self.send_header('Location', '/taskmanager')
                self.send_header('Set-Cookie', f'session_token={session_token}; Path=/')
                self.end_headers()
            else:
                self.send_response(401)  # Unauthorized
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Invalid username or password')
        
        elif self.path.startswith('/taskmanager'):
            nameTask = parsed_data['task'][0]
            descriptions = parsed_data['descriptions'][0]
            estimate = parsed_data['estimate'][0]
            progress = parsed_data['progress'][0]
            self.send_response(200)  
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            insert_task(nameTask,descriptions, estimate, progress)
            self.wfile.write(b'Add task successfully!')

        elif self.path == '/register':
            name = parsed_data['name'][0]
            username = parsed_data['user'][0]
            phone = parsed_data['phone'][0]
            password = parsed_data['pass'][0]
            passwordRepeat = parsed_data['pass_repeat'][0]

            if password != passwordRepeat:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Mat khau khong match')
            else:
                # Kiểm tra xem tồn tại user chưa:
                user = check_user(username)
                if user:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'User already exists!')
                else:
                    self.send_response(303)
                    self.send_header('Location', '/login')
                    self.end_headers()
                    insert_user(name,phone,username,password)
                    self.wfile.write(b'Singup successfully!')

# Hàm đọc nội dung của tệp HTML
def read_file(file_html, file_css):
    html_content =''
    css_content = ''
    with open(file_html, "r") as html_file:
        html_content = html_file.read()
    
    with open(file_css, "r") as css_file:
        css_content = css_file.read()

    html_with_css = html_content.replace('</head>', '<style>' + css_content + '</style></head>')
    
    return html_with_css


# Tạo máy chủ HTTP
def run():
    print('Starting server...')
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server started...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()