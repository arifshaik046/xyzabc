from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.response import Response
from django.core.mail import send_mail
from .serializers import QueryDataSerializer
from rest_framework.decorators import api_view
import csv
import openpyxl
# from django.core.files.uploadhandler import TemporaryFileUploadHandler
import random
from django.http import JsonResponse
import pandas as pd  # For parsing Excel files
from .models import UploadedFile,ParsedData
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Func, F, Value, CharField,Q
from .forms import CustomUserCreationForm, CustomAuthenticationForm,UploadFileForm



# @login_required
def profile(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('/')
@api_view(['GET'])
def result_view(request):
    # Extract query parameters from the URL
    country = request.GET.get('country')
    print(country)
    year_founded = request.GET.get('yearFounded')
    print(year_founded)
    state = request.GET.get('state')
    print(state)
    industry = request.GET.get('industry')
    print(industry)
    employee_from = request.GET.get('employeeFrom')
    print(employee_from)
    employee_to = request.GET.get('employeeTo')
    print(employee_to)
    city = request.GET.get('city')
    print(city)
    data = {
        'country': country,
        'year_founded': year_founded,
        'state': state,
        'industry': industry,
        'employee_from': employee_from,
        'employee_to': employee_to,
        'city':city
    }
    serializer = QueryDataSerializer(data=data)
    print(serializer.is_valid())
    if serializer.is_valid():
        data = serializer.validated_data

        country = data['country']
        year_founded = data['year_founded']
        state = data['state']
        industry = data['industry']
        employee_from = data['employee_from']
        employee_to = data['employee_to']
        city = data['city']
        locality_value = f'{city},{state},{country}'
        print(locality_value)

        # Query to filter and count matching records
        count = ParsedData.objects.filter(Q(locality__startswith=f"{city}, {state}"),
            Q(country=country),# Filter by city and state in locality
            Q(year_founded=year_founded),
            Q(industry=industry),
            Q(current_employee_estimate=(employee_from)),
            Q(total_employee_estimate=(employee_to))  # Range condition
        ).count()
        print('----------',count)

        return Response({'count': count})

    return Response(serializer.errors, status=400)


def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            confirmation_code = ''.join(random.choices('0123456789', k=6))

            # Send confirmation email
            send_mail(
                'Confirmation Email',
                f'Hi \n\nThank you for signing up!\n\nYour confirmation code is: {confirmation_code}\n\nBest regards,\nYour Website Team',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            # Store confirmation code in session
            request.session['confirmation_code'] = confirmation_code
            request.session['email'] = email
            return render(request, 'confirmation.html', {'form': form})
        else:
            return HttpResponse('<script>alert("Invalid Details.");window.location.href = "/";</script>')

    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# views.py
# views.py (adjusted for error handling)
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request=request, data=request.POST)
        print(f"Form valid: {form.is_valid()}")
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(f"Email: {email}, Password: {password}")
            user = authenticate(request, email=email, password=password)
            print(f"User: {user}")
            if user is not None:
                login(request, user)
                return redirect('upload')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Invalid email or password')
            print("Form errors:", form.errors)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})



# @method_decorator(csrf_protect)
# @method_decorator(csrf_/exempt)
# Create your views here.
# def confirmation(request):
#     if request.method == 'POST':
#         user_confirmation_code = request.POST['confirmation_code']
#         session_keys = list(request.session.keys())
#         print(session_keys)
#         if user_confirmation_code == request.session['confirmation_code']:
#             request.session.clear()
#             return HttpResponse('<script>alert("Sign up successful!"); window.location.href = "/";</script>')
#         else:
#             messages.error(request, 'Invalid confirmation code. Please try again.')
#             return redirect('confirmation')
#     return render(request, 'confirmation.html')

def submit(request):
    if request.method == 'POST':
        user_confirmation_code = request.POST['confirmation_code']
        session_keys = list(request.session.keys())
        print(session_keys)
        if user_confirmation_code == request.session['confirmation_code']:
            request.session.clear()
            # return redirect('login')
            return HttpResponse('<script>alert("Sign up successful!"); window.location.href = "/";</script>')
        else:
            messages.error(request, 'Invalid confirmation code. Please try again.')
            return redirect('confirmation')
    return render(request, 'confirmation.html')

@login_required
def upload_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the file and save parsed data
            if request.FILES['file'].name.endswith('.csv'):
                process_csv(request.FILES['file'])
            elif request.FILES['file'].name.endswith('.xlsx'):
                process_xlsx(request.FILES['file'])

            else:
                return HttpResponse('<script>alert("Invalid File Format"); window.location.href = "/";</script>')

            HttpResponse('File uploaded successfully')
            return render(request, 'filter.html')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def process_csv(file):
    # Check if the ParsedData table is empty
    if not ParsedData.objects.exists():
        # Create a generator to yield lines from the file one by one
        reader = csv.DictReader((line.decode('utf-8') for line in file))
        bulk_data = []
        for row in reader:
            # Check for empty strings before converting to float
            year_founded = int(float(row.get('year founded', 0))) if row.get('year founded', '') else 0
            current_employee_estimate = int(row.get('current employee estimate', 0)) if row.get(
                'current employee estimate', '') else 0
            total_employee_estimate = int(row.get('total employee estimate', 0)) if row.get('total employee estimate',
                                                                                            '') else 0

            bulk_data.append(ParsedData(
                name=row.get('name', ''),
                domain=row.get('domain', ''),
                year_founded=year_founded,
                industry=row.get('industry', ''),
                size_range=row.get('size range', ''),
                locality=row.get('locality', ''),
                country=row.get('country', ''),
                linkedin_url=row.get('linkedin url', ''),
                current_employee_estimate=current_employee_estimate,
                total_employee_estimate=total_employee_estimate
            ))
            # Batch insert records every 1000 rows
            if len(bulk_data) >= 1000:
                ParsedData.objects.bulk_create(bulk_data)
                bulk_data = []
        # Insert remaining records
        if bulk_data:
            ParsedData.objects.bulk_create(bulk_data)
    else:
        # Delete existing data in the ParsedData table
        ParsedData.objects.all().delete()

        # Process and insert data from the uploaded file
        file.seek(0)  # Reset file pointer to beginning
        process_csv(file)


def process_xlsx(file):
    # Check if the ParsedData table is empty
    if not ParsedData.objects.exists():
        # Load the workbook
        workbook = openpyxl.load_workbook(file, read_only=True, data_only=True)
        sheet = workbook.active
        bulk_data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Convert empty strings to 0 before converting to int
            year_founded = int(float(row[2])) if row[2] else 0
            current_employee_estimate = int(row[8]) if row[8] else 0
            total_employee_estimate = int(row[9]) if row[9] else 0

            bulk_data.append(ParsedData(
                name=row[0],
                domain=row[1],
                year_founded=year_founded,
                industry=row[3],
                size_range=row[4],
                locality=row[5],
                country=row[6],
                linkedin_url=row[7],
                current_employee_estimate=current_employee_estimate,
                total_employee_estimate=total_employee_estimate
            ))
            # Batch insert records every 1000 rows
            if len(bulk_data) >= 1000:
                ParsedData.objects.bulk_create(bulk_data)
                bulk_data = []
        # Insert remaining records
        if bulk_data:
            ParsedData.objects.bulk_create(bulk_data)
    else:
        # Delete existing data in the ParsedData table
        ParsedData.objects.all().delete()

        # Process and insert data from the uploaded file
        file.seek(0)  # Reset file pointer to beginning
        process_xlsx(file)



class SplitPart(Func):
    function = 'split_part'
    template = "%(function)s(%(expressions)s)"
    output_field = CharField()

def get_country(request):
    country = ParsedData.objects.values_list('country', flat=True).distinct()
    print(country)
    return JsonResponse(list(country), safe=False)

def get_states(request):
    country = request.GET.get('country', None)
    print('----',country)
    if country:
        states=ParsedData.objects.filter(country=country).annotate(
            first_value=SplitPart('locality', Value(','), Value(2))
        ).values_list('first_value', flat=True).distinct()
        print(list(states),type(states))
        return JsonResponse(list(states), safe=False)
    return JsonResponse([], safe=False)

def get_industries(request):
    industries = ParsedData.objects.values_list('industry', flat=True).distinct()
    return JsonResponse(list(industries), safe=False)

def get_cities(request):
    state_name = request.GET.get('state', None)
    print(state_name)
    if state_name:
        annotated_queryset = ParsedData.objects.annotate(
            second_value=SplitPart('locality', Value(','), Value(1)),
            state_value=SplitPart('locality', Value(','), Value(2))
        )

        # Filter by the annotated field
        filtered_queryset = annotated_queryset.filter(state_value=state_name).values_list('second_value',
                                                                                          flat=True).distinct()

        cities_list = list(filtered_queryset)
        print(cities_list, type(cities_list))
        return JsonResponse(cities_list, safe=False)
    return JsonResponse([], safe=False)