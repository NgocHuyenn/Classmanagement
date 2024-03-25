Công cụ sử dụng : Django, MySQL



**Setup Django:**

pip install django
django-admin startproject classmanagement
cd classmanagement
python manage.py makemigrations
python manage.py migrate
python manage.py startapp myapp

python manage.py runserver



**Models:**
from django.contrib.auth.models import AbstractUser
from django.db import models
import os

class User(AbstractUser):
class Message(models.Model):
class Assignment(models.Model):
class Submission(models.Model):
class Challenge(models.Model):

**Import:**

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
