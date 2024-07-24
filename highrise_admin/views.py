import pandas as pd
from django.shortcuts import render, HttpResponse, redirect, reverse, get_object_or_404
from highrise_app.models import *
from datetime import datetime, timedelta
from django.db.models import Count, Case, When, IntegerField, Sum, F, Q, Exists, OuterRef, Subquery, Value, CharField, Func
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.conf import settings
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models.fields import CharField

from io import StringIO  
import json
from django.db import transaction
import calendar
from django.contrib import messages
import time




current_da = datetime.now().date()

# Calculate yesterday's date
yesterday_date = current_da - timedelta(days=1)

# Format yesterday's date as a string in the desired format
yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")


def error_404_view(request, exception):
    return render(request, '404.html', status=404)
    

@login_required(login_url='')
def CreateMember(request):
    if request.method == 'POST':
        # print("==========1============")
        try:
            # print("=========2=============")
            name = request.POST['uname']
            team_name = request.POST.get('team_name')
            designation = request.POST['designation']
            ph_number = request.POST['ph_number']
            password = request.POST['password']
            try:
                create_mem = User.objects.create_user(username=name, password=password)
                
                # print("=========3=============")
            except Exception as e:
                # print("=========4=============")
                error_message = f'Thi name already taken{e}'
                return render(request, 'Admin/CreateMember.html', {'error_message': error_message})
                 
            team_instance = get_object_or_404(Teams, pk=team_name)
            crnt_user = get_user_model()
            crnt_user1 = settings.AUTH_USER_MODEL
            user_pwd = crnt_user.objects.get(username=name)
            pwd_main = user_pwd.password
            user = Members.objects.create(
                    uname=name,
                    member_name= name,
                    team=team_instance,
                    designation=designation,
                    mobile=ph_number,
                    pwd= pwd_main
                )
            user.save()
            # print("=========5=============")
            
            
            success_message = f'Member has been created: {name}.'
            return render(request, 'Admin/CreateMember.html', {'success_message': success_message})
        except KeyError as e:
            error_message = f'Missing data: {e}.'
            return render(request, 'Admin/CreateMember.html', {'error_message': error_message})
        except ValueError as e:
            error_message = f'Invalid value: Enter valid value.'
            return render(request, 'Admin/CreateMember.html', {'error_message': error_message})
        except Http404:
            error_message = 'Team not found.'
            return render(request, 'Admin/CreateMember.html', {'error_message': error_message})
    else:
        teams = Teams.objects.values('id', 'T_name')
        return render(request, 'Admin/CreateMember.html', {'teams': teams})
    
    

@login_required(login_url='/')
def CreateTeam(request):
    if request.method == 'POST':
        t_name = request.POST.get('T_name')
        
        team_head_username = request.POST.get('team_head')
        password = request.POST.get('password')
        date = request.POST.get('date')

        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:           
            team_head = User.objects.get(username=team_head_username)
        except User.DoesNotExist:           
            try:
                team_head = User.objects.create_user(username=team_head_username, password=password)
            except Exception as e:
                error_message = 'Failed to create user. Please try again later. team_head'
                return render(request, 'app/CreateTeam.html', {'error_message': error_message})
        
        try:
            # print("===================")
            team = Teams.objects.create(
                T_name=t_name,
                
                team_head=team_head,
                date=date
            )
            # print("===================")
            team.save()
            success_message = 'Team has been created successfully.'
            return render(request, 'app/CreateTeam.html', {'success_message': success_message})
        except Exception as e:
            error_message = 'Failed to create team. Please try again later.'
            return render(request, 'app/CreateTeam.html', {'error_message': error_message})
    else:
        return render(request, 'app/CreateTeam.html')

@login_required()
def DropDownTeam(request):
    teams = Teams.objects.values('id', 'T_name')
    return render(request, 'app/CreateMember.html',{'teams':teams})


# @login_required()
# def EmployeeData(request, employee):
#     data = HighRiseData.objects.filter(HandledByEmployee=employee)
#     return render(request, 'Admin/UserData.html', {'data': data})

def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')        
        if username and password:      
        #     print('===========================1')
            user = authenticate(username=username, password=password)
            # request.session['username'] = username
            userna = list(Members.objects.filter(uname = username).values_list('member_name', flat=True))
            request.session['username'] = ', '.join(userna) 
            request.session['usern'] = username
            # print('=========', request.session.username)
            if user is not None and user.is_superuser and user.is_active:   
                #print('===========================2')
                login(request, user)
                return redirect('/admin/dashboard/')
            elif user is not None and user.is_staff and user.is_active:
                # print('==========================', user)
                teamIDs = list(Members.objects.filter(uname=user).values_list('team_id', flat=True)) 
                # print('==========================', teamIDs)
                team_name = list(Teams.objects.filter(id__in=teamIDs).values_list('T_name', flat=True)) 
                # print('==========================',team_name)
                if teamIDs:
                    request.session['teamIDs'] = teamIDs 
                    request.session['team_name'] = ', '.join(team_name)    
                    # request.session['username'] = username
                    
                login(request, user)
                return redirect('/admin/dashboard/')

            else:                                
                error_message = 'Invalid username or password.'
                return render(request, 'Admin/Login.html', {'error_message': error_message})
        else:            
            error_message = 'Please provide both username and password.'
            return render(request, 'Admin/Login.html', {'error_message': error_message})
    else:
        return render(request, 'Admin/Login.html')
    

@login_required(login_url='/')
def Dashboard(request):
   
    # teamIDs = list(Members.objects.filter(uname=User).values_list('team_id', flat=True))

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    endDate = request.GET.get('end_date')
    teamIDs = request.session.get('teamIDs', [])
    
    current_date = datetime.now().date().strftime("%Y-%m-%d")

    if teamIDs and start_date and end_date:    
        end_date =  datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1) 
        members = Members.objects.filter(team_id__in=teamIDs).values('member_name')
        if members.exists():
            for member in members:                
                bookings = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(Enquiry_Status='Booked') & Q(Enquiry_Conclusion_Date__range=(start_date, end_date)) ).count()
                new_leads = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(EDate__range=(start_date, end_date))).count()
                # new_leads = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(EDate__range=(start_date, end_date)) & Q(Enquiry_Status='Open')).count()
                total_leads = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(Enquiry_Status = 'Open')).count()
                site_visit = FollowUpData.objects.filter(Q(EnquiryStage='Site Visit - Done') & Q(Employee_Name=member['member_name']) & Q(FollowUp_Date__range =(start_date, end_date))).count()
                # home_visit = HomeVisit.objects.filter(Q(name=member['member_name']) & Q(date__range=(start_date, end_date))).count()
                solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__range=(start_date, end_date)) & Q(visit_type='solo')).count()  
                team_home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__range=(start_date, end_date)))
                team_home_visit_count = 0

                for visit in team_home_visits:
                    if visit.co_fellow: 
                        co_fellows = [name.strip() for name in visit.co_fellow.split(',')]
                        if member['member_name'] in co_fellows:
                            team_home_visit_count += 1
                home_visit = solo_home_visit + team_home_visit_count
                # home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__range=(start_date, end_date))).count()  
                # home_visit = FollowUpData.objects.filter(Q(EnquiryStage='Home Visit - Done') & Q(Employee_Name=member['member_name']) & Q(FollowUp_Date__range =(start_date, end_date))).count()
                corporate_visit = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_date__range = (start_date, end_date)) | Q(cofel_name__contains=member['member_name'])).count()
               
        
    elif teamIDs:
        members = Members.objects.filter(team_id__in=teamIDs).values('member_name')
        if members.exists():
            for member in members:                
                bookings = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(Enquiry_Status='Booked')).count()
                new_leads = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(EDate__date=current_date)).count()              
                # new_leads = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(EDate__date=current_date) & Q(Enquiry_Status='Open')).count()              
                total_leads = HighRiseData.objects.filter(Q(HandledByEmployee=member['member_name']) & Q(Enquiry_Status = 'Open')).count()
                site_visit = FollowUpData.objects.filter(Q(EnquiryStage='Site Visit - Done') & Q(Employee_Name=member['member_name'])).count()                
                # home_visit = FollowUpData.objects.filter(Q(EnquiryStage='Home Visit - Done') & Q(Employee_Name=member['member_name'])).count()
                # home_visit = HomeVisit.objects.filter(Q(name=member['member_name'])).count()
                solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(visit_type='solo')).count()  
                team_home_visits = HomeVisit.objects.filter(Q(visit_type='team'))
                team_home_visit_count = 0

                for visit in team_home_visits:
                    if visit.co_fellow:
                        co_fellows = [name.strip() for name in visit.co_fellow.split(',')]
                        if member['member_name'] in co_fellows:
                            team_home_visit_count += 1


                home_visit = solo_home_visit + team_home_visit_count
                corporate_visit = CorpFormData.objects.filter(Q(name=member['member_name']) | Q(cofel_name__contains=member['member_name'])).count()
               

    elif start_date and end_date:     
        end_date =  datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)  
        bookings = HighRiseData.objects.filter(Q(Enquiry_Conclusion_Date__range=(start_date, end_date)) & Q(Enquiry_Status='Booked')).count()
        # new_leads = HighRiseData.objects.filter(Q(EDate__range=(start_date, end_date)) &  Q(Enquiry_Status='Open')).count()
        new_leads = HighRiseData.objects.filter(Q(EDate__range=(start_date, end_date))).count()
        # total_leads = HighRiseData.objects.filter(Q(EDate__range=(start_date, end_date)) &  Q(Enquiry_Status='Open')).count()
        total_leads = HighRiseData.objects.filter(Enquiry_Status = 'Open').count()
        site_visit = FollowUpData.objects.filter(Q(EnquiryStage='Site Visit - Done') & Q(FollowUp_Date__range =(start_date, end_date))).count()

        corporate_visit = CorpFormData.objects.filter(visit_date__range=(start_date, end_date)).count()
        # solo_home_visit = HomeVisit.objects.filter(Q(date__range=(start_date, end_date))).count()  
        home_visit = HomeVisit.objects.filter(Q(date__range=(start_date, end_date))).count()

    else:
        site_visit = FollowUpData.objects.filter(Q(EnquiryStage='Site Visit - Done')).count()
        bookings = HighRiseData.objects.filter(Enquiry_Status='Booked').count()
        new_leads = HighRiseData.objects.filter(EDate__date=current_date).count()
        total_leads = HighRiseData.objects.filter(Enquiry_Status = 'Open').count()
        home_visit = HomeVisit.objects.filter().count()
        corporate_visit = CorpFormData.objects.all().count()
        # corporate_visit = CorpFormData.objects.filter(Q(visit_type='solo')).count()
   
    # print("========", new_leads, current_date)
    return render(request, 'Admin/dashboard.html', {'bookings': bookings, 'new_leads': new_leads,
                                                     'total_leads': total_leads, 'site_visit': site_visit,
                                                     'home_visit': home_visit, 'corporate_visit': corporate_visit, 'start_date':start_date,
                                                       'end_date':endDate})


def UserLogout(request):
    logout(request)
    return redirect('/') 


# @login_required(login_url='/admin/')
def Sign_in(request):
    if request.method == 'POST':
       
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role') 

        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        team = User.objects.create_user(
            username=name,
            password=password,
            email=email,
            is_superuser = role
        )
        success_message = 'Team has been created successfully.'
        return render(request, 'Admin/createUser.html', {'success_message': success_message})
    else:
        return render(request, 'Admin/createUser.html')
    






@login_required(login_url='/')
def UpdateData(request):
    error_message = None
    success_message = None
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        try:
            HighRiseData.objects.all().delete()
            df = pd.read_excel(excel_file)
            
            # Disable auto-commit
            with transaction.atomic():
                batch_size = 1000 
                rows_to_insert = []
                for _, row in df.iterrows():
                    highrise_data = HighRiseData()
                    for col_name, value in row.items():
                        if pd.isna(value):
                            setattr(highrise_data, col_name, None)
                        elif col_name == 'Enquiry Conclusion Date':
                            setattr(highrise_data, 'Enquiry_Conclusion_Date', timezone.make_aware(datetime.strptime(value, '%d %b %Y %H:%M:%S')))
                        elif col_name in ['FollowUp_Date', 'Next_FollowUp1', 'EDate', 'StageChangeDate']:
                            setattr(highrise_data, col_name, timezone.make_aware(datetime.strptime(value, '%d %b %Y %H:%M:%S')))
                        else:
                            setattr(highrise_data, col_name, value)
                    rows_to_insert.append(highrise_data)
                    
                    # Save in batches
                    if len(rows_to_insert) >= batch_size:
                        HighRiseData.objects.bulk_create(rows_to_insert)
                        rows_to_insert = []
                
                # Insert any remaining rows
                if rows_to_insert:
                    HighRiseData.objects.bulk_create(rows_to_insert)
                
            messages.success(request, 'Data Uploaded Successfully')
            return redirect('/admin/dashboard/')
        except FileNotFoundError:
            error_message = 'File not found. Please upload a valid Excel file.'
            # print('error_message',error_message)
            
        except pd.errors.ParserError:
            error_message = 'Error parsing Excel file. Please ensure the file format is correct.'
            # print('error_message',error_message)
        except Exception as e:
            error_message = f'Error: {str(e)}'
            # print('error_message',error_message)
    else:
        error_message = 'No file uploaded or invalid request method.'
    # print('error_message', message)
    return render(request, 'Admin/dashboard.html', {'error_message': error_message})



@login_required(login_url='/')
def FollowUploadData(request):
    error_message = None
    success_message = None
    
    if request.method == 'POST' and request.FILES.get('excel_file2'):
        excel_file = request.FILES['excel_file2']
        
        try:
            FollowUpData.objects.all().delete()
            df = pd.read_excel(excel_file)
            # print('=======')
            # Convert date and time columns to datetime objects
            date_time_columns = ['Edate', 'Next_FollowUp1', 'FollowUp_Date']
            for col_name in date_time_columns:
                # df[col_name] = pd.to_datetime(df[col_name], format='%d/%m/%Y %H:%M:%S').dt.tz_localize('UTC')
                # print(f'=====Original {col_name}=====')
                # print(df[col_name].head())  # Print first few rows for checking
                
                # Convert to datetime and then extract the date
                df[col_name] = pd.to_datetime(df[col_name], format='%m/%d/%Y %I:%M:%S %p').dt.date
                
                # Print the converted dates
                # print(f'=====Formatted {col_name}=====')
                # print(df[col_name].head())
                # df[col_name] = pd.to_datetime(df[col_name], format='%d/%m/%Y %H:%M:%S').dt.date
            
            # Disable auto-commit
            with transaction.atomic():
                batch_size = 1000 
                rows_to_insert = []
                for _, row in df.iterrows():
                    fw_data = FollowUpData()
                    for col_name, value in row.items():
                        if pd.isna(value):
                            setattr(fw_data, col_name, None)
                        else:
                            setattr(fw_data, col_name, value)
                    rows_to_insert.append(fw_data)
                    
                    # Save in batches
                    if len(rows_to_insert) >= batch_size:
                        FollowUpData.objects.bulk_create(rows_to_insert)
                        rows_to_insert = []
                
                # Insert any remaining rows
                if rows_to_insert:
                    FollowUpData.objects.bulk_create(rows_to_insert)
                
            messages.success(request, 'Data Uploaded Successfully')
            return redirect('/admin/dashboard/')
        except FileNotFoundError:
            error_message = 'File not found. Please upload a valid Excel file.'
        except pd.errors.ParserError:
            error_message = 'Error parsing Excel file. Please ensure the file format is correct.'
        except Exception as e:
            error_message = f'Error: {str(e)}'
    else:
        error_message = 'No file uploaded or invalid request method.'
        
    return render(request, 'Admin/dashboard.html', {'error_message': error_message})








# this function run when leadfunnel page render
@login_required(login_url='/')
def LeadFunnel(request):
    teams = Teams.objects.filter(status=1).values('id', 'T_name').order_by('T_name')
    members = Members.objects.filter(status=1).values('id', 'uname', 'member_name').order_by('member_name')
    
    return render(request, 'Admin/LeadFunnel.html', {'teams':teams, 'members':members})
    
 

@login_required(login_url='/')
def DailyPerReport(request):
  
    teams = Teams.objects.filter(status=1).values('id', 'T_name').order_by('T_name')
    members = Members.objects.filter(status=1).values('id', 'uname', 'member_name').order_by('member_name')
    return render(request, 'Admin/DailyPerReport.html', {'teams': teams, 'members': members})


@login_required(login_url='/')
def EmployeeData(request, employee):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    view = request.GET.get('view')  
    
    teamid = Members.objects.filter(member_name__contains=employee, status=1).values_list('team_id', flat=True)
    team = Teams.objects.filter(id__in=teamid, status=1).values()
    
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    current_month_number = datetime.now().strftime("%m")
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        # end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        end_date =  datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        previous_date = end_date - timedelta(days=1)
        previous_date_str = previous_date.strftime('%Y-%m-%d')
        total_sm_leads = HighRiseData.objects.filter(HandledByEmployee=employee, EDate__date__range=(start_date, end_date), Enquirytype__contains='Sage Mitra').count()
                          
        total_leads = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(FollowUp_Date__range=(start_date, end_date))).count()                        
        
        # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date)) & Q(visit_type='solo')).count()  
        # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__range=(start_date, end_date)) & Q(co_fellow__contains = employee)).count()
        # total_home_visits = solo_home_visit + home_visits
        solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date)) & Q(visit_type='solo')).count()  
        home_visits = HomeVisit.objects.filter(Q(date__range=(start_date, end_date)) & Q(visit_type='team'))
        team_home_visit_count = 0
        for visit in home_visits:
            if visit.co_fellow: 
                co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
                if employee in co_fellows:
                    team_home_visit_count += 1
        total_home_visits = solo_home_visit + team_home_visit_count
      
        total_1_site_visits = FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date), EnquiryStage__icontains='Site Visit - Done').count()
        hot_leads = HighRiseData.objects.filter(HandledByEmployee=employee, FollowUp_Date__range=(start_date, end_date), CustomerGrade='Hot', Enquiry_Status='Open').count()
        total_2_site_visits =  FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date), EnquiryStage__icontains='Site Visit - Revisit').count()
        missed_fw = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=previous_date_str)).count()
        SM_FW = Sagemitra.objects.filter(uname=employee, followUp_date__range=(start_date, end_date)).count()
       
        # corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__range = (start_date, end_date))).count()
        # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)) & Q(cofel_name__contains=employee)).count()
        # total_corpo_visits = corpo_solo + corporate
        corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__range = (start_date, end_date))).count()
        corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)))
        team_corporate_visit_count = 0
        for visit in corporate:        
            if visit.cofel_name: 
                co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
                if employee in co_fellows:
                    
                    team_corporate_visit_count += 1
        
        total_corpo_visits = corpo_solo + team_corporate_visit_count
                      
        data  = FollowUpData.objects.filter(Q(Employee_Name=employee) &  Q(FollowUp_Date__range=(start_date, end_date))).values()       
        emp_name = Members.objects.filter(member_name=employee).values_list('id')
        total_IP = IpData.objects.filter(name_id__in= emp_name, date__range= (start_date, end_date)).count()          
        total_admission  = AdmissionData.objects.filter(name_id__in= emp_name, date__range= (start_date, end_date)).count()          
        # print(total_leads)
        if view == 'Bookings':
            data = HighRiseData.objects.filter(HandledByEmployee=employee, Enquiry_Conclusion_Date__range=(start_date, end_date), Enquiry_Status='Booked').values()
            # print('==============',data)
        elif view == 'IP':
            data = IpData.objects.filter(name_id__in= emp_name, date__range=(start_date, end_date)).values()
        elif view == 'Admission':
            data = AdmissionData.objects.filter(name_id__in= emp_name, date__range=(start_date, end_date)).values()
        elif view == 'Home-Visit':
            data = HomeVisit.objects.filter(Q(Q(name=employee) | Q(co_fellow__contains=employee)) & Q(date__range=(start_date, end_date))).values()
        elif view == 'SM-Leads':
            data = HighRiseData.objects.filter(HandledByEmployee=employee, EDate__date__range=(start_date, end_date), Enquirytype='Sage Mitra').values()
        elif view == '1Site-Visits':
            data = FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date), EnquiryStage__icontains='Site Visit - Done').values()
        elif view == 'Hot-Leads':
            data = HighRiseData.objects.filter(HandledByEmployee=employee, FollowUp_Date__range=(start_date, end_date), CustomerGrade='Hot', Enquiry_Status='Open').values()
        elif view == '2Site-Visits':
            # data = HighRiseData.objects.filter(HandledByEmployee=employee, StageChangeDate__date__range=(start_date, end_date), EnquiryStage='Site Visit - Revisit').annotate()
            data = FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date), EnquiryStage__icontains='Site Visit - Revisit').values()
        elif view == 'Missed-FW':
            # data = HighRiseData.objects.filter(HandledByEmployee=employee, Next_FollowUp1__range=(start_date, end_date), Enquiry_Status='Open').values()
            data = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=previous_date_str)).values()
        elif view == 'SM-FW':
            data = Sagemitra.objects.filter(uname=employee, followUp_date__range=(start_date, end_date)).values()
        elif view == 'Corp-visits':
            # data = CorpFormData.objects.filter(name=employee, visit_date__range=(start_date, end_date)).values()   
            data = CorpFormData.objects.filter(Q(Q(name=employee) | Q(cofel_name__contains =employee)) &  Q(visit_date__range=(start_date, end_date))).values()   


    else:

        data =FollowUpData.objects.filter(Employee_Name=employee).values()      
        total_sm_leads = HighRiseData.objects.filter(HandledByEmployee=employee, Enquirytype__contains='Sage Mitra').count()
        # total_1_site_visits = HighRiseData.objects.filter(HandledByEmployee=employee, EnquiryStage='Site Visit - Done').count()
        total_1_site_visits = FollowUpData.objects.filter(Employee_Name=employee, EnquiryStage__icontains='Site Visit - Done').count()
        # total_leads = HighRiseData.objects.filter(HandledByEmployee=employee).filter(Enquiry_Status='Open').count()
        total_leads = FollowUpData.objects.filter(Employee_Name=employee).count()      
        total_bookings = HighRiseData.objects.filter(HandledByEmployee=employee, Enquiry_Status='Booked').count()

        # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(visit_type='solo') & Q(date__month=current_month_number)).count()  
        # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(co_fellow__contains = employee) & Q(date__month=current_month_number)).count()
        

        # total_home_visits = solo_home_visit + home_visits
        solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__month=(current_month_number)) & Q(visit_type='solo')).count()  
        home_visits = HomeVisit.objects.filter(Q(date__month=(current_month_number)) & Q(visit_type='team'))
        team_home_visit_count = 0
        for visit in home_visits:
            if visit.co_fellow: 
                co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
                if employee in co_fellows:
                    team_home_visit_count += 1
        total_home_visits = solo_home_visit + team_home_visit_count

        hot_leads = HighRiseData.objects.filter(HandledByEmployee=employee, CustomerGrade='Hot', Enquiry_Status='Open').count()
        # total_2_site_visits = HighRiseData.objects.filter(HandledByEmployee=employee, EnquiryStage='Site Visit - Revisit').count()
        total_2_site_visits = FollowUpData.objects.filter(Employee_Name=employee, EnquiryStage__icontains='Site Visit - REvisit').count()
        # missed_fw = HighRiseData.objects.filter(HandledByEmployee=employee, Next_FollowUp1__date=(current_date), Enquiry_Status='Open').count()
        missed_fw = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=yesterday_date_str)).count()
        SM_FW = Sagemitra.objects.filter(Q(uname=employee) & Q(followUp_date__month=current_month_number)).count()
       
        # corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__month = (current_month_number))).count()
        # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__month = (current_month_number)) & Q(cofel_name__contains=employee)).count()
        # total_corpo_visits = corpo_solo + corporate
        corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__month = (current_month_number))).count()
        corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__month = (current_month_number)))
        team_corporate_visit_count = 0
        for visit in corporate:        
            if visit.cofel_name: 
                co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
                if employee in co_fellows:
                    
                    team_corporate_visit_count += 1
        
        total_corpo_visits = corpo_solo + team_corporate_visit_count
        # print('========================', total_corpo_visits)
        emp_name = Members.objects.filter(member_name=employee).values_list('id')
        total_IP = IpData.objects.filter(Q(name_id__in= emp_name) & Q(date__month=current_month_number)).count()
        total_admission = AdmissionData.objects.filter(Q(name_id__in= emp_name) & Q(date__month=current_month_number)).count()
        
        # print('=================', employee)
        if view == 'Bookings':
            data = HighRiseData.objects.filter(HandledByEmployee=employee, Enquiry_Status='Booked').values()
        elif view == 'IP':
           
            data = IpData.objects.filter(Q(name_id__in= emp_name) & Q(date__month=current_month_number)).values()
        elif view == 'Admission':
        
            data = AdmissionData.objects.filter(Q(name_id__in= emp_name) & Q(date__month=current_month_number)).values()
        elif view == 'Home-Visit':
            data = HomeVisit.objects.filter(Q(Q(name=employee) | Q(co_fellow__contains=employee)) & Q(date__month=current_month_number)).values()
        elif view == 'SM-Leads':
            data = HighRiseData.objects.filter(HandledByEmployee=employee, Enquirytype__contains='Sage Mitra').values()
        elif view == '1Site-Visits':
            data = FollowUpData.objects.filter(Employee_Name=employee, EnquiryStage__icontains='Site Visit - Done').values()
        elif view == 'Hot-Leads':
            data = HighRiseData.objects.filter(HandledByEmployee=employee, CustomerGrade='Hot', Enquiry_Status='Open' ).values()
        elif view == '2Site-Visits':
            data = FollowUpData.objects.filter(Employee_Name=employee, EnquiryStage__icontains='Site Visit - Revisit').values()
        elif view == 'Missed-FW':
            # data = HighRiseData.objects.filter(HandledByEmployee=employee, Next_FollowUp1__date=(current_date), Enquiry_Status='Open').values()
            data = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=yesterday_date_str)).values()
        elif view == 'SM-FW':
            data = Sagemitra.objects.filter(Q(uname=employee) & Q(followUp_date__month=current_month_number)).values()
        elif view == 'Corp-visits':
            data = CorpFormData.objects.filter(Q(Q(name=employee) | Q(cofel_name__contains =employee)) & Q(visit_date__month=current_month_number)).values()   
          
    
    return render(request, 'Admin/UserData.html', {   'total_admission': total_admission,'total_IP':total_IP, 'total_corpo_visits': total_corpo_visits, 'SM_FW': SM_FW, 'missed_fw': missed_fw, 'total_2_site_visits': total_2_site_visits, 'hot_leads': hot_leads,
                                                   'view': view, 'team': team, 'start_date': start_date_str, 'end_date': end_date_str, 'data': data, 'name': employee,
                                                   'total_sm_leads': total_sm_leads, 'total_home_visits': total_home_visits,'total_leads': total_leads, 'total_1_site_visits': total_1_site_visits })





# def get_report_data(start_date=None, end_date=None, request=None):
#     teamIDs = request.session.get('teamIDs', [])
#     if teamIDs:
#         teams = Teams.objects.filter(status=1, id__in=teamIDs).values('id', 'T_name')
#     else:
#         teams = Teams.objects.filter(status=1).values('id', 'T_name')

#     # print(teams)
#     team_members = {}
#     team_sm_counts = {}
#     team_corp_counts = {}
#     current_month = datetime.now().strftime("%B")
#     current_month_number = datetime.now().strftime("%m")
#     # print('======current_month_number======', current_month_number)
#     current_date = datetime.now().date().strftime("%Y-%m-%d")
#     if start_date and end_date:
       
#         select_month_end = datetime.strptime(end_date, '%Y-%m-%d').strftime("%B") 
#         start_date = datetime.strptime(start_date, "%Y-%m-%d")
#         end_date =  datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
#         select_month = start_date.strftime("%B") 
        
      
#         # cuurent_date = datetime.no
#         # print(current_date)
#         # e_date =  datetime.strptime(end_date, '%Y-%m-%d') 
#         for team in teams:
#             members = Members.objects.filter(team_id=team['id'], status=1).values('id', 'member_name').order_by('member_name')
#             team_data = {}
#             team_sm_count = 0
#             team_corp_count = 0

#             for member in members:
#                 target_query = EmpSetTarget.objects.filter(Employee_id=member['id'], month=select_month)
#                 target_query_end = EmpSetTarget.objects.filter(Employee_id=member['id'], month=select_month_end)
#                 target_values = target_query.values('target', 'Target_id')
#                 target_values_end = target_query_end.values('target', 'Target_id')
#                 # print('=target_values==', target_values)

                
#                 print('=target_values_end==', target_values_end)
               
               
#                 # corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_type='solo') & Q(visit_date__range = (start_date, end_date))).count()
#                 # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)) & Q(cofel_name__contains=(member['member_name']))).count()
            
#                 # corp = corpo_solo + corporate
#                 corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_date__range = (start_date, end_date))).count()

#                 corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)))
#                 team_corporate_visit_count = 0
#                 for visit in corporate:        
#                     if visit.cofel_name: 
#                         co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
#                         if member['member_name'] in co_fellows:
                            
#                             team_corporate_visit_count += 1
                
#                 corp = corpo_solo + team_corporate_visit_count
#                 # print('=======================', corp)
#                 sm_sum = Sagemitra.objects.filter(uname=member['member_name'], followUp_date__range=(start_date, end_date)).count()
#                 high_rise_data = HighRiseData.objects.filter(HandledByEmployee=member['member_name'])            
               
#                 # solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__range=(start_date, end_date)) & Q(visit_type='solo')).count()  
#                 # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__range=(start_date, end_date)) & Q(co_fellow__contains = member['member_name'])).count()
#                 # Home_visit = solo_home_visit + home_visits
#                 solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__range=(start_date, end_date))).count()  
#                 home_visits = HomeVisit.objects.filter(Q(date__range=(start_date, end_date)) & Q(visit_type='team'))
#                 team_home_visit_count = 0
#                 for visit in home_visits:
#                     if visit.co_fellow: 
#                         co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
#                         if member['member_name'] in co_fellows:
#                             team_home_visit_count += 1
#                 Home_visit = solo_home_visit + team_home_visit_count
                
#                 followup = FollowUpData.objects.filter(Q(Employee_Name=member['member_name']) & Q(FollowUp_Date__range=(start_date, end_date))).count()
#                 emp_id = Members.objects.filter(member_name=member['member_name']).values_list('id')
#                 total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()    
#                 total_admission = AdmissionData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()                  
#                 total_event = EventAcc.objects.filter(Q(name = member['member_name']) & Q(start_date__range = (start_date, end_date))).count()       

#                 member_data = high_rise_data.aggregate(
#                     bookings=Count('Enquiry_Status', filter=Q(Enquiry_Status='Booked') & Q(Enquiry_Conclusion_Date__range=(start_date, end_date))),                    
#                     new_leads=Count('EDate', filter=Q(EDate__range=(start_date, end_date))),
#                 )
#                 member_data['corp_visits'] = corp
#                 member_data['total_event'] = total_event
#                 member_data['total_sm_leads'] = sm_sum
#                 member_data['customerfollowup'] = followup
#                 member_data['home_visit'] = Home_visit
#                 member_data['target_values'] = target_values
#                 member_data['total_ip'] = total_ip
#                 member_data['total_admission'] = total_admission
#                 team_sm_count += sm_sum
#                 team_corp_count += corp
                
#                 team_data[member['member_name']] = member_data

#             team_sm_counts[team['id']] = team_sm_count
#             team_corp_counts[team['id']] = team_corp_count
#             team_members[team['T_name']] = team_data

#         return teams, team_members, team_sm_counts, team_corp_counts
#     else:
#         # print('=======================')
#         for team in teams:
#             members = Members.objects.filter(team_id=team['id'], status=1).values('id', 'member_name').order_by('member_name')
#             team_data = {}
#             team_sm_count = 0
#             team_corp_count = 0
           

#             for member in members:
#                 target_query = EmpSetTarget.objects.filter(Employee_id=member['id'], month=current_month)
#                 target_values = target_query.values('target', 'Target_id')
                
#                 # corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_type='solo') & Q(visit_date__month = current_month_number)).count()
#                 # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(cofel_name__contains=(member['member_name'])) & Q(visit_date__month = current_month_number)).count()
#                 # corp = corpo_solo + corporate
#                 corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_type='solo') & Q(visit_date__month = (current_month_number))).count()

#                 corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__month = (current_month_number)))
#                 team_corporate_visit_count = 0
#                 for visit in corporate:        
#                     if visit.cofel_name: 
#                         co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
#                         if member['member_name'] in co_fellows:
                            
#                             team_corporate_visit_count += 1
                
#                 corp = corpo_solo + team_corporate_visit_count
#                 # print('==========corp========', corp, current_month_number)
                
#                 emp_id = Members.objects.filter(member_name=member['member_name']).values_list('id')
#                 total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__month=current_month_number)).count()    
#                 total_admission = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__month=current_month_number)).count()    
               
#                 sm_sum = Sagemitra.objects.filter(Q(uname=member['member_name']) & Q(followUp_date__month=(current_month_number))).count()
        
#                 # solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__month=current_month_number) & Q(visit_type='solo')).count()  
#                 # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__month=current_month_number) & Q(co_fellow__contains = member['member_name'])).count()
#                 # Home_visit = solo_home_visit + home_visits
#                 solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__month=(current_month_number)) & Q(visit_type='solo')).count()  
#                 home_visits = HomeVisit.objects.filter(Q(date__month=(current_month_number)) & Q(visit_type='team'))
#                 team_home_visit_count = 0
#                 for visit in home_visits:
#                     if visit.co_fellow: 
#                         co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
#                         if member['member_name'] in co_fellows:
#                             team_home_visit_count += 1
#                 Home_visit = solo_home_visit + team_home_visit_count
                
#                 total_event = EventAcc.objects.filter(Q(name = member['member_name']) & Q(start_date__month = (current_month_number))).count()
#                 high_rise_data = HighRiseData.objects.filter(HandledByEmployee=member['member_name'])                   
#                 followup = FollowUpData.objects.filter(Q(Employee_Name=member['member_name'])).count()          

#                 member_data = high_rise_data.aggregate(
#                     bookings=Count('Enquiry_Status', filter=Q(Enquiry_Status='Booked')),                    
#                     new_leads=Count('EDate', filter=Q(EDate__date=current_date)),
#                 )
#                 member_data['total_event'] = total_event
#                 member_data['corp_visits'] = corp
#                 member_data['total_sm_leads'] = sm_sum
#                 member_data['target_values'] = target_values
#                 member_data['customerfollowup'] = followup
#                 member_data['home_visit'] = Home_visit
#                 member_data['total_ip'] = total_ip
#                 member_data['total_admission'] = total_admission
                
#                 team_sm_count += sm_sum
#                 team_corp_count += corp

#                 team_data[member['member_name']] = member_data

#             team_sm_counts[team['id']] = team_sm_count
#             team_corp_counts[team['id']] = team_corp_count
#             team_members[team['T_name']] = team_data

#         return teams, team_members, team_sm_counts, team_corp_counts





def get_report_data(start_date=None, end_date=None, request=None):
    teamIDs = request.session.get('teamIDs', [])
    if teamIDs:
        teams = Teams.objects.filter(status=1, id__in=teamIDs).values('id', 'T_name')
    else:
        teams = Teams.objects.filter(status=1).values('id', 'T_name')

    # print(teams)
    team_members = {}
    team_sm_counts = {}
    team_corp_counts = {}
    current_month = datetime.now().strftime("%B")
    current_month_number = datetime.now().strftime("%m")
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    
    if start_date and end_date:

        target_values_end = []
       
        select_month_end = datetime.strptime(end_date, '%Y-%m-%d').strftime("%B") 
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date =  datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        select_month = start_date.strftime("%B") 
        for team in teams:
            members = Members.objects.filter(team_id=team['id'], status=1).values('id', 'member_name').order_by('member_name')
            team_data = {}
            team_sm_count = 0
            team_corp_count = 0

            for member in members:
                if select_month == select_month_end:
                    target_query = EmpSetTarget.objects.filter(Employee_id=member['id'], month=select_month)                
                    target_values_start = target_query.values('target', 'Target_id')
                    
                else:
                                       
                    target_query = EmpSetTarget.objects.filter(Employee_id=member['id'], month=select_month)                
                    target_values_start = target_query.values('target', 'Target_id')
                    target_query_end = EmpSetTarget.objects.filter(Employee_id=member['id'], month=select_month_end)
                    target_values_end = target_query_end.values('target', 'Target_id')

                corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_date__range = (start_date, end_date))).count()

                corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)))
                team_corporate_visit_count = 0
                for visit in corporate:        
                    if visit.cofel_name: 
                        co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
                        if member['member_name'] in co_fellows:
                            
                            team_corporate_visit_count += 1
                
                corp = corpo_solo + team_corporate_visit_count
                # print('=======================', corp)
                sm_sum = Sagemitra.objects.filter(uname=member['member_name'], followUp_date__range=(start_date, end_date)).count()
                high_rise_data = HighRiseData.objects.filter(HandledByEmployee=member['member_name'])            

                solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__range=(start_date, end_date))).count()  
                home_visits = HomeVisit.objects.filter(Q(date__range=(start_date, end_date)) & Q(visit_type='team'))
                team_home_visit_count = 0
                for visit in home_visits:
                    if visit.co_fellow: 
                        co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
                        if member['member_name'] in co_fellows:
                            team_home_visit_count += 1
                Home_visit = solo_home_visit + team_home_visit_count
                
                followup = FollowUpData.objects.filter(Q(Employee_Name=member['member_name']) & Q(FollowUp_Date__range=(start_date, end_date))).count()
                emp_id = Members.objects.filter(member_name=member['member_name']).values_list('id')
                total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()    
                total_admission = AdmissionData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()                  
                total_event = EventAcc.objects.filter(Q(name = member['member_name']) & Q(start_date__range = (start_date, end_date))).count()       

                member_data = high_rise_data.aggregate(
                    bookings=Count('Enquiry_Status', filter=Q(Enquiry_Status='Booked') & Q(Enquiry_Conclusion_Date__range=(start_date, end_date))),                    
                    new_leads=Count('EDate', filter=Q(EDate__range=(start_date, end_date))),
                )
                member_data['corp_visits'] = corp
                member_data['total_event'] = total_event
                member_data['total_sm_leads'] = sm_sum
                member_data['customerfollowup'] = followup
                member_data['home_visit'] = Home_visit
                member_data['target_values'] = target_values_start
               
                member_data['target_values_end'] = target_values_end
                member_data['total_ip'] = total_ip
                member_data['total_admission'] = total_admission
                team_sm_count += sm_sum
                team_corp_count += corp
                
                team_data[member['member_name']] = member_data

            team_sm_counts[team['id']] = team_sm_count
            team_corp_counts[team['id']] = team_corp_count
            team_members[team['T_name']] = team_data

        return teams, team_members, team_sm_counts, team_corp_counts
    else:
        # print('=======================')
        for team in teams:
            members = Members.objects.filter(team_id=team['id'], status=1).values('id', 'member_name').order_by('member_name')
            team_data = {}
            team_sm_count = 0
            team_corp_count = 0
           

            for member in members:
                target_query = EmpSetTarget.objects.filter(Employee_id=member['id'], month=current_month)
                target_values = target_query.values('target', 'Target_id')
                
                # corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_type='solo') & Q(visit_date__month = current_month_number)).count()
                # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(cofel_name__contains=(member['member_name'])) & Q(visit_date__month = current_month_number)).count()
                # corp = corpo_solo + corporate
                corpo_solo = CorpFormData.objects.filter(Q(name=member['member_name']) & Q(visit_type='solo') & Q(visit_date__month = (current_month_number))).count()

                corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__month = (current_month_number)))
                team_corporate_visit_count = 0
                for visit in corporate:        
                    if visit.cofel_name: 
                        co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
                        if member['member_name'] in co_fellows:
                            
                            team_corporate_visit_count += 1
                
                corp = corpo_solo + team_corporate_visit_count
                # print('==========corp========', corp, current_month_number)
                
                emp_id = Members.objects.filter(member_name=member['member_name']).values_list('id')
                total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__month=current_month_number)).count()    
                total_admission = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__month=current_month_number)).count()    
               
                sm_sum = Sagemitra.objects.filter(Q(uname=member['member_name']) & Q(followUp_date__month=(current_month_number))).count()
        
                # solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__month=current_month_number) & Q(visit_type='solo')).count()  
                # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__month=current_month_number) & Q(co_fellow__contains = member['member_name'])).count()
                # Home_visit = solo_home_visit + home_visits
                solo_home_visit = HomeVisit.objects.filter(Q(name = member['member_name']) & Q(date__month=(current_month_number)) & Q(visit_type='solo')).count()  
                home_visits = HomeVisit.objects.filter(Q(date__month=(current_month_number)) & Q(visit_type='team'))
                team_home_visit_count = 0
                for visit in home_visits:
                    if visit.co_fellow: 
                        co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
                        if member['member_name'] in co_fellows:
                            team_home_visit_count += 1
                Home_visit = solo_home_visit + team_home_visit_count
                
                total_event = EventAcc.objects.filter(Q(name = member['member_name']) & Q(start_date__month = (current_month_number))).count()
                high_rise_data = HighRiseData.objects.filter(HandledByEmployee=member['member_name'])                   
                followup = FollowUpData.objects.filter(Q(Employee_Name=member['member_name'])).count()          

                member_data = high_rise_data.aggregate(
                    bookings=Count('Enquiry_Status', filter=Q(Enquiry_Status='Booked')),                    
                    new_leads=Count('EDate', filter=Q(EDate__date=current_date)),
                )
                member_data['total_event'] = total_event
                member_data['corp_visits'] = corp
                member_data['total_sm_leads'] = sm_sum
                member_data['target_values'] = target_values
                member_data['customerfollowup'] = followup
                member_data['home_visit'] = Home_visit
                member_data['total_ip'] = total_ip
                member_data['total_admission'] = total_admission
                
                team_sm_count += sm_sum
                team_corp_count += corp

                team_data[member['member_name']] = member_data

            team_sm_counts[team['id']] = team_sm_count
            team_corp_counts[team['id']] = team_corp_count
            team_members[team['T_name']] = team_data

        return teams, team_members, team_sm_counts, team_corp_counts





@login_required(login_url='/')
def RPT_team_per(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    teams, team_members, team_sm_counts, team_corp_counts = get_report_data(start_date, end_date, request)
    return render(request, 'Admin/RPT-Team-Performance.html', {'team': teams, 'team_members': team_members, 'start_date':start_date , 'end_date':end_date})


@login_required(login_url='/')
def RPT_sm_corp(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    teams, team_members, team_sm_counts, team_corp_counts = get_report_data(start_date, end_date, request)
    return render(request, 'Admin/RPT-SM-Corp-FW.html', {'team_sm_counts':team_sm_counts,'team_corp_counts':team_corp_counts,'team': teams, 'team_members': team_members, 'start_date': start_date, 'end_date': end_date})


@login_required(login_url='/')
def RPT_funnel(request):
    teamIDs = request.session.get('teamIDs', [])
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    # print('======================', start_date)
    # print('======================', start_date)
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    follow = []
    data = []

    if start_date and end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        end_date__d = end_date + timedelta(days=1) - timedelta(seconds=1)
        previous_date = end_date__d - timedelta(days=1)
        previous_date_str = previous_date.strftime('%Y-%m-%d')
        if teamIDs:
            members = Members.objects.filter(status=1, team_id__in=teamIDs).order_by('member_name')
        else:
            members = Members.objects.filter(status=1).order_by('member_name')

        for member in members:
            missed_followUp = FollowUpData.objects.filter(
                Q(Employee_Name=member.member_name) & Q(Next_FollowUp1__date=previous_date_str)
            ).count()
            follow.append({'name': member.member_name, 'missed_followUp': missed_followUp})

            data.append(
                {
                    'HandledByEmployee': member.member_name,
                    'total_leads': HighRiseData.objects.filter(HandledByEmployee=member.member_name, Enquiry_Status='Open').count(),
                    'total_hot_leads': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Hot', FollowUp_Date__range=(start_date, end_date), Enquiry_Status='Open').count(),
                    'total_opportunity': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Opportunity', FollowUp_Date__range=(start_date, end_date), Enquiry_Status='Open').count(),
                    'total_proposal': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Proposal', FollowUp_Date__range=(start_date, end_date), Enquiry_Status='Open').count(),
                    'total_cold': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Cold', FollowUp_Date__range=(start_date, end_date), Enquiry_Status='Open').count(),
                    'total_closed': HighRiseData.objects.filter(HandledByEmployee=member.member_name, Enquiry_Status='Closed', Enquiry_Conclusion_Date__range=(start_date, end_date)).count(),
                    'total_bookings': HighRiseData.objects.filter(HandledByEmployee=member.member_name, Enquiry_Status='Booked', Enquiry_Conclusion_Date__range=(start_date, end_date)).count(),
                }
            )
        end_date = request.GET.get('end_date')
    else:
        previous_date = datetime.now() - timedelta(days=1)
        previous_date_str = previous_date.strftime('%Y-%m-%d')

        if teamIDs:
            members = Members.objects.filter(status=1, team_id__in=teamIDs).order_by('member_name')
        else:
            members = Members.objects.filter(status=1).order_by('member_name')
        for member in members:
            missed_followUp = FollowUpData.objects.filter(
                Q(Employee_Name=member.member_name) & Q(Next_FollowUp1__date=previous_date_str)
            ).count()
            follow.append({'name': member.member_name, 'missed_followUp': missed_followUp})

            data.append(
                {
                    'HandledByEmployee': member.member_name,
                    'total_leads': HighRiseData.objects.filter(HandledByEmployee=member.member_name, Enquiry_Status='Open').count(),
                    'total_hot_leads': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Hot', Enquiry_Status='Open').count(),
                    'total_opportunity': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Opportunity', Enquiry_Status='Open').count(),
                    'total_proposal': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Proposal', Enquiry_Status='Open').count(),
                    'total_cold': HighRiseData.objects.filter(HandledByEmployee=member.member_name, CustomerGrade='Cold', Enquiry_Status='Open').count(),
                    'total_closed': HighRiseData.objects.filter(HandledByEmployee=member.member_name, Enquiry_Status='Closed').count(),
                    'total_bookings': HighRiseData.objects.filter(HandledByEmployee=member.member_name, Enquiry_Status='Booked').count(),
                }
            )

    return render(request, 'Admin/RPT-Funnel.html', {'data': data, 'start_date': start_date, 'end_date': end_date, 'follow': follow})




@login_required(login_url='/')
def Target_assign(request):
    emp = Members.objects.filter(status=1).all().values('member_name', 'id', 'uname').order_by('member_name')
    target = Target.objects.filter(status=1).values('id', 'name').order_by('name')
    months = [calendar.month_name[i] for i in range(1, 13)]
    current_month = datetime.now().strftime("%B")
    teamIDs = request.session.get('teamIDs', [])

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        target_id = request.POST.get('target')
        year = request.POST.get('year')
        month = request.POST.get('month')
        target_value = request.POST.get('target_value')

        target_instance = Target.objects.get(id=target_id)
        
        obj = EmpSetTarget.objects.filter(Target=target_instance, Employee_id=employee_id, month=month).first()
        
        if obj:
           
            obj.target = target_value
            obj.year = year
            obj.month = month
            obj.save()
        else:            
            set_target = EmpSetTarget.objects.create(
                Employee_id=employee_id, 
                Target=target_instance,
                target=target_value,
                year=year,
                month=month
            )
            set_target.save()
        
        return redirect('/admin/Target-Assign/')
    if teamIDs:
        # print(teamIDs)
        emp_data = Members.objects.filter(status=1, team_id__in=teamIDs).values_list('member_name', 'id').order_by('member_name')
        emp = Members.objects.filter(status=1, team_id__in=teamIDs).all().values('member_name', 'id', 'uname').order_by('member_name')
    else: 
        emp_data = Members.objects.filter(status=1).values_list('member_name', 'id').order_by('member_name')
    
    target_data_list = []
    for member_tuple in emp_data:
        member_name = member_tuple[0]  
        member_id = member_tuple[1]
        target_data = EmpSetTarget.objects.filter(Employee_id=member_id, month=current_month).values('Target_id', 'target', 'month')
        target_data_list.append({'member_name': member_name, 'target_data': target_data})
    # print('=============', target_data_list)

    context = {'emp': emp, 'target': target, 'months': months, 'target_data_list': target_data_list}
    return render(request, 'Admin/TargetAssign.html', context)
    




# Lead Funnel section start 
def LF_Date_Range(emp, start_date, end_date, request):
    data = []
    teamIDs = request.session.get('teamIDs', [])
    if teamIDs:
        emp = Members.objects.filter(team_id__in=teamIDs, status=1).order_by('member_name').values_list('member_name', flat=True)
    end_d = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
    for employee in emp:
        first_site_visits = FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date),
                EnquiryStage='Site Visit - Done').count()
        second_site_visits = FollowUpData.objects.filter(Employee_Name=employee,  FollowUp_Date__range=(start_date, end_date),
                EnquiryStage='Site Visit - Revisit').count()
        high_rise_data = HighRiseData.objects.filter(HandledByEmployee=employee)                 
        employee_data = high_rise_data.aggregate(
                total_leads=Count('Enquiry_Status', filter=Q(Enquiry_Status='Open')),
                hot_leads=Count('FollowUp_Date', filter=Q(FollowUp_Date__range=(start_date, end_date)) & Q(CustomerGrade='Hot') & Q(Enquiry_Status='Open')),
                new_leads=Count('EDate', filter=Q(EDate__range=(start_date, end_date)))
            )
        employee_data['HandledByEmployee'] = employee
        employee_data['first_site_visits'] = first_site_visits
        employee_data['second_site_visits'] = second_site_visits

        data.append(employee_data)

        
    return data


def LF_Without_Date_Range(emp, request):
    teamIDs = request.session.get('teamIDs', [])
    if teamIDs:
        emp = Members.objects.filter(team_id__in=teamIDs, status=1).order_by('member_name').values_list('member_name', flat=True)
    
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    data = []
    for employee in emp:
        first_site_visits = FollowUpData.objects.filter(Employee_Name=employee, EnquiryStage='Site Visit - Done').count()
        second_site_visits = FollowUpData.objects.filter(Employee_Name=employee, EnquiryStage='Site Visit - Revisit').count()
        high_rise_data = HighRiseData.objects.filter(HandledByEmployee=employee)                 
        employee_data = high_rise_data.aggregate(
                total_leads=Count('Enquiry_Status', filter=Q(Enquiry_Status='Open')),
                hot_leads=Count('FollowUp_Date', filter=Q(CustomerGrade='Hot') & Q(Enquiry_Status='Open')),
                new_leads=Count('EDate', filter=Q(EDate__date=(current_date)))
            )
        employee_data['HandledByEmployee'] = employee
        employee_data['first_site_visits'] = first_site_visits
        employee_data['second_site_visits'] = second_site_visits

        data.append(employee_data)
        
    return data


def Filter(start_date=None, end_date=None, member=None, team=None, request=None):    
    emp = []
    members = None
    if start_date and end_date:
        if member and team:        
            # print('=======')             
            employee_queryset = Members.objects.filter(member_name=member, status=1)
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name',flat=True)

            if employee_queryset.exists():
                emp = [employee_queryset.first().member_name]
                leadfunnelData = LF_Date_Range(emp, start_date, end_date, request)

        elif member:
            employee_queryset = Members.objects.filter(member_name=member, status=1)
            members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name',flat=True)

            if employee_queryset.exists():
                emp = [employee_queryset.first().member_name]
                leadfunnelData = LF_Date_Range(emp, start_date, end_date, request)

        elif team  :
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name', flat=True)
            emp = list(members)
            leadfunnelData = LF_Date_Range(emp, start_date, end_date, request)
            
        else:           
            members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name', flat=True)
            emp = list(members)
            leadfunnelData = LF_Date_Range(emp, start_date, end_date, request)

    elif team or member:

        if member and team:
            # print('=======')
            # print(member, team,'=================')
            employee_queryset = Members.objects.filter(member_name=member, status=1)
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name',flat=True)

            if employee_queryset.exists():
                emp = [employee_queryset.first().member_name]
                leadfunnelData = LF_Without_Date_Range(emp, request)

        elif member:
            # print('======')
            employee_queryset = Members.objects.filter(member_name=member, status=1)
            members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name',flat=True)
            # print(employee_queryset)
            # print(members)
            if employee_queryset.exists():
                emp = [employee_queryset.first().member_name]
                leadfunnelData = LF_Without_Date_Range(emp, request)
        elif team:
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name', flat=True)
            emp = list(members)
            leadfunnelData = LF_Without_Date_Range(emp, request)

        else:           
            members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name', flat=True)
            emp = list(members)
            leadfunnelData = LF_Without_Date_Range(emp, request)

    else:
        
        members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name', flat=True)
        emp = list(members)
        leadfunnelData = LF_Without_Date_Range(emp, request)




    return leadfunnelData, members


def L_Funnel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    member = request.GET.get('member')
    team = request.GET.get('team')
    
    try:
        leadfunnelData, members = Filter(start_date, end_date, member, team, request) 
        leadfunnelData_list = list(leadfunnelData)
        # print(members)
        members_list = list(members)  
        return JsonResponse({'leadfunnelData': leadfunnelData_list, 'members': members_list}, safe=False)
    except Exception as e:
        # print(f"Error occurred: {e}")
        return JsonResponse({'error': str(e)}, status=500)


#=============== end of lead funnel ===============



# this section for DPR functions where we get request from user and filter data here with dates, members, teams
# this funtion run when user select the dates 

# def DPR_Date_Range(emp, start_date, end_date, request):
#     end_date_str = datetime.strptime(end_date, '%Y-%m-%d')
#     end_date_present = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
#     previous_date = end_date_str - timedelta(days=1)
#     previous_date_str = previous_date.strftime('%Y-%m-%d')
#     current_month = datetime.now().strftime("%B")
#     data = []

#     emp = list(emp)
#     # print('===emp===', emp)
#     teamIDs = request.session.get('teamIDs', [])
#     if teamIDs:
#         emp = Members.objects.filter(team_id__in=teamIDs, status=1).order_by('member_name').values_list('member_name', 'id')
#     for employee, employee_id  in emp:       

#         target = EmpSetTarget.objects.filter(Employee_id=employee_id, month=current_month).values('Target_id', 'target')
        
       
        
#         # corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__range = (start_date, end_date))).count()
#         # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)) & Q(cofel_name__contains=(employee))).count()
              
#         # corpo_visit = corpo_solo + corporate
#         corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_date__range = (start_date, end_date))).count()

#         corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)))
#         team_corporate_visit_count = 0
#         for visit in corporate:        
#             if visit.cofel_name: 
#                 co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
#                 if employee in co_fellows:
                    
#                     team_corporate_visit_count += 1
        
#         corpo_visit = corpo_solo + team_corporate_visit_count

#         sm_followup = Sagemitra.objects.filter(uname=employee, followUp_date__range=(start_date, end_date)).count()
#         lead_FW = FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date_str)).count()
#         missed_followUp = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=previous_date_str)).count()
#         # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date))).count()  
#         emp_id = Members.objects.filter(member_name=employee).values_list('id')
#         total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()    
#         total_admission = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()    
    
#         # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date)) & Q(visit_type='solo')).count()  
#         # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__range=(start_date, end_date)) & Q(co_fellow__contains = employee)).count()
#         # home_visit = solo_home_visit + home_visits
#         solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date))).count()  
#         home_visits = HomeVisit.objects.filter(Q(date__range=(start_date, end_date)) & Q(visit_type='team'))
#         team_home_visit_count = 0
#         for visit in home_visits:
#             if visit.co_fellow: 
#                 co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
#                 if employee in co_fellows:
#                     team_home_visit_count += 1
#         home_visit = solo_home_visit + team_home_visit_count
#         high_rise_data = HighRiseData.objects.filter(HandledByEmployee=employee)                 
#         employee_data = high_rise_data.aggregate(
#                 new_leads=Count('EDate', filter=Q(EDate__range=(start_date, end_date))),
#                 leadsSageMitra=Count('Enquirytype', filter=Q(Enquirytype__contains='Sage Mitra') & Q(EDate__range=(start_date, end_date)))
#             )
#         employee_data['HandledByEmployee'] = employee
#         employee_data['corpo_visit'] = corpo_visit
#         employee_data['total_ip'] = total_ip
#         employee_data['total_admission'] = total_admission
#         employee_data['home_visit'] = home_visit
#         employee_data['sm_followup'] = sm_followup
#         employee_data['lead_FW'] = lead_FW
#         employee_data['missed_followUp'] = missed_followUp
#         employee_data['target'] = list(target)

#         data.append(employee_data)
#     return data




def DPR_Date_Range(emp, start_date, end_date, request):
    end_date_str = datetime.strptime(end_date, '%Y-%m-%d')
    end_date_present = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
    previous_date = end_date_str - timedelta(days=1)
    previous_date_str = previous_date.strftime('%Y-%m-%d')
    # current_month = datetime.now().strftime("%B")
    data = []

    emp = list(emp)
    # print('===emp===', emp)
    teamIDs = request.session.get('teamIDs', [])
    select_month_end = datetime.strptime(end_date, '%Y-%m-%d').strftime("%B") 
    end_date =  datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    select_month = start_date.strftime("%B") 

    target_values_end = []
    if teamIDs:
        emp = Members.objects.filter(team_id__in=teamIDs, status=1).order_by('member_name').values_list('member_name', 'id')
    for employee, employee_id  in emp:       
        
       
        if select_month == select_month_end:                  
            target_query = EmpSetTarget.objects.filter(Employee_id=employee_id, month=select_month)          
            target = target_query.values('target', 'Target_id')
            
            # print(target)
        else:                          
            target_query = EmpSetTarget.objects.filter(Employee_id=employee_id, month=select_month) 
            target = target_query.values('target', 'Target_id')
            target_query_end = EmpSetTarget.objects.filter(Employee_id=employee_id, month=select_month_end)
            target_values_end = target_query_end.values('target', 'Target_id')
        
   
        # target = EmpSetTarget.objects.filter(Employee_id=employee_id, month=current_month).values('Target_id', 'target')
        
        
        
        # corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__range = (start_date, end_date))).count()
        # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)) & Q(cofel_name__contains=(employee))).count()
              
        # corpo_visit = corpo_solo + corporate
        corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_date__range = (start_date, end_date))).count()

        corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__range = (start_date, end_date)))
        team_corporate_visit_count = 0
        for visit in corporate:        
            if visit.cofel_name: 
                co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
                if employee in co_fellows:
                    
                    team_corporate_visit_count += 1
        
        corpo_visit = corpo_solo + team_corporate_visit_count
        # print('===================',previous_date_str)

        sm_followup = Sagemitra.objects.filter(uname=employee, followUp_date__range=(start_date, end_date)).count()
        lead_FW = FollowUpData.objects.filter(Employee_Name=employee, FollowUp_Date__range=(start_date, end_date_str)).count()
        missed_followUp = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=previous_date_str)).count()
        
        # print(missed_followUp)
        # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date))).count()  
        emp_id = Members.objects.filter(member_name=employee).values_list('id')
        total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()    
        total_admission = AdmissionData.objects.filter(Q(name_id__in=emp_id) & Q(date__range=(start_date, end_date))).count()    
    
        # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date)) & Q(visit_type='solo')).count()  
        # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__range=(start_date, end_date)) & Q(co_fellow__contains = employee)).count()
        # home_visit = solo_home_visit + home_visits
        solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__range=(start_date, end_date))).count()  
        home_visits = HomeVisit.objects.filter(Q(date__range=(start_date, end_date)) & Q(visit_type='team'))
        team_home_visit_count = 0
        for visit in home_visits:
            if visit.co_fellow: 
                co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
                if employee in co_fellows:
                    team_home_visit_count += 1
        home_visit = solo_home_visit + team_home_visit_count
        high_rise_data = HighRiseData.objects.filter(HandledByEmployee=employee)                 
        employee_data = high_rise_data.aggregate(
                new_leads=Count('EDate', filter=Q(EDate__range=(start_date, end_date))),
                leadsSageMitra=Count('Enquirytype', filter=Q(Enquirytype__contains='Sage Mitra') & Q(EDate__range=(start_date, end_date)))
            )
        employee_data['HandledByEmployee'] = employee
        employee_data['corpo_visit'] = corpo_visit
        employee_data['total_ip'] = total_ip
        employee_data['total_admission'] = total_admission
        employee_data['home_visit'] = home_visit
        employee_data['sm_followup'] = sm_followup
        employee_data['lead_FW'] = lead_FW
        employee_data['missed_followUp'] = missed_followUp
        employee_data['target'] = list(target)
        employee_data['target_values_end'] = list(target_values_end)

        data.append(employee_data)
    return data


# this function run when user want data with out dates

def DPR_Without_Date_Range(emp, request):
    current_date = datetime.now().date().strftime("%Y-%m-%d")
    yesterday_date = datetime.now() - timedelta(1)
    yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%B")
    current_month_number = datetime.now().strftime("%m")
    data = []
    # print('=================',list(emp))
    emp = list(emp)
    start_time = time.time()
    teamIDs = request.session.get('teamIDs', [])
    # print('===================================',emp)
    if teamIDs:
        emp = Members.objects.filter(team_id__in=teamIDs, status=1).order_by('member_name').values_list('member_name', 'id')
        member = Members.objects.filter(team_id__in=teamIDs, status=1).order_by('member_name').values_list('member_name', 'id')
    
    for employee, employee_id in emp:
        

        target = EmpSetTarget.objects.filter(Employee_id=employee_id, month=current_month).values('Target_id', 'target')

        # corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_type='solo') & Q(visit_date__month=current_month_number) ).count()
        # corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(cofel_name__contains=(employee)) & Q(visit_date__month=current_month_number)).count()
              

        # corpo_visit = corpo_solo + corporate
        # print('====================', corpo_visit)
        corpo_solo = CorpFormData.objects.filter(Q(name=employee) & Q(visit_date__month = (current_month_number))).count()

        corporate = CorpFormData.objects.filter(Q(visit_type='team') & Q(visit_date__month = (current_month_number)))
        team_corporate_visit_count = 0
        for visit in corporate:        
            if visit.cofel_name: 
                co_fellows = [name.strip() for name in visit.cofel_name.split(',')]                                
                if employee in co_fellows:
                    
                    team_corporate_visit_count += 1
        
        corpo_visit = corpo_solo + team_corporate_visit_count
        
        sm_followup = Sagemitra.objects.filter(Q(uname=employee) & Q(followUp_date__month=(current_month_number))).count()
        lead_FW = FollowUpData.objects.filter(Employee_Name=employee).count()
        missed_followUp = FollowUpData.objects.filter(Q(Employee_Name=employee) & Q(Next_FollowUp1__date=yesterday_date_str)).count()
      
        # solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__month=(current_month_number)) & Q(visit_type='solo')).count()  
        # home_visits = HomeVisit.objects.filter(Q(visit_type='team') & Q(date__month=(current_month_number)) & Q(co_fellow__contains = employee)).count()
        # home_visit = solo_home_visit + home_visits
        solo_home_visit = HomeVisit.objects.filter(Q(name = employee) & Q(date__month=(current_month_number))).count()  
        home_visits = HomeVisit.objects.filter(Q(date__month=(current_month_number)) & Q(visit_type='team'))
        team_home_visit_count = 0
        for visit in home_visits:
            if visit.co_fellow: 
                co_fellows = [name.strip() for name in visit.co_fellow.split(',')]                        
                if employee in co_fellows:
                    team_home_visit_count += 1
        home_visit = solo_home_visit + team_home_visit_count
        
        emp_id = Members.objects.filter(member_name=employee).values_list('id')
        total_ip = IpData.objects.filter(Q(name_id__in=emp_id) & Q(date__month=current_month_number)).count()    
        total_admission = AdmissionData.objects.filter(Q(name_id__in=emp_id) & Q(date__month=current_month_number)).count()    
   
        
        # employee_data = HighRiseData.objects.filter(HandledByEmployee=employee).values('HandledByEmployee').order_by('HandledByEmployee').annotate(
        #     booked_count=Sum(Case(When(Q(Enquiry_Status='Booked'), then=1), default=0, output_field=IntegerField())),           
        #     new_leads=Sum(Case(When(EDate__date=current_date, then=1), default=0, output_field=IntegerField())),
        #     leadsSageMitra=Sum(Case(When(Enquirytype__contains='Sage Mitra', then=1), default=0, output_field=IntegerField())),
        # )
        high_rise_data = HighRiseData.objects.filter(HandledByEmployee=employee)                 
        employee_data = high_rise_data.aggregate(
                new_leads=Count('EDate', filter=Q(EDate__date=current_date)),
                leadsSageMitra=Count('Enquirytype', filter=Q(Enquirytype__contains='Sage Mitra'))
            )
        employee_data['HandledByEmployee'] = employee
        employee_data['corpo_visit'] = corpo_visit
        employee_data['total_ip'] = total_ip
        employee_data['total_admission'] = total_admission
        employee_data['home_visit'] = home_visit
        employee_data['sm_followup'] = sm_followup
        employee_data['lead_FW'] = lead_FW
        employee_data['missed_followUp'] = missed_followUp
        employee_data['target'] = list(target)

        data.append(employee_data)
    
    
    # end_time = time.time()  
    # query_time = end_time - start_time  
    
    # print('======================')
    # print("Query Time:", query_time)
    return data


def DPR_Filter(start_date=None, end_date=None, member=None, team=None, request=None):    
    emp = []
    members = None
    if start_date and end_date:
        # print('========', start_date, end_date)
        if member and team:            
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name','id')
            mem = Members.objects.filter(member_name=member, status=1)
            emp = list(mem.values_list('member_name','id'))
            DPR_data = DPR_Date_Range(emp, start_date, end_date, request)

        elif member:            
            mem = Members.objects.filter(member_name=member, status=1)
            members = list(mem.values_list('member_name','id'))
            if mem.exists():              
                # emp = [mem.first().member_name]             
                # print('===========',emp)   
                DPR_data = DPR_Date_Range(emp, start_date, end_date, request)


        elif team:
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name','id')
            emp = list(members)
            DPR_data = DPR_Date_Range(emp, start_date, end_date, request)
            


        else:           
            members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name','id')
            emp = list(members)                           
            DPR_data = DPR_Date_Range(emp, start_date, end_date, request)



    elif team or member:
        if member and team:            
            # print('============', member, team)
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name','id')
            mem = Members.objects.filter(member_name=member, status=1)
            emp = list(mem.values_list('member_name','id'))
            DPR_data = DPR_Without_Date_Range(emp, request)

        elif member:
            mem = Members.objects.filter(member_name=member, status=1)
            members = list(mem.values_list('member_name','id'))

            if mem.exists():               
                # emp = [mem.first().member_name]
                emp = members
                # print('===========',emp)   
                DPR_data = DPR_Without_Date_Range(emp, request)

        elif team:
            members = Members.objects.filter(team_id=team, status=1).order_by('member_name').values_list('member_name','id')
            emp = list(members)
            DPR_data = DPR_Without_Date_Range(emp, request)

        else:           
            members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name','id')
            emp = list(members)
            DPR_data = DPR_Without_Date_Range(emp, request)

    else:       
        members = Members.objects.filter(status=1).order_by('member_name').values_list('member_name','id')
        emp = list(members)
        DPR_data = DPR_Without_Date_Range(emp, request)

    return DPR_data, members  



def DPR(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    member = request.GET.get('member')
    team = request.GET.get('team')
   
   
    DPR_data, members = DPR_Filter(start_date, end_date, member, team, request)
    DPR_data = list(DPR_data)
    members = list(members)
    return JsonResponse({'DPRData': DPR_data, 'members': members}, safe=False)
   





#=====end====DPR===section====== 
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def Delete_Record(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            view = data.get('view')

            
            if item_id and view == 'Corp-visits':
                
                CorpFormData.objects.filter(id=item_id).delete()
                return JsonResponse({'message': 'Record deleted successfully', 'view': view})
            
            elif item_id and view == 'Home-Visit':    
                HomeVisit.objects.filter(id=item_id).delete()
                return JsonResponse({'message': 'Record deleted successfully', 'view': view})
            
            elif item_id and view == 'SM-FW':                
                Sagemitra.objects.filter(id=item_id).delete()
                return JsonResponse({'message': 'Record deleted successfully', 'view': view})
            
            elif item_id and view == 'Admission':                
                AdmissionData.objects.filter(id=item_id).delete()
                return JsonResponse({'message': 'Record deleted successfully', 'view': view})
            
            elif item_id and view == 'IP':                
                IpData.objects.filter(id=item_id).delete()
                return JsonResponse({'message': 'Record deleted successfully', 'view': view})
            
            else:
                return JsonResponse({'message': 'Item ID not provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'message': 'Invalid request'}, status=400)





def Employee_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        u_id = request.POST.get('u_id')
        emp_status = request.POST.get('emp_status')
        username = request.POST.get('username')
        email = request.POST.get('email')
        teamid = request.POST.get('team')
        ph_number = request.POST.get('ph_number')
        password = request.POST.get('password')
        Emp_name = request.POST.get('Emp_name')
        team_id = request.POST.get('team_id')
        

        if user_id and emp_status:

            member = Members.objects.get(id=user_id)
            member.status = emp_status
            member.save()

            user = User.objects.get(username=member.uname)
            user.is_active = True if emp_status == '1' else False
            user.save()

        elif username and email and ph_number and password:
         
            user = User.objects.create_user(username=username, email=email, password=password, is_active=True, first_name=Emp_name)
            member = Members.objects.create(uname=username, member_name=Emp_name, email=email, team_id=teamid, mobile=ph_number, status=1 )
            member.save()

        elif u_id and team_id:
            member = Members.objects.get(id=u_id)
            member.team_id = team_id
            member.save()
        
        return redirect('Employee_status')

    employee = Members.objects.all().order_by('member_name').values()
    team = Teams.objects.all().order_by('T_name').values()
    return render(request, 'Admin/Employee_status.html', {'employee': employee, 'team': team})