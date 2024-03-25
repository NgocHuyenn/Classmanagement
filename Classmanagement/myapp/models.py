from django.contrib.auth.models import AbstractUser
from django.db import models
import os



# Create your models here.
# class MyModel(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()

class User(AbstractUser):

    phone_number = models.CharField(max_length=20, blank=True)

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='assignment/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submission/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"
    
def challenge_file_upload_path(instance, filename):
    # Tạo thư mục con với tên là 'challenge/id/' trong thư mục media
    return os.path.join('challenge', str(instance.id), filename)

class Challenge(models.Model):
    nameChallenge = models.CharField(max_length=100)
    hint = models.TextField()
    file = models.FileField(upload_to=challenge_file_upload_path)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nameChallenge