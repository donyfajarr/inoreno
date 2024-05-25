import requests
from datetime import date
from . import models
import urllib.parse

def send_email(request):
    if request.method == "GET":
        today = date.today()
        
        # Query tasks
        start_today_tasks = models.task.objects.filter(start_date=today)
        end_today_tasks = models.task.objects.filter(due_date=today)
        ongoing_tasks = models.task.objects.filter(assignee=request.user, start_date__lte=today, due_date__gte=today)

        def find_pic(task):
            return list(models.pic.objects.filter(id_task=task))

        def create_email_body(task, status, recipient_email):
            general_name = "Team Member"
            fullname = task.assignee.first_name + " " + task.assignee.last_name
            author_name = fullname            
            project_name = task.id_project.subject
            subject = task.subject
            start_date = task.start_date
            due_date = task.due_date
            task_id = task.id

            encoded_email = urllib.parse.quote(recipient_email)
            if status == 'start':
                body = f"""
                Dear {general_name},

                You have a task that started today and will be due on {due_date} from the {project_name} project
                with the task subject: {subject}.

                View more at: http://10.24.7.165/listdetails/{task_id}?email={encoded_email}

                Regards,
                {author_name}
                """
            elif status == 'ongoing':
                body = f"""
                Dear {general_name},

                You still have a running task that started on {start_date} and will be due on {due_date}
                from the {project_name} project with the task subject: {subject}.

                View more at: http://10.24.7.165/listdetails/{task_id}?email={encoded_email}

                Regards,
                {author_name}
                """
            else:
                body = f"""
                Dear {general_name},

                You have a task that will be due today ({due_date}) from the {project_name} project
                with the task subject: {subject}.

                View more at: http://10.24.7.165/listdetails/{task_id}?email={encoded_email}

                Regards,
                {author_name}
                """
            return body

        def send_email(to, cc, subject, body):
            email_api = "http://10.24.7.70:3333/send-email"
            payload = {
                "to": [to],
                "cc": [cc],
                "subject": subject,
                "body": body
            }
            print(payload)
            response = requests.post(email_api, json=payload)
            if response.status_code == 200:
                print("Email sent successfully.")
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                print(response.text)

        # # Process tasks and send emails
        for task in start_today_tasks:
            pics = find_pic(task)
            for pic in pics:
                body = create_email_body(task, 'start', pic.pic)
                send_email(pic.pic, task.assignee.email, f"#{task.id} [{task.subject}] Task Reminder", body)
        
        for task in end_today_tasks:
            pics = find_pic(task)
            for pic in pics:
                body = create_email_body(task, 'end', pic.pic)
                send_email(pic.pic, task.assignee.email, f"#{task.id} [{task.subject}] Task Reminder", body)
        
        for task in ongoing_tasks:
            pics = find_pic(task)
            for pic in pics:
                body = create_email_body(task, 'ongoing', pic.pic)
                send_email(pic.pic, task.assignee.email, f"#{task.id} [{task.subject}] Task Reminder", body)
        
        return "success"
    