"""
URL configuration for Classmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import login_view, home, logout_view # register_view  #đường dẫn tuyệt đối: myapp.views
from myapp.views import profile
from myapp.views import teacher_list, student_list
from myapp.views import send_message, edit_student, delete_student
from myapp.views import message, compose_message, delete_message
from myapp.views import assignment, download_file, upload_file
from myapp.views import create_assignment, edit_assignment,  delete_assignment, detail_assignment
from myapp.views import challenge, create_challenge, edit_challenge,  delete_challenge
from myapp.views import answer_challenge, read_file

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('home/', home, name='home'),
    path('profile/<str:username>/', profile, name='profile'),
    # path('register/', register_view, name='register'),

    path('teacher/', teacher_list, name='teacher'),
    path('student/', student_list, name='student'),
    path('send-message/', send_message, name='send_message'), # URLpattern cho view send_message
    path('edit_student/<int:student_id>/', edit_student, name='edit_student'), # URLpattern cho view edit_student
    path('delete_student/<int:student_id>/', delete_student, name='delete_student'),

    path('message/', message, name='message'),
    path('compose_message/', compose_message, name='compose_message'),
    path('delete_message/<int:student_id>/', delete_message, name='delete_message'),
    
    path('assignment/', assignment, name='assignment'),
    path('download/<int:assignment_id>/', download_file, name='download_file'),
    path('upload_file/<int:assignment_id>/', upload_file, name='upload_file'),
    path('create_assignment/', create_assignment, name='create_assignment'),
    path('edit_assignment/<int:assignment_id>/', edit_assignment, name='edit_assignment'),
    path('delete_assignment/<int:assignment_id>/', delete_assignment, name='delete_assignment'),
    path('detail_assignment/<str:assignment_title>/', detail_assignment, name='detail_assignment'),

    path('challenge/', challenge, name='challenge'),
    path('create_challenge/', create_challenge, name='create_challenge'),
    path('edit_challenge/<int:challenge_id>/', edit_challenge, name='edit_challenge'),
    path('delete_challenge/<int:challenge_id>/', delete_challenge, name='delete_challenge'),
    path('answer_challenge/<int:challenge_id>/', answer_challenge, name='answer_challenge'),
    path('read_file/<int:challenge_id>/', read_file, name='read_file')
]