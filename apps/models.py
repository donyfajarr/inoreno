from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class status(models.Model):
    id = models.AutoField(primary_key=True)
    jenis = models.CharField(max_length=30)

    def __str__(self):
        return str(self.jenis)
    
class project(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=50)
    desc = models.TextField(max_length=150)
    status = models.ForeignKey(status, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete = models.CASCADE)
    link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.subject)
    
class priority(models.Model):
    id = models.AutoField(primary_key=True)
    jenis = models.CharField(max_length=30)

    def __str__(self):
        return str(self.jenis)
    

class task(models.Model):
    id = models.AutoField(primary_key=True)
    id_project = models.ForeignKey(project, on_delete=models.CASCADE)
    id_priority = models.ForeignKey(priority, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    start_date = models.DateField(null=True)
    due_date = models.DateField(null=True)
    assignee = models.ForeignKey(User, on_delete = models.CASCADE)
    status = models.ForeignKey(status,on_delete=models.CASCADE, default=1)
    parent = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.subject)

class pic(models.Model):
    id = models.AutoField(primary_key=True)
    id_task = models.ForeignKey(task, on_delete=models.CASCADE)
    pic = models.EmailField()

    def __str__(self):
        return str(self.pic)

class feedback(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(null=True, blank=True)
    id_task = models.ForeignKey(task, on_delete=models.CASCADE)
    desc = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return str(self.id_task)

class settings(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gannt_start_column = models.IntegerField(default='9')
    week_number_row = models.IntegerField(default='4')
    start_row = models.IntegerField(default='5')
    start_column = models.IntegerField(default='2')
    end_column = models.IntegerField(default='6')
    pic_column = models.IntegerField(default='8')
    email_column = models.IntegerField(default='61')
    priority_column = models.IntegerField(default='62')

    def __str__(self):
        return str(self.user)