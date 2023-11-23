from django.shortcuts import render, redirect, HttpResponseRedirect
import requests
import random
from .utils import send_email_to_client
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import student_profile
from .models import faculty_profile
from .models import Course, Assignment, Submission, Announcements, Material, feedback, query
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.db.models import Q

def home(request):
    if request.user.is_authenticated:
        return redirect('/mycourse')
    return render(request , 'land.html')

def admindashboard(request):
    return render(request , 'admin_dashboard.html')

def students_profile(request):
    try:
        prof = faculty_profile.objects.get(user=request.user)
        return redirect('/mycourse')
    except:
        student = student_profile.objects.get(user=request.user)
        context = {
            'student':student
        }
        return render(request , 'student_profile.html', context)

def actions_student(request):
    return render(request , 'actions_student.html')

def actions(request):
    return render(request , 'actions.html')

def materials(request,course_id):
    isprof = True
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        isprof = False
    course = Course.objects.get(course_code=course_id)
    material = Material.objects.filter(course=course)
    context = {
        'material':material,
        'course':course,
        'isprof':isprof
    }
    return render(request , 'materials.html', context)

def addmaterial(request,course_id):
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        messages.error(request, "You cannot Post Material here.")
        return redirect('/mycourse/'+course_id+'/materials')
    if request.method == "POST":
        course = Course.objects.get(course_code=course_id)
        title = request.POST.get('title')
        desc = request.POST.get('description')
        file = request.POST.get('file')
        material_files = Material.objects.create(title=title,description=desc, course=course, material_file=file)
        material_files.save()
        return redirect('/mycourse/'+course_id+"/materials")
    else:
        course = Course.objects.get(course_code=course_id)
        context = {
            'course':course
        }
        return render(request , 'add_material.html', context)

def announcements(request , course_id):
    isprof = True
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        isprof = False
    course = Course.objects.get(course_code=course_id)
    announce = Announcements.objects.filter(course=course)
    context = {
        "course":course,
        "announce":announce,
        'isprof':isprof
    }
    return render(request , 'announcements.html', context)

def addannouncement(request,course_id):
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        messages.error(request, "You cannot Post Material here.")
        return redirect('/mycourse/'+course_id+'/materials')
    if request.method == "POST":
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        course = Course.objects.get(course_code=course_id)
        my_announce = Announcements.objects.create(title=title, description=desc, course=course, user=request.user)
        my_announce.save()
        return redirect('/mycourse/'+course_id)
    else:
        course = Course.objects.get(course_code=course_id)
        context = {
            "course":course
        }
        return render(request , 'add_announcement.html', context)

def fb_response(request, course_id):
    course = Course.objects.get(course_code=course_id)
    try:
        prof = faculty_profile.objects.get(user=request.user)
        fb = feedback.objects.filter(course=course)
        isprof = True
        context = {
            'prof':prof,
            'feedback':fb,
            'isprof':isprof,
            'course':course
        }
        return render(request, 'feedback_faculty.html', context)
    except:
        try:
            fb = feedback.objects.get(user=request.user, course=course)
            messages.error(request, "You have already given the feedback")
            return redirect('/mycourse/'+course_id)
        except:
            if request.method == "POST":
                details = request.POST.get('feedback')
                fb = feedback.objects.create(fb=details, user=request.user,course=course)
                fb.save()
                return redirect('/mycourse/'+course_id)
            else:
                context = {
                    'course':course
                }
                return render(request , 'feedback_student.html',context)

def login_func(request, loginid):
    if request.user.is_authenticated:
        return redirect('/mycourse')

    if request.method == "POST":
        username = request.POST.get('user')
        passwrd = request.POST.get('pass1')
        user = authenticate(request , username=username, password=passwrd)
        if user is None:
            messages.warning(request, "Please Enter the correct Credentials.")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        if loginid == "faculty":
            try:
                faculty = faculty_profile.objects.get(user=user)
                login(request, user)
                return redirect('/mycourse')
            except:
                messages.warning(request, "Please Enter the correct Credentials.")
                return redirect('/login/faculty')
        elif loginid == "student":
            try:
                student = student_profile.objects.get(user=user)
                login(request, user)
                return redirect('/mycourse')
            except:
                messages.warning(request, "Please Enter the correct Credentials.")
                return redirect('/login/student')
    else:
        if loginid == "student":
            return render(request , 'login_page_student.html')
        else:
            return render(request , 'login_page_admin.html')
        
def register(request):
    if request.user.is_authenticated:
        return redirect('/mycourse')

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST.get('pass1')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        batch = request.POST.get('batch')
        branch = request.POST.get('branch')
        program = request.POST.get('program')
        code = random.randint(1000,9999)
        request.session['code'] = code
        request.session['password'] = password
        send_email_to_client(email, code)
        dict = {'email':email,'password':password,'first_name':first_name,'middle_name':middle_name,'last_name':last_name,'batch':batch,'branch':branch,'program':program }
        return render(request,'otp_ver.html',dict)
    else:
        return redirect('/')

def verifyRegistration(request):
    if request.user.is_authenticated:
        return redirect('/mycourse')

    if request.method == "POST":
        code = request.session.get('code', None)
        email = request.POST['email']
        password = request.session.get('password', None)
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        batch = request.POST.get('batch')
        branch = request.POST.get('branch')
        program = request.POST.get('program')
        code = str(code)
        ver_code = request.POST.get('ver_code')
        print(email)
        print(password)
        if User.objects.filter(email=email).exists():
            messages.warning(request, "Enter correct Email")
            return redirect('/register')
        if code == ver_code:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.set_password(password)
            my_profile = student_profile.objects.create(user=user, first_name=first_name, middle_name=middle_name, last_name=last_name, batch=batch, branch=branch, program=program)
            my_profile.save()
            user = authenticate(request, username=email, password=password)
            login(request,user)
            return redirect('/mycourse')
        else:
            messages.error("PLEASE ENTER CORRECT OTP")
            return render(request,'register.html')
    else:
        return redirect('/')

def addcourse(request):
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        messages.error(request, "You are not authorized to add a Course")
        return redirect('/mycourse')
    if(request.method == 'POST'):
        course_name = request.POST.get('coursename')
        courseid = request.POST.get('courseid')
        description = request.POST.get('description')
        prof = faculty_profile.objects.get(user=request.user)
        if not Course.objects.filter(course_code = courseid).exists():
            my_course = Course.objects.create(name = course_name , course_code = courseid , description = description , faculty = prof)
            my_course.save()
        return redirect('/mycourse')
    

    return render(request , 'addcourse.html')

def edit_course(request, course_id):
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        messages.error(request, "You are not authorized to edit a Course")
        return redirect('/mycourse')
    if(request.method == 'POST'):
        editcourse = Course.objects.get(course_code = course_id)
        editcourse.name = request.POST.get('coursename')
        editcourse.course_code = request.POST.get('courseid')
        editcourse.description = request.POST.get('description')
        editcourse.save()
    else:
        editcourse = Course.objects.get(course_code = course_id)
        params = {'record' : editcourse}
        return render(request, 'editcourse.html', params)
    return redirect('mycourse')

def student_list(request , course_id):
    isprof = True
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        isprof = False
    current_course = Course.objects.get(course_code = course_id)
    students = current_course.studentlist.all()

    context = {
        "students":students,
        "course":current_course,
        'isprof':isprof
    }

    return render(request , 'student_list.html' , context)

def view_profile(request, course_id, id):
    student = student_profile.objects.get(id = id)
    current_course = Course.objects.get(course_code = course_id)
    context = {'student':student, 'course':current_course}
    return render(request , 'view_other_student_profile.html', context)

def students_assignment(request , course_id , student):

    course = Course.objects.get(course_code=course_id)
    assign = Assignment.objects.filter(assignment_course=course).all()

    thisstudent = student_profile.objects.get(first_name = student)
    print(thisstudent)
    
    submitlist = []
    for a in assign :
        if(Submission.objects.filter(assignment = a , student = thisstudent).exists()):
            submitlist.append(Submission.objects.get(assignment = a , student = thisstudent))

    context = {
        "submission":submitlist
    }
    return render(request , 'students_assignment.html' , context)

def add_course_to_user(request, course_id):
    try:
        current_user = request.user
        print(current_user)
        course = Course.objects.get(course_code = course_id)
        print(course)
        if course.studentlist.filter(user = current_user).exists():
            messages.error(request , 'User is already enrolled in this course')
            return redirect('mycourse')
        studentuser = student_profile.objects.get(user = current_user)
        course.studentlist.add(studentuser)
        studentuser.student_courses.add(course)

        course.save()
        studentuser.save()
        messages.success(request , 'User successfully enrolled in the course')
        return redirect('mycourse')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def coursedashboard(request):
    try:
        course = Course.objects.all()
        current_user = request.user
        student = student_profile.objects.get(user = current_user)
        myenroll = student.student_courses.all()

        final = course.difference(myenroll)
        context = {
            "courses":final,
            "student":student
        }
    except:
        course = Course.objects.all()
        current_user = request.user
        prof = faculty_profile.objects.get(user = current_user)
        myenroll = Course.objects.filter(faculty=prof)

        final = course.difference(myenroll)

        context = {
            "courses":final,
            "student":prof
        }
    return render(request , 'course_dashboard_student.html' , context)

def mycourse(request):
    current_user = request.user
    isprof=False
    try:
        student = student_profile.objects.get(user = current_user)
        # print(student)
        myenroll = student.student_courses.all()
        # print((myenroll))
        context = {
            'enrolled': myenroll,
            'student':student,
            'isprof':isprof
        }
    except:
        prof = faculty_profile.objects.get(user = current_user)
        myenroll = Course.objects.filter(faculty=prof)
        isprof=True
        context = {
            'enrolled': myenroll,
            'student':prof,
            'isprof':isprof
        }
    return render(request , 'my_course_student.html' , context)

def createassignment(request, course_id):
    params = {
        "courseid":course_id
    }
    return render(request, 'add_assignment.html', params)

def add_assignment(request, course_id):
    user = request.user
    prof = faculty_profile.objects.filter(user=user)
    if prof is None:
        messages.error(request,"You cannot post an announcement")
    else:
        course = Course.objects.get(course_code = course_id)
        if(request.method == 'POST'):
            assignmentname = request.POST.get('name')
            description = request.POST.get('description')
            duedate = request.POST.get('duedate')
            max_grade = request.POST.get('max_grade')
            attachment = request.POST.get('attachment')
            assignment = Assignment.objects.create(name = assignmentname, description = description, duedate = duedate, max_grade=max_grade, attachment = attachment, assignment_course = course)

            assignment.save()

    return redirect('/mycourse/'+course_id+'/viewassignments')

def view_assignments(request,course_id):
    prof = faculty_profile.objects.filter(user=request.user)
    course = Course.objects.get(course_code=course_id)
    assign = Assignment.objects.filter(assignment_course=course)
    if prof.exists():
        isprof=True
        param = {
            'course':course,
            'assign':assign,
            'isprof':isprof
        }
        return render(request, 'view_assignments_faculty.html', param)
    else:
        student_prof = student_profile.objects.get(user=request.user)
        submit=[]
        for x in assign:
            y = Submission.objects.filter(student=student_prof).filter(assignment=x)
            submit.append(y)
        merged = tuple(zip(assign, submit))
        param = {
            'course':course,
            'merged':merged
        }
        
        return render(request , 'view_assignments.html', param)
        

def edit_assignment(request, course_id, name):
    try:
        prof = faculty_profile.objects.get(user=request.user)
    except:
        messages.error(request, "You are not authorized to add a Course")
        return redirect('/mycourse/'+course_id+'/viewassignments')
    if request.method == 'POST':
        course = Course.objects.get(course_code = course_id)
        editassignment = Assignment.objects.get(assignment_course=course, name=name)
        editassignment.name = request.POST.get('name')
        editassignment.description = request.POST.get('description')
        editassignment.duedate = request.POST.get('duedate')
        editassignment.max_grade = request.POST.get('max_grade')
        editassignment.attachment = request.POST.get('attachment')
        editassignment.save()
    else:
        course = Course.objects.get(course_code = course_id)
        editassignment = Assignment.objects.get(assignment_course=course, name=name)
        params = {'record' : editassignment, 'course' : course}
        return render(request, 'edit_assignment.html', params)
    return redirect('/mycourse/'+course_id+'/viewassignments')

def delete_assignment(request , course_id , name):

    course = Course.objects.get(course_code = course_id)
    Assignment.objects.filter(assignment_course = course , name = name).delete()
    view_assignments(request , course_id)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def delete_announcement(request , course_id , ann_id):

    Announcements.objects.filter(id = ann_id).delete()
    announcements(request , course_id)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

   

def add_submission(request, course_id, name):
    student = student_profile.objects.get(user = request.user)
    assignment = Assignment.objects.get(name = name)
    if(request.method == 'POST'):
        work = request.POST.get('work')
        submission = Submission.objects.create(student = student, assignment = assignment, work = work)
        submission.save()

    if(submission.timestamp <= assignment.duedate):
        submission.feedback='Turned in'
    else:
        submission.feedback='Turned in late'
    submission.save()


    return redirect('/mycourse/'+course_id+'/viewassignments')

def edit_submission(request, course_id, name):
    if(request.method == 'POST'):
        student = student_profile.objects.get(user = request.user)
        assignment = Assignment.objects.get(name = name)
        editsubmission = Submission.objects.get(student = student, assignment = assignment)
        editsubmission.work = request.POST.get('work')
        editsubmission.save()
        if(editsubmission.timestamp <= assignment.duedate):
            editsubmission.feedback='Turned in'
        else:
            editsubmission.feedback='Turned in late'
        editsubmission.save()

    return redirect('/mycourse/'+course_id+'/viewassignments')

def view_students_submission(request,course_id, name):
    course = Course.objects.get(course_code=course_id)
    assignment = Assignment.objects.get(name = name, assignment_course = course)
    submission = Submission.objects.filter(assignment=assignment)
    isprof = True
    params = {'assignment':assignment, 'submission' : submission, 'course' : course, 'isprof' : isprof}
    return render(request, 'view_students_submission.html', params)

def grade_student_submission(request,course_id,name,sub_id):
    course = Course.objects.get(course_code=course_id)
    assignment = Assignment.objects.get(name = name, assignment_course = course)
    submission = Submission.objects.filter(assignment=assignment)
    submissiongrade = Submission.objects.get(assignment=assignment, id=sub_id)
    isprof = True
    params = {'assignment':assignment, 'submission' : submission, 'course' : course, 'isprof' : isprof}
    if(request.method == 'POST'):
        submissiongrade.grade = request.POST.get('grade')
        submissiongrade.graded = True
        submissiongrade.save()
        return render(request, 'view_students_submission.html', params)
    return render(request,'view_students_submission.html',params)

def view_query(request, course_id):
    course = Course.objects.get(course_code=course_id)
    Query = query.objects.filter(course = course)
    prof = faculty_profile.objects.filter(user=request.user)
    isprof=False
    if prof.exists():
        isprof=True
    params = {'course' : course, 'Query' : Query, 'isprof' : isprof}
    return render(request, 'view_query.html', params)

def add_query(request, course_id):
    course = Course.objects.get(course_code=course_id)
    student = student_profile.objects.get(user = request.user)
    params = {'course' : course}
    if(request.method == 'POST'):
        qry = request.POST.get('qry')
        Query = query.objects.create(course=course, user = student, qry=qry)
        Query.save()
        QueryList = query.objects.filter(course = course)
        isprof = False
        params2 = {'course' : course, 'Query' : QueryList, 'isprof' : isprof}
        return render(request, 'view_query.html', params2)
    return render(request, 'add_query.html', params)

def reply_query(request, course_id, qid):
    course = Course.objects.get(course_code=course_id)
    SQuery = query.objects.get(id=qid)
    Query = query.objects.filter(course = course)
    isprof = True
    params = {'course' : course, 'SQuery' : SQuery, 'Query' : Query, 'isprof' : isprof}
    if(request.method == 'POST'):
        SQuery.reply = request.POST.get('reply')
        SQuery.save()
        return render(request, 'view_query.html', params)
    return render(request, 'reply_query.html', params)

def log_out(request):
    logout(request)
    return redirect('/')

def student_list_search(request,course_id):
    if request.method == "POST":
        name = request.POST.get('Search')
        course = Course.objects.get(course_code=course_id)
        student = student_profile.objects.filter(Q(first_name__icontains = name, student_courses=course) | Q(last_name__icontains = name, student_courses=course))
        print(student)
        context = {
            'students':student,
            'course':course
        }
        return render(request , 'student_list.html' , context)
    else:
        return redirect('/mycourse/'+course_id+'/studentlist')
    
def mycourse_search(request):
    if request.method == "POST":
        course_detail = request.POST.get('Search')
        try:
            student = student_profile.objects.get(user = request.user)
            myenroll = student.student_courses.filter(Q(course_code__icontains = course_detail) | Q(name__icontains = course_detail))
            context = {
                'enrolled': myenroll,
                'student':student,
                'isprof':isprof
            }
        except:
            prof = faculty_profile.objects.get(user = request.user)
            myenroll = Course.objects.filter(faculty=prof).filter(Q(course_code__icontains = course_detail) | Q(name__icontains = course_detail))
            isprof=True
            context = {
                'enrolled': myenroll,
                'student':prof,
                'isprof':isprof
            }
        return render(request , 'my_course_student.html' , context)
    else:
        return redirect('/mycourse')
    
def coursedashboard_search(request):
    if request.method == "POST":
        course_detail = request.POST.get('Search')
        try:
            course = Course.objects.filter(Q(course_code__icontains = course_detail) | Q(name__icontains = course_detail))
            current_user = request.user
            student = student_profile.objects.get(user = current_user)
            myenroll = student.student_courses.all()

            final = course.difference(myenroll)

            context = {
                "courses":final,
                "student":student
            }
        except:
            course = Course.objects.filter(Q(course_code__icontains = course_detail) | Q(name__icontains = course_detail))
            current_user = request.user
            prof = faculty_profile.objects.get(user = current_user)
            myenroll = Course.objects.filter(faculty=prof)

            final = course.difference(myenroll)

            context = {
                "courses":final,
                "student":prof
            }
        return render(request , 'course_dashboard_student.html' , context)
    else:
        return redirect('/coursedashboard')
    
def update_profile(request):
    try:
        prof = faculty_profile.objects.get(user=request.user)
        return redirect('/mycourse')
    except:
        student = student_profile.objects.get(user=request.user)
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            print(first_name)
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            batch = request.POST.get('batch')
            branch = request.POST.get('branch')
            program = request.POST.get('program')
            student.first_name = first_name
            student.middle_name = middle_name
            student.last_name = last_name
            student.batch = batch
            student.branch = branch
            student.program = program
            student.save()
            return redirect('/student_profile')
        else:
            context = {
                'student':student
            }
            return render(request, 'update_profile.html', context)
