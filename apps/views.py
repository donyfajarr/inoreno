from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib import messages
from .decorators import login
from openpyxl import load_workbook
from datetime import datetime, timedelta, date
from . import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_date
# Create your views here.
from django.db.models import Q
import json
from django.http import JsonResponse
import requests
import urllib.parse
from urllib.parse import unquote

@login
def index(request):
    first_name = request.user.first_name
    last_name = request.user.last_name
    user = first_name + " " + last_name
    sum = models.project.objects.filter(assignee = request.user).exclude(Q(status=3)).count()
    rawproject = models.project.objects.filter(assignee = request.user).count()
    rawprojects = models.project.objects.filter(assignee = request.user)
    totaltask = models.task.objects.filter(assignee = request.user).exclude(Q(status=3)).count()
    rawtask = models.task.objects.filter(assignee = request.user).count()
    alltask = models.task.objects.filter(assignee = request.user).order_by('due_date').exclude(Q(due_date=None))
    opentask = models.task.objects.filter(assignee = request.user, status=1).count()
    opentaskraw = models.task.objects.filter(assignee = request.user, status=1, due_date__isnull=False).order_by("due_date")
    # undertask = models.task.objects.filter(assignee = request.user, status=2).count()
    closetask = models.task.objects.filter(assignee = request.user, status=3).count()
    rawunder = models.task.objects.filter(assignee = request.user, status=2)
    undertask = rawunder.count()
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    closeproject = models.project.objects.filter(assignee = request.user, status=3).count()

    categories = []
    open_counts = []
    closed_counts = []
    for i in range(5):
        day = start_of_week + timedelta(days=i)
        categories.append(day.strftime("%a"))
        closed_tasks = models.task.objects.filter(assignee = request.user, status=3, due_date = day).count()
        open_tasks = models.task.objects.filter(assignee = request.user, status__in=[1,2], due_date=day).count()
        closed_counts.append(closed_tasks)
        open_counts.append(-open_tasks)
    series = [
        {
            "name": "Closed",
            "data": closed_counts
        },
        {
            "name": "Open",
            "data": open_counts
        }
    ]

    chartdata = {
    "categories" : categories,
    "series" : series
    }

    data = {
        'labels' : ['Open Task', 'Under Review Task', 'Closed Task'],
        'series' : [opentask, undertask, closetask]
    }
    totalproject = models.project.objects.filter(assignee=request.user).count()
    closeproject = totalproject - sum
    reviewproject = totalproject - sum - closeproject
    print(rawunder)
    json_chartdata = json.dumps(chartdata)
    json_data = json.dumps(data)
    return render(request, 'index.html', {
        'user':user,
        'sum':sum,
        'totaltask':totaltask,
        'alltask' : alltask,
        'rawtask' : rawtask,
        'rawproject' : rawproject,
        'json_data' : json_data,
        'opentask' :opentask,
        'undertask' :undertask,
        'closetask' :closetask,
        'rawunder':rawunder,
        'opentaskraw' : opentaskraw,
        'rawprojects' : rawprojects,
        'closeproject' : closeproject,
        'reviewproject' : reviewproject,
        'json_chartdata' : json_chartdata
    
    })

def get_project_data(request):
    
    if request.method == 'GET':
        
        selected_project = request.GET.get('project_id')
      
        # Fetch data for the selected project
        # For example, let's assume you have a Task model with 'project' field
        tasks = models.task.objects.filter(id_project=selected_project)
    
        # Process the data and prepare it for the response
        closed_counts = []
        open_counts = []
        categories = []
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        for i in range(5):
            day = start_of_week + timedelta(days=i)
            categories.append(day.strftime("%a"))
            closed_tasks = tasks.filter(assignee = request.user, status=3, due_date = day).count()
            open_tasks = tasks.filter(assignee = request.user, status__in=[1,2], due_date=day).count()
            closed_counts.append(closed_tasks)
            open_counts.append(-open_tasks)
        # Perform calculations or processing to get the desired data
        # Here, we'll just count the tasks for each status for demonstration purposes

        # Prepare the data to be sent back to the client
        series = [
        {
            "name": "Closed",
            "data": closed_counts
        },
        {
            "name": "Open",
            "data": open_counts
        }
    ]
        data = {
            'series' : series
        }

        # Return the data in JSON format
        return JsonResponse(data)

    # If the request method is not GET or it's not an AJAX request, return an empty response or appropriate error
    return JsonResponse({'error': 'Invalid request'})
@login
def addissue(request):
    if request.method == "GET":
        getallproject = models.project.objects.all()
        allstatus = models.status.objects.all()
        allpriority = models.priority.objects.all()
        return render(request, 'addissue.html', {
            'getallproject' : getallproject,
            'allstatus' : allstatus,
            'allpriority' : allpriority
        })
    else:
        id = request.POST['id']
        subject = request.POST['subject']
        status = request.POST['status']
        priority = request.POST['priority']
        start_date = request.POST['start_date'] 
        due_date = request.POST['due_date'] 
        assignee = request.user
        pic = request.POST['pic']
        getstatus = models.status.objects.get(id=status)
        getpriority = models.priority.objects.get(id=priority)
        getproject = models.project.objects.get(id=id)
        createissue = models.task.objects.create(
            subject = subject,
            status = getstatus,
            id_project = getproject,
            id_priority = getpriority,
            start_date = start_date if start_date else None,
            due_date = due_date if due_date else None,
            assignee = assignee,
        )
        createpic = models.pic.objects.create(id_task = createissue, pic=pic)
        return redirect ('listproject')
@login
def listproject(request):
    listproject = models.project.objects.filter(assignee = request.user)
    return render(request, 'listproject.html', {
        'listproject': listproject,})

@login
def newproject(request):
    if request.method == "POST":
        subject = request.POST['name']
        desc = request.POST['description']
        get = models.status.objects.get(id=1)
        newproject = models.project(
            subject = subject,
            desc = desc,
            assignee = request.user,
            status = get
        )
        newproject.save()
        return redirect('confirmation', id=newproject.id)
    return render(request, 'newproject.html')

@login
def settings(request):
    user = request.user

    if request.method == "GET":

        try:
            get = models.settings.objects.get(user=user)
            
            dict = {
                'start_row' : get.start_row,
                'gannt_start_column' : get.gannt_start_column,
                'week_number_row' : get.week_number_row,
                'start_column' : get.start_column,
                'end_column' : get.end_column,
                'pic_column' : get.pic_column,
                'email_column' : get.email_column
            }
        except ObjectDoesNotExist:
            create = models.settings.objects.create(user=user)
            get = create
            dict={
                'start_row' : get.start_row,
                'gannt_start_column' : get.gannt_start_column,
                'week_number_row' : get.week_number_row,
                'start_column' : get.start_column,
                'end_column' : get.end_column,
                'pic_column' : get.pic_column,
                'email_column' : get.email_column
            }
        return render(request, 'settings.html',{
    'dict' : dict})
    else:
        get = models.settings.objects.get(user=user)
        get.gannt_start_column = request.POST['gannt_start_column']
        get.week_number_row = request.POST['week_number_row']
        get.start_row = request.POST['start_row']
        get.start_column = request.POST['start_column']
        get.end_column = request.POST['end_column']
        get.pic_column = request.POST['pic_column']
        get.email_column = request.POST['email_column']
        get.save()
        return redirect('settings')
    
@login
def confirmation (request, id):
    if request.method == 'POST':
        get = models.settings.objects.get(user=request.user)
        allpriority = models.priority.objects.all()

        forprint = list()
        if 'upload' in request.POST:
            # LOAD XLSX
            files = request.FILES['filea']
            wb = load_workbook(files)
            ws = wb.active
            
            # START GANTT CHART ROW
            start_row = get.start_row

            # STORED COLUMN VALUES

            def get_date_range_for_week(year, week_start, week_end):
                if week_start is None or week_start < 1:
                    return []
                first_day = datetime(year, 1, 1)
                def calculate_week_dates(week_number):
                    offset = (week_number - 1) * 7
                    start_date = first_day + timedelta(days=offset)
                    end_date = start_date + timedelta(days=4)
                    return start_date, end_date
                if week_end is None:
                    start_date, end_date = calculate_week_dates(week_start)
                    return [(start_date, end_date)] 
                elif week_start is not None and week_end is not None and week_end >= week_start:
                    start_date = calculate_week_dates(week_start)[0]
                    end_date = calculate_week_dates(week_end)[1]
                    return [(start_date, end_date)]
                else:
                    return []
                
            def find_col_with_filled_color(ws, row_index):
                filled_cells = []
                # 9 STATE THE COLUMN GANTT CHART STARTED
                for col_index in range(get.gannt_start_column, ws.max_column + 1):
                    cell = ws.cell(row=row_index, column=col_index)
                    if isinstance(cell.fill.fgColor.theme, int) or (cell.fill.fgColor.rgb != 'FFFF0000' and  cell.fill.fgColor.rgb !='00000000'):
                        findweek = ws.cell(get.week_number_row, col_index).value
                        filled_cells.append(findweek)

                return filled_cells if filled_cells else None
            
            all = {}
            all['col_start'] = []
            for i in range(1, get.end_column - get.start_column):
                all[f'col{i}_values'] = []
            all['col_end'] = []

            # ITERATE COLUMN 2 AS A BASE

            for row in ws.iter_rows(min_row=start_row,min_col=get.start_column,max_col=get.start_column, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                all['col_start'].append(cell_value)  
            # ITERATE ROW FOR EVERY COLUMN TO GET THE VALUES
            for i in range(1, get.end_column - get.start_column):
                for row in ws.iter_rows(min_row=start_row, min_col=get.start_column+i, max_col=get.start_column+i, values_only=True):
                    cell_value = row[0] if row and row[0] is not None else None
                    all[f'col{i}_values'].append(cell_value)
            for row in ws.iter_rows(min_row=start_row, min_col=get.end_column, max_col=get.end_column, values_only=True):
                cell_value = row[0] if row and row[0] is not None else None
                all['col_end'].append(cell_value)        
            
            
            tasks_data = []
            current_task = None
           
        # Dictionary to keep track of the current parent task at each column level
            current_tasks = {key: None for key in all.keys()}

            for idx, value in enumerate(all['col_start']):
                if value is not None:
                    # Main Task
                 
                    p = find_col_with_filled_color(ws, idx + start_row)
                    if p is not None:
                        if len(p) > 1:
                            week_start = min(p)
                            week_end = max(p)
                        else:
                            week_start = min(p)
                            week_end = None

                        get_ranges = get_date_range_for_week(2024, week_start, week_end)
                        for start_date, end_date in get_ranges:
                            start_date = start_date.strftime('%Y-%m-%d')
                            end_date = end_date.strftime('%Y-%m-%d')
                    else:
                        week_start = None
                        week_end = None
                        start_date = week_start
                        end_date = week_end

                    findpic = ws.cell(idx + start_row, get.pic_column).value
                    if findpic is not None:
                        findpic = findpic.upper()
                    findperson = ws.cell(idx + start_row, get.email_column).value
                    if findperson is not None:
                        if ',' in findperson:
                            findperson = findperson.split(',')
                        else:
                            findperson = [findperson]

                    current_task = {
                        'name': value,
                        'start_date': start_date,
                        'due_date': end_date,
                        'pic': findpic,
                        'person': findperson,
                        'subtasks': []
                    }
                    tasks_data.append(current_task)

                    # Set the current task for col_start level
                    current_tasks['col_start'] = current_task

                    # Reset the current task for all subsequent columns
                    for key in list(current_tasks.keys())[1:]:
                        current_tasks[key] = None

                else:
                    # Iterate through remaining columns to find subtasks
                    for key in list(all.keys())[1:]:
                        col_values = all[key]
                        subtask_value = col_values[idx]
                        if subtask_value is not None:
                          
                            p = find_col_with_filled_color(ws, idx + start_row)
                            if p is not None:
                                if len(p) > 1:
                                    week_start = min(p)
                                    week_end = max(p)
                                else:
                                    week_start = min(p)
                                    week_end = None

                                get_ranges = get_date_range_for_week(2024, week_start, week_end)
                                for start_date, end_date in get_ranges:
                                    start_date = start_date.strftime('%Y-%m-%d')
                                    end_date = end_date.strftime('%Y-%m-%d')
                            else:
                                week_start = None
                                week_end = None
                                start_date = week_start
                                end_date = week_end

                            findpic = ws.cell(idx + start_row, get.pic_column).value
                            if findpic is not None:
                                findpic = findpic.upper()
                            findperson = ws.cell(idx + start_row, get.email_column).value
                            if findperson is not None:
                                if ',' in findperson:
                                    findperson = findperson.split(',')
                                else:
                                    findperson = [findperson]
                       

                            subtask = {
                                'name': subtask_value,
                                'pic': findpic,
                                'start_date': start_date,
                                'due_date': end_date,
                                'person': findperson,
                                'subtasks': []
                            }

                            # Find the appropriate parent task for the current subtask
                            for parent_key in reversed(list(current_tasks.keys())[:list(current_tasks.keys()).index(key)]):
                                if current_tasks[parent_key] is not None:
                                    if 'subtasks' not in current_tasks[parent_key]:
                                        current_tasks[parent_key]['subtasks'] = []
                                    current_tasks[parent_key]['subtasks'].append(subtask)
                                    break

                            # Set the current task for the current column
                            current_tasks[key] = subtask

                            # Reset the current task for all subsequent columns
                            for subsequent_key in list(current_tasks.keys())[list(current_tasks.keys()).index(key) + 1:]:
                                current_tasks[subsequent_key] = None

            

         
            # IT IS USED TO ATTACH A PARENT NAME KEYS FOR A SUBTASKS BASED ON A SUBTASKS THAT CONTAINED IN PARENT
            def process_tasks(tasks, parent_name=None):
                for task in tasks:
                    task['Parent'] = parent_name
                    forprint.append(task)
                    if 'subtasks' in task and task['subtasks']:
                        process_tasks(task['subtasks'], parent_name=task['name'])
                    if 'subtasks' in task:
                        del task['subtasks']
            
            process_tasks(tasks_data)


            # print(forprint)
            # SESSION THE DATA TO BE PASSED INTO AFTER POST LOGIC

            request.session['forprint'] = forprint
            request.session['name'] = id

            return render (request, 'confirmation.html', {
                'tasks_data' : forprint,
                'allpriority' : allpriority
            })
        else:
            # IN THIS SECTION, THE DATA IS BEING CREATED INTO REDMINE DB
            # GET THE SESSION
            forprint = request.session.get('forprint',[])
            name = request.session.get('name',[])
            def create_issue(item):
                # THE ['name'] IS USE TO HANDLE A MULTIPLE FORM FOR A MULTIPLE TASK THAT WILL BE PROCCESSED
                
                form_name = f"name_{item['name']}"
                form_start_date = f"start_date_{item['name']}"
                form_due_date = f"due_date_{item['name']}"
                form_responsible = f"responsible_{item['name']}[]"
                form_priority = f"priority_{item['name']}"
                subject = request.POST.get(form_name)
                start_date = request.POST.get(form_start_date)
                due_date = request.POST.get(form_due_date)
                assigned_to = request.user
                
                priority = request.POST.get(form_priority)
                
                responsible = request.POST.getlist(form_responsible)
                ids = models.project.objects.get(id=id)
                pri = models.priority.objects.get(id=priority)
                start_date = parse_date(start_date) if start_date else None
                due_date = parse_date(due_date) if due_date else None
                create = models.task(
                    id_project = ids,
                    subject = subject, 
                    assignee = assigned_to,
                    start_date = start_date,
                    due_date = due_date,
                    id_priority = pri,)
                create.save()
                for email in responsible:
                    getid = models.task.objects.get(id=create.id)
                    pic = models.pic(id_task=getid, pic=email)
                    pic.save()
            for item in forprint:
                create_issue(item)
            
            return redirect('listproject')
    return render(request, 'confirmation.html')

@login
def deleteproject(request,id):
    get = models.project.objects.get(id=id)
    get.delete()
    return redirect('listproject')

@login
def updateproject(request, id):
    update = models.project.objects.get(id=id)
    if request.method == "GET":
        return render(request, 'updateproject.html',{
            'update' : update,
        })
    else:
        subject = request.POST.get('subject', '')  # Safely retrieve 'subject' from POST data
        description = request.POST.get('description', '')  # Safely retrieve 'description' from POST data
        
        # Update the project object with the retrieved values
        update.subject = subject
        update.desc = description
        update.save()
        return redirect ('listproject')


@login
def listissue(request,id):
    listissue = models.task.objects.filter(id_project = id)
    request.session['idproject'] = id
    return render(request, 'listissue.html', {
        'listissue' : listissue,
        
    })

def listdetails(request, id):
    if request.method == 'GET':
        get = models.task.objects.get(id=id)
        getproject = get.id_project
        getpic = models.pic.objects.filter(id_task = id)
        
        listpic = []
        for item in getpic:
            listpic.append(item.pic)
        listpic = ','.join(listpic)
        email = request.GET.get('email', '')
        if email:
            email = unquote(email)
        return render(request, 'listdetails.html', {
        "get" : get,
        "getproject" : getproject,
        'getpic' : listpic,
        'email' : email,
        'id' : id
    })
    else:
        sender = request.POST['sender']
        description = request.POST['description']
        get = models.task.objects.get(id=id)
        receipent = get.assignee.email
        fullname = get.assignee.first_name + " " + get.assignee.last_name
        email_api = "http://10.24.7.70:3333/send-email"
        subject = f"#{get.id}-{get.subject} Task Feedback"
        body = f"""
                Dear {fullname},

                This is my feedback about my #{get.id}-{get.subject} task:
                {description}
                
                Regards,
                {sender}
                """
        payload = {
            "to": [receipent],
            "cc": [],
            "subject": subject,
            "body": body
        }
        print(payload)
    #    response = requests.post(email_api, json=payload)
    #     if response.status_code == 200:
    #         print("Email sent successfully.")
    #     else:
    #         print(f"Failed to send email. Status code: {response.status_code}")
    #         print(response.text)
        return redirect ('listdetails', id=id)
        #  
    

@login
def newissue(request):
    allissue = models.task.objects.filter(assignee = request.user)
    print(allissue)
    return render(request, 'newissue.html',{
        'allissue' : allissue
    })
@login
def updateissue(request,id):
    get = models.task.objects.get(id=id)
    allpriority = models.priority.objects.all()
    getpic = models.pic.objects.filter(id_task = id)
    allstatus = models.status.objects.all()
    if request.method == "GET":
        print(getpic)
        return render(request, 'updateissue.html', {
            'update' : get,
            'allpriority' : allpriority,
            'getpic' : getpic,
            'allstatus' : allstatus
        })
    else:
        subject = request.POST['subject']
        status = request.POST['status']
        start_date = request.POST['start_date']
        due_date = request.POST['due_date']
        priority = request.POST['priority']
        addpic = request.POST['addpic']
        pic = request.POST.getlist("pic")

        get.subject = subject
        getstatus = models.status.objects.get(id=status)
        getpriority = models.priority.objects.get(id=priority)
        get.status = getstatus
        print('here',start_date)
        gettask = models.task.objects.get(id=id)
        findpic = models.pic.objects.filter(id_task = id)
        findpic.delete()
        print(pic)
        for i in pic:
            newpic = models.pic.objects.create(id_task = gettask, pic=i)
            newpic.save()
        if start_date:
            get.start_date = start_date
        if due_date:
            get.due_date = due_date
        get.priority = getpriority
        gettask = models.task.objects.get(id=id)
        if addpic:
            registerpic = models.pic.objects.create(id_task=gettask, pic=addpic)
            registerpic.save()
        get.save()
        return redirect('listdetails', id=id)
@login
def deleteissue(request,id):
    get = models.task.objects.get(id=id)
    get.delete()
    idproject = request.session.get('idproject')
    return redirect('listissue', id=idproject)



def user_login(request):
    if request.method == "GET":
        # FIND SESSION FROM RECENT LOGIN
        if request.session.get('username') and request.session.get('password'):
            return redirect('index')
        else:
            return render(request, 'login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        userobj = authenticate(request, username=username, password=password)
        if userobj is not None :
            auth_login(request, userobj)
            request.session['username'] = username
            request.session['password'] = password
            return redirect("index")
        else:
            messages.error(request, "Username atau Password Anda Salah!").delete()
            return redirect("login")
@login
def user_logout (request):
    logout(request)
    return redirect ('login')




@login
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
                "cc": [],
                "subject": subject,
                "body": body
            }
            print(payload)
        #     response = requests.post(email_api, json=payload)
        #     if response.status_code == 200:
        #         print("Email sent successfully.")
        #     else:
        #         print(f"Failed to send email. Status code: {response.status_code}")
        #         print(response.text)

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
        
        return redirect('index')