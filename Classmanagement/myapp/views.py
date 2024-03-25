from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from myapp.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from myapp.models import Message
from myapp.models import Assignment, Submission, Challenge
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from urllib.parse import quote    #mã hóa tên tệp tin (tránh lỗi tải xuống)
import hashlib  #mã hóa tên file 
import os
from django.conf import settings

def authenticate_user(username_or_email, account_type):
    
    user = None

    if account_type == 'student':
        user = User.objects.filter((Q(username=username_or_email) | Q(email=username_or_email))& Q(role='student')).first()
        print(user)
    else:
        user = User.objects.filter((Q(username=username_or_email) | Q(email=username_or_email))& Q(role='teacher')).first()
        print(user)
    return user

def login_view(request):
    if request.method =='POST':
        account_type = request.POST['account_type']
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']
        

        user = authenticate( username=authenticate_user(username_or_email, account_type), password=password)
        # hashed_password = make_password(password)
        print(user)
        # print(hashed_password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            error_message = 'Invalid username or password.'
            messages.error(request, error_message)
            return redirect('login')
    return render(request, 'login.html')

def home(request):
    
    return render(request, 'home.html', {'user': request.user})

# def register_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         User.objects.create_user(username=username, email=email, password=password)
#         return redirect('login')  # Chuyển hướng đến trang đăng nhập sau khi đăng ký thành công
#     return render(request, 'register.html')

@login_required
def teacher_list(request):
        teachers =  User.objects.filter(role='teacher')  # Lấy tất cả người dùng từ bảng auth_user
        return render(request, 'teacher_list.html', {'teachers': teachers})

@login_required
def student_list(request):
    students = User.objects.filter(role='student')

    if request.user.role == 'teacher':
        return render(request, 'TE_student_list.html', {'students': students})

    if request.user.role == 'student':
        return render(request, 'ST_student_list.html', {'students': students})
    
@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        if (phone_number == user.phone_number and
            email == user.email):
            messages.success(request, 'No changes made!')
            return redirect('profile', username=username)
        else:
            # Cập nhật thông tin người dùng
            user.phone_number = phone_number
            user.email = email
            user.save()
            # Cập nhật phiên đăng nhập
            update_session_auth_hash(request, user)
            # Hiển thị thông báo khi cập nhật thành công
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile', username=username)
    return render(request, 'profile.html', {"user": user})

@login_required
def logout_view(request):
    logout(request)
    # Chuyển hướng đến trang sau khi đăng xuất, ví dụ: trang chính
    return redirect('login')

@login_required
def edit_student(request, student_id):
    if request.method == 'POST':
        username = request.POST['username']
        fullname = request.POST['fullname']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        last_name, first_name = fullname.split()

        user = User.objects.get(id=student_id)
       
        if (username == user.username and
            first_name == user.first_name and
            last_name == user.last_name and
            phone_number == user.phone_number and
            email == user.email):  
            messages.success(request, 'No changes made!')
            return redirect('/student/')
        else:
            # Cập nhật thông tin người dùng
            user.username = username
            user.first_name, user.last_name = fullname.split()  # Tách tên thành first name và last name
            user.phone_number = phone_number
            user.email = email
            user.save()
            # Hiển thị thông báo khi cập nhật thành công
            messages.success(request, 'Successfully edited student information!')
            return redirect('/student/')
    return redirect('/student/')

@login_required
def delete_student(request, student_id):
    if request.method == 'POST':
        student = User.objects.get(id=student_id)
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('/student/')  # Hoặc chuyển hướng đến trang khác sau khi xóa
    return redirect('/student/')

@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_email = request.POST['receiver']
        subject = request.POST['subject']
        body = request.POST['body']

         # Tìm user dựa trên địa chỉ email
        receiver_user = User.objects.get(email=receiver_email)        # Tạo một đối tượng Message mới và lưu vào cơ sở dữ liệu
        
        receiver_role = receiver_user.role

        sender_user = request.user
        message = Message(sender=sender_user, receiver=receiver_user, subject=subject, body=body)
        message.save()  
        if receiver_role == 'teacher':
            return redirect('/teacher/')  # Thay 'teacher_view' bằng tên URL pattern cho trang giáo viên
        elif receiver_role == 'student':
            return redirect('/student/')
    return render(request, 'ST_student_list.html')

@login_required
def message(request):
    sent_messages = Message.objects.select_related('receiver').filter(sender=request.user)
    received_messages = Message.objects.select_related('sender').filter(receiver=request.user)

    # render() trong Django chỉ chấp nhận một từ điển (dictionary) duy nhất làm tham số cuối cùng.
    context = {'sent_messages': sent_messages, 'received_messages': received_messages}
    return render(request, 'message.html', context)

@login_required
def compose_message(request):
    if request.method == 'POST':
        receiver_email = request.POST['receiver']
        subject = request.POST['subject']
        body = request.POST['body']
        
        # Tìm user dựa trên địa chỉ email
        receiver_user = User.objects.get(email=receiver_email)
        
        # Tạo một đối tượng Message mới và lưu vào cơ sở dữ liệu
        sender_user = request.user
        message = Message(sender=sender_user, receiver=receiver_user, subject=subject, body=body)
        message.save()  
        messages.success(request, 'Message sent successfully!')
        return redirect('/message/')
    return redirect('/message/')

@login_required
def delete_message(request, message_id):
    if request.method == 'POST':
        message = Message.objects.get(id=message_id)
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('/message/')  # Hoặc chuyển hướng đến trang khác sau khi xóa
    return redirect('/message/')

@login_required
def assignment(request):
    assignments = Assignment.objects.all()

    if request.user.role == 'student':
        return render(request, 'ST_assignment.html', {'assignments': assignments})

    if request.user.role == 'teacher':
        return render(request, 'TE_assignment.html', {'assignments': assignments})

def download_file(request, assignment_id):
    # Lấy đối tượng Assignment dựa trên assignment_id
    assignment = get_object_or_404(Assignment, id=assignment_id)
    # Đường dẫn tới tệp tin trong hệ thống
    file_name = assignment.file.name.split('/')[-1]
    file_path = assignment.file.path
    # Mở và đọc tệp tin
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        # Sử dụng quote để mã hóa tên tệp tin
        response['Content-Disposition'] = f'attachment; filename="{quote(file_name)}"'
        return response
    
def upload_file(request, assignment_id):
    if request.method == 'POST' and request.FILES.get('file'):
        # Lấy thông tin về student từ request.user và assignment_id từ request.POST hoặc từ định nghĩa của hàm
        student = request.user
        assignment_id = assignment_id  # Hoặc lấy từ request.POST, tùy vào cách bạn định nghĩa hàm và template

        # Lấy file từ request
        uploaded_file = request.FILES['file']
        
        # Tạo một instance mới của Submission và lưu vào database
        submission = Submission.objects.create(
            assignment_id=assignment_id,
            student_id=student.id,
            file=uploaded_file
        )
        submission.save()
        # Redirect hoặc hiển thị thông báo upload thành công
        messages.success(request, 'File uploaded successfully!')
        return redirect('assignment')  
    
    return redirect('assignment') 
    
@login_required
def create_assignment(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file') if 'file' in request.FILES else None
        
        assignment = Assignment.objects.create(title=title, description=description, file=file, created_by=request.user)
        assignment.save() 
        messages.success(request, 'Created new assignment successfully!')
        return redirect('assignment')  # Chuyển hướng đến trang danh sách Assignment sau khi tạo thành công
    
    return render(request, 'TE_assignment.html')

@login_required
def edit_assignment(request, assignment_id):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file') if 'file' in request.FILES else None

        assignment = Assignment.objects.get(id=assignment_id)
        # print(assignment.file)

        if (title == assignment.title and
            description == assignment.description and
            (file is None or file == assignment.file)):  
            messages.success(request, 'No changes made!')
            return redirect('/assignment/')
        else:
            # Cập nhật thông tin người dùng
            assignment.title = title
            assignment.description = description
            if file:
                assignment.file = file
            assignment.save()
            # Hiển thị thông báo khi cập nhật thành công
            messages.success(request, 'Successfully edited assignment!')
            return redirect('/assignment/')
    return redirect('/assignment/')

def delete_assignment(request, assignment_id):
    if request.method == 'POST':
        assignment = Assignment.objects.get(id=assignment_id)
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('/assignment/')  # Hoặc chuyển hướng đến trang khác sau khi xóa
    return redirect('/assignment/')

def detail_assignment(request, assignment_title):
    assignment = get_object_or_404(Assignment, title=assignment_title)
    submissions = Submission.objects.filter(assignment_id=assignment.id)
    # Lặp qua từng submission và lấy tên sinh viên từ bảng User
    for submission in submissions:
        # Lấy sinh viên từ bảng User
        student = submission.student
        # Lấy tên của sinh viên
        student_name = student.username  # Thay ".name" bằng trường tên của sinh viên trong bảng User

        # Đưa tên sinh viên vào context để truyền vào template
        submission.student_name = student_name
    context = {'assignment': assignment, 'submissions': submissions}

    return render(request, 'detail_assignment.html', context)


def encode_filename(filename):
    # Xóa dấu từ tên file
    encoded_filename = filename.encode('ascii', 'ignore').decode('utf-8')
    # Thay thế các ký tự đặc biệt bằng khoảng trắng
    encoded_filename = encoded_filename.replace('_', ' ')
    encoded_filename = encoded_filename.replace('-', ' ')
    # Loại bỏ các khoảng trắng kép
    encoded_filename = ' '.join(encoded_filename.split())
    return encoded_filename



@login_required
def challenge(request):
    challenges = Challenge.objects.all()

    if request.user.role == 'student':
        return render(request, 'ST_challenge.html', {'challenges': challenges})

    if request.user.role == 'teacher':
        return render(request, 'TE_challenge.html', {'challenges': challenges})



def encode_filename(filename):
    # Mã hóa tên file thành dạng bytes trước khi băm
    filename_bytes = filename.encode('utf-8')
    # Áp dụng hàm băm (hash) cho chuỗi bytes đã mã hóa
    hashed_filename = hashlib.md5(filename_bytes).hexdigest()
    return hashed_filename

def create_challenge(request):
    if request.method == 'POST':
        nameChallenge = request.POST.get('nameChallenge')
        hint = request.POST.get('hint')
        file = request.FILES.get('file') if 'file' in request.FILES else None
       
        # Lưu dữ liệu vào cơ sở dữ liệu
        new_challenge = Challenge.objects.create(nameChallenge=nameChallenge, hint=hint, created_by=request.user)
        
        folder_path = 'challenge/' + str(new_challenge.id) # Đường dẫn đến thư mục challenge/id
        if not os.path.exists(folder_path):
            os.makedirs(folder_path) 

        # Tạo đường dẫn cho file được upload
        file_path = os.path.join(folder_path, file.name)

        # Lưu file vào đường dẫn đã tạo
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Cập nhật đường dẫn của file vào đối tượng Challenge
        new_challenge.file = file_path
        new_challenge.save()
        return redirect('challenge')  
    
    return redirect('challenge') 


def edit_challenge(request, challenge_id):
    if request.method == 'POST':
        nameChallenge = request.POST.get('nameChallenge')
        hint = request.POST.get('hint')
        file = request.FILES.get('file') if 'file' in request.FILES else None

        challenge = Challenge.objects.get(id=challenge_id)

        if (nameChallenge == challenge.nameChallenge and
            hint == challenge.hint and
            (file is None or file == challenge.file)):  
            messages.success(request, 'No changes made!')
            return redirect('/challenge/')
        else:
            challenge.nameChallenge = nameChallenge
            challenge.hint = hint
            if file:
                challenge.file = file
                challenge.encoded_filename = encode_filename(file.name)
            challenge.save()
            # Hiển thị thông báo khi cập nhật thành công
            messages.success(request, 'Successfully edited challenge!')
            return redirect('/challenge/')

    return redirect('challenge') 

def delete_challenge(request, challenge_id):
    if request.method == 'POST':
        challenge = Challenge.objects.get(id=challenge_id)
        challenge.delete()
        messages.success(request, 'Challenge deleted successfully!')
        return redirect('/challenge/')  # Hoặc chuyển hướng đến trang khác sau khi xóa
    return redirect('/challenge/')

def answer_challenge(request, challenge_id):
    if request.method == 'POST':
        user_input = request.POST['answer']
        
        file_name = get_path(challenge_id)
        if compare_strings(user_input, file_name):
            return redirect('read_file', challenge_id=challenge_id)
        else:
            messages.error(request, "Oh no, that's not right. Please try again!")
            return redirect('/challenge/')  # Chuyển hướng người dùng đến trang `/challenge/` với thông báo lỗi

    return redirect('/challenge/')  
def compare_strings(user_input, file_name):
    if file_name is None:
        return 0  # Trả về 0 nếu không tìm thấy tên file

    # Lấy tên tập tin từ đường dẫn
    file_name = os.path.splitext(os.path.basename(file_name))[0]

    # Loại bỏ các kí tự đặc biệt
    file_name = file_name.replace('_', ' ').replace('-', ' ')
    
    if user_input.lower() == file_name.lower():
        return 1
    return 0

def read_file(request, challenge_id):
    challenge = Challenge.objects.get(id=challenge_id)
    file_path = challenge.file.path  # Thay file_field_name bằng tên của trường dữ liệu tệp trong model của bạn
    
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    context = {
        'challenge': challenge,
        'file_content': file_content,
    }

    messages.success(request, "Congratulations, you solved successfully")
    return render(request, 'read_file.html', context)


def get_first_file_in_folder(folder_path):
    first_file = None
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if files:
            first_file = files[0]
    return first_file

def get_path(challenge_id):
    # Thư mục chứa các tệp
    folder_path = 'E:/BlueC/Classmanagement/challenge'
    
    file_path = os.path.join(folder_path, str(challenge_id))
    if os.path.exists(file_path):
        first_file_in_folder = get_first_file_in_folder(file_path)
        return first_file_in_folder
    else:
        return None
