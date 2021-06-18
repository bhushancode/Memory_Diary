#-*- coding: utf-8 -*-
from __future__ import unicode_literals
# from myapp import Config as config
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import requests
import os
import re
import logging
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()


def kerberos_to_entry_number(kerberos):
    return "20" + kerberos[3:5] + kerberos[:3].upper() + kerberos[5:]

# Create your views here.

def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'myapp/changePassword.html', {
        'form': form
    })

def index(request):
    # print(os.environ["OauthTokenURL"])
    # # if request.method == 'POST':
    #     # return redirect(config.authLinkPart1 + config.CLIENT_ID + config.authLinkPart2)
    # myUser = User.objects.get(username=('atishya').lower())
    # print (myUser)
    # login(request, myUser)
    # return redirect('/profile')
    # if request.method=='POST':
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     user = authenticate(username=username, password=password)
    #     if user is not None:
    #         if user.is_active:
    #             login(request, user)
    #             return redirect('/profile')
    #         else:
    #             return render(request, 'myapp/index.html',{'error_string':'Not found'})


    if request.method == 'POST':
        return redirect(os.environ["authLinkPart1"] + os.environ["CLIENT_ID"] + os.environ["authLinkPart2"])
    return render(request, 'myapp/index.html')
    # return render(request, 'myapp/index.html')


def authenticate(request):
    # PostData = {'client_id': config.CLIENT_ID,
    # 'client_secret': config.CLIENT_SECRET,
    # 'grant_type': config.AUTHORIZATION_CODE,
    # 'code': request.GET.get('code')}
    PostData = {'client_id': os.environ["CLIENT_ID"],
    'client_secret': os.environ["CLIENT_SECRET"],
    'grant_type': os.environ["AUTHORIZATION_CODE"],
    'code': request.GET.get('code')}
    print("post data")

    r = requests.post(os.environ["OauthTokenURL"], PostData, verify=os.environ["certiPath"])
    a = r.json()
    access_token = a['access_token']
    PostData2 = {
        'access_token': access_token
    }
    r1 = requests.post(os.environ["ResourceURL"], PostData2, verify=os.environ["certiPath"])
    b = r1.json()

    if User.objects.filter(username=(b['uniqueiitdid']).lower()).exists():
        myUser = User.objects.get(username=(b['uniqueiitdid']).lower())
        print(myUser)
        login(request, myUser)
        return redirect('/profile')
    else:
        # return redirect('/')
        return render(request, 'myapp/index.html', {"error_string": "You are unauthorized to access"})
        # return HttpResponse('Unauthorized to access')
    # myUser = User.objects.get(username=('mayank').lower())
    # login(request, myUser)
    # return redirect('/profile')

# @login_required()
def profile(request):
    email = request.user.email
    print(email)
    print("InProfile")
    exceptions = ['subodh.verma.min19@itbhu.ac.in','vidya.bhushan.che19@itbhu.ac.in']
    # if request.user.is_superuser:
    #     return HttpResponse('super users not allowed')
    # if not(re.findall("15@", email) or re.findall("16@", email)) and not(email in exceptions):
    #    user = User.objects.get(email=email)
    #    user.delete()
    #    return redirect('logout') 
    try:
        u = request.user.student
        print(u)
    except:
        IDDyear = "19"
        query = r"(?<=\.)(.*)(?=\@)"
        branch = str(re.search(r"(?<=\.)(.*)(?=\@)", email).group(0))[-5:-2]
        if(IDDyear+"@" in email):
            try:
                logging.basicConfig(filename='year15.log',level=logging.INFO)
                logging.info(email)
            except:
                pass
            # return redirect('logout')
            branch += "-idd"
        u = Student(name=request.user.first_name, user=request.user, email=request.user.email, department=branch)
        u.save()
    # u = Student(name=request.user.first_name, user=request.user, email=request.user.email)
    # u.save()
    if request.method == 'GET':
        context = {"user": u}
        return render(request, 'myapp/profile.html', context)
    # print int(request.FILES.get('dp').size)<6000000
    if(request.FILES.get('dp') != None):
        if( int(request.FILES.get('dp').size) > 2000000 ):
            return render(request, 'myapp/profile.html', {"user": u, "image": "Image size should be less than 2mb"})
        # Get the picture
        picture = request.FILES.get('dp')
        # check extension
        if not (picture.name.lower().endswith(('.png', '.jpg', '.jpeg'))):
            return render(request, 'myapp/profile.html', {"user": u, "image": "Image should be in .png, .jpg or .jpeg format"})
        extension = picture.name.lower()[picture.name.lower().rfind("."):] 
        picture.name = request.user.username + extension
        u.DP = picture

    if(request.FILES.get('genPic1') != None):
        if( int(request.FILES.get('genPic1').size) > 2000000 ):
            return render(request, 'myapp/profile.html', {"user": u, "image": "Image size should be less than 2mb"})
        u.genPic1 = request.FILES.get('genPic1')
        if not (u.genPic1.name.lower().endswith(('.png', '.jpg', '.jpeg'))):
            return render(request, 'myapp/profile.html', {"user": u, "image": "Image should be in .png, .jpg or .jpeg format"})
        extension = u.genPic1.name.lower()[u.genPic1.name.lower().rfind("."):] 

        u.genPic1.name = request.user.username + extension

    if(request.FILES.get('genPic2') != None):
        if( int(request.FILES.get('genPic2').size) > 2000000 ):
            return render(request, 'myapp/profile.html', {"user": u, "image": "Image size should be less than 2mb"})
        u.genPic2 = request.FILES.get('genPic2')
        if not (u.genPic2.name.lower().endswith(('.png', '.jpg', '.jpeg'))):
            return render(request, 'myapp/profile.html', {"user": u, "image": "Image should be in .png, .jpg or .jpeg format"})
        extension = u.genPic2.name.lower()[u.genPic2.name.lower().rfind("."):] 
        u.genPic2.name = request.user.username + extension

    u.name = request.POST.get('name')
    if len(u.name) == 0:
        return render(request, 'myapp/profile.html', {"user": u, "name": "Name cannot be empty"})

    # Phone email and oneliner can be empty if the user does not wish to specify.
    u.phone = request.POST.get('phone')
    u.email = request.POST.get('email')
    u.oneliner = request.POST.get('oneliner')
    u.future = request.POST.get('future')
    u.save()
    return redirect('/profile')


# @login_required
def answerMyself(request):
    u = request.user
    if request.method == 'GET':
        GenQuestions = GenQuestion.objects.all()
        AnswersDisplay = u.student.AnswersAboutMyself
        gen_GenQuestions = []
        for q in GenQuestions:
            gen_GenQuestions.append([q.id, q.question, ""])
            if (str(q.id) in AnswersDisplay):
                gen_GenQuestions[-1][-1] = AnswersDisplay[str(q.id)]
        context = {"genQuestions": gen_GenQuestions}
        return render(request, 'myapp/answers.html', context)
    # print request.POST.getlist('answer[]')
    for i in range(len(request.POST.getlist('answer[]'))):
        if GenQuestion.objects.filter(id=request.POST.getlist('id[]')[i]).exists() and len(str(request.POST.getlist('answer[]')[i]).strip())>0:
            u.student.AnswersAboutMyself[request.POST.getlist(
                'id[]')[i]] = request.POST.getlist('answer[]')[i]
        else:
            continue
        u.student.save()
    return redirect('/answer')

def get_poll_display(polls, VotesDisplay):
    result = []
    for p in polls:
        try:
            existingVote = VotesDisplay[str(p.id)]
            if not isinstance(existingVote, dict):
                raise TypeError
        except (KeyError, TypeError):
            existingVote = {
                'username': '',
                'name': ''
            }
        result.append([p.id, p.poll, existingVote['username'], existingVote['name']])
    return result


# @login_required()
def poll(request):
    u = request.user
    VotesDisplay = u.student.VotesIHaveGiven
    if request.method == 'GET':
        users_all = User.objects.filter(is_superuser=False)
        # Same dept users
        # dept_users = users_all.filter(student__department=u.student.department)
        dept_users = users_all.all()

        # allPolls = Poll.objects.filter(department="all")
        # deptPolls = Poll.objects.filter(department=u.student.department)
        allPolls = Poll.objects.all()
        deptPolls = Poll.objects.all()

        gen_allPolls = get_poll_display(allPolls, VotesDisplay)
        gen_deptPolls = get_poll_display(deptPolls, VotesDisplay)
        context={"allPolls":gen_allPolls, "deptPolls":gen_deptPolls,"users":users_all,"deptUsers":dept_users}
        return render(request, 'myapp/poll.html',context)

    # if POST request
    # print request.POST.getlist('entrynumber[]')
    entries = request.POST.getlist('entrynumber[]')
    polls = Poll.objects.filter(
        id__in=request.POST.getlist('id[]')
    ).select_for_update()
    print(entries, polls)
    # Fundamental check for double loops
    for (entry, poll) in zip(entries, polls):
        lowerEntry = entry.lower()
        if lowerEntry == u.username.lower():
            continue
        try:
            # Attempt and remove previous vote of current user for this poll
            oldVotePresent = VotesDisplay[str(poll.id)]['username']
            poll.votes[oldVotePresent] -= 1
        except (KeyError, TypeError):
            pass
        otherUser = None
        try:
            otherUser = User.objects.get(username=lowerEntry)
        except:
            continue
        try:
            # otherUser already has votes, incremement it
            poll.votes[lowerEntry] += 1
        except KeyError:
            if (poll.department.lower() == 'all') or (poll.department == otherUser.student.department):
                poll.votes[lowerEntry] = 1
            else:
                continue
        u.student.VotesIHaveGiven[str(poll.id)] = {
            'username': lowerEntry,
            'name': otherUser.student.name
        }
        poll.save(update_fields=('votes',))
        u.student.save(update_fields=('VotesIHaveGiven',))
    return redirect("/poll")
        
# @login_required()
def comment(request):
    u = request.user
    users_all = User.objects.all()
        # we pass this to display options, remove self user
    myComments = u.student.CommentsIWrite
    gen_comments = []
    for c in myComments:
        tmpName=c["forWhom"]
        if users_all.filter(username = c["forWhom"]).exists():
            tmpName=users_all.get(username=c["forWhom"]).student.name
        if not (  "showNameinPDF" in c):
            c["showNameinPDF"]="False"    
        gen_comments.append([c["comment"],c["forWhom"],tmpName,c["showNameinPDF"]])
    context={"comments":gen_comments,"users":users_all}
    if request.method=='GET':
        return render(request, 'myapp/comment.html',context)
    for i in range(len(request.POST.getlist('forWhom[]'))):
        lowerEntry = (request.POST.getlist('forWhom[]')[i]).lower()
        for c in u.student.CommentsIWrite:
            if c["forWhom"]==lowerEntry: #updating an already written message
                c["comment"]=request.POST.getlist('val[]')[i]
                if not (  "showNameinPDF" in c):
                    c["showNameinPDF"]="False"
                else:
                    c["showNameinPDF"]=request.POST.getlist('show[]')[i]
                # A not found check for the user
                if (users_all.filter(username = lowerEntry).exists() and (u.username.lower() != lowerEntry)):
                    u_new = users_all.get(username=lowerEntry) 
                else:
                    return redirect('/comment')
                for c_new in u_new.student.CommentsIGet:
                    if c_new["fromWhom"]==u.username:
                        c_new["comment"]=request.POST.getlist('val[]')[i]
                        c_new["showNameinPDF"]=request.POST.getlist('show[]')[i]
                        break
                u_new.student.save()
                break
        else:
            u.student.CommentsIWrite.append({"comment":request.POST.getlist('val[]')[i],"forWhom":lowerEntry,"showNameinPDF":request.POST.getlist('show[]')[i] })
            # A not found check of user and I cant comment for myself
            if (u.username.lower() == lowerEntry):
                return render(request, 'myapp/comment.html', {"comments":gen_comments,"users":users_all, "comment": "You can't comment for yourself :)"})
            if (users_all.filter(username = lowerEntry).exists()):
                u_new = users_all.get(username=lowerEntry)
            else:
                #print (users_all.filter(username = lowerEntry).exists())
                return redirect('/comment')
            u_new.student.CommentsIGet.append({"comment":request.POST.getlist('val[]')[i],"fromWhom":u.username,"displayInPdf":"True","showNameinPDF":""+request.POST.getlist('show[]')[i] })
            u_new.student.save()
        u.student.save()
    return redirect('/comment')

# @login_required()
def otherComment(request):
    u = request.user
    if request.method=='GET':
        CommentsIGet = u.student.CommentsIGet
        gen_comments=[]
        for c in CommentsIGet:
            tmpName=c["fromWhom"]
            if User.objects.filter(username = c["fromWhom"]).exists():
                tmpName=User.objects.get(username=c["fromWhom"]).student.name
            if not (  "showNameinPDF" in c):
                c["showNameinPDF"]="False"
            gen_comments.append([c["comment"],c["fromWhom"],tmpName,c["displayInPdf"],c["showNameinPDF"] ])
        context={"comments":gen_comments}
        if len(gen_comments)==0:
            return render(request, 'myapp/no_comment.html')
        return render(request, 'myapp/otherComment.html',context)
    for i in range(len(request.POST.getlist('fromWhom[]'))):
        lowerEntry = (request.POST.getlist('fromWhom[]')[i]).lower()
        for c in u.student.CommentsIGet:
            if c["fromWhom"]==lowerEntry:
                c["displayInPdf"]=request.POST.getlist('val[]')[i]
                break
        u.student.save()
    return redirect('/otherComment')


# @login_required()
def yearbook(request):
    dep="eee"
    departmentDic={
            "che": "Chemical",
            "che-idd": "Chemical IDD",
            "cer": "Ceramic",
            "cer-idd": "Ceramic IDD",
            "civ": "Civil",
            "civ-idd": "Civil IDD",
            "cse": "Computer Ccience",
            "cse-idd": "Computer Ccience IDD",
            "eee": "Electrical",
            "eee-idd": "Electrical IDD",
            "ece": "Electronics",
            "mat": "Mathematics",
            "mat-idd": "Mathematics IDD",
            "mec": "Mechanical",
            "mec-idd": "Mechanical IDD",
            "min": "Mining",
            "min-idd": "Mining IDD",
            "phe": "Pharma",
            "phe-idd": "Pharma IDD",
            "chy": "Chemistry",
            "chy-idd": "Chemistry IDD",
            "met": "Metallurgy",
            "met-idd": "Metallurgy IDD",
            "mst": "Material",
            "mst-idd": "Material IDD",
            "hss": "humanities",
            "phy": "Physics",
            "phy-idd": "Physics IDD",
            "bce": "Biotechnology",
            "bce-idd": "Biotechnology IDD",
            "bme": "Biomedical",
            "bme-idd": "Biomedical IDD",
            "all": "all"
    }
    # if request.user.is_superuser:
    #     dep = request.GET.get('department')
    # else:
    dep = request.user.student.department
        
    departmentN=""
    if dep in departmentDic:
        departmentN = departmentDic[dep]
    else:
        departmentN = "all"
    GenQuestions = GenQuestion.objects.all()
    # students_dep = Student.objects.filter(department=dep)
    students_dep = Student.objects.all()
    for i in students_dep:
        gen_GenQuestions=list([])
        for q in GenQuestions:
            if ((str(q.id) in i.AnswersAboutMyself) and i.AnswersAboutMyself[str(q.id)]!=""):
                gen_GenQuestions.append([])
                gen_GenQuestions[-1] = [q.question,i.AnswersAboutMyself[str(q.id)]]
        i.AnswersAboutMyself=list(gen_GenQuestions)

        gen_commentsIGet=list([])
        '''
        for a in i.CommentsIGet:
            if(User.objects.filter(username=a['fromWhom']).exists() and a['comment']!="" and a['displayInPdf']=="True"):
                gen_commentsIGet.append([])
                if('showNameinPDF' in a):
                    if(a['showNameinPDF']=='True'):
                        gen_commentsIGet[-1] = [a['comment'],User.objects.filter(username=a['fromWhom'])[0].student.name]
                    else:
                        gen_commentsIGet[-1] = [a['comment'],""]
                else:
                    gen_commentsIGet[-1] = [a['comment'],""]
        '''

        i.CommentsIGet=list(gen_commentsIGet)

    all_polls=[]
    # for p in Poll.objects.filter(department="all"):
    for p in Poll.objects.all():
        tmpVotes = []
        for (person,count) in p.votes.items():
            Person=""
            if(User.objects.filter(username=person).exists()):
                Person=User.objects.filter(username=person)[0].student.name
            tmpVotes.append([int(count),Person])
        print(tmpVotes)
        tmpVotes.sort(reverse=True)
        ind = min(5,len(tmpVotes))
        if ind!=0:
            all_polls.append([p.poll,tmpVotes[0:ind]])
    dep_polls=[]
    # for p in Poll.objects.filter(department=dep):
    for p in Poll.objects.all():
        tmpVotes = []
        for (person,count) in p.votes.items():
            Person=""
            if(User.objects.filter(username=person).exists()):
                Person=User.objects.filter(username=person)[0].student.name
            tmpVotes.append([int(count),Person])
        tmpVotes.sort(reverse=True)
        ind = min(5,len(tmpVotes))
        if ind!=0:
            dep_polls.append([p.poll,tmpVotes[0:ind]])

    context={"students":students_dep,"department":departmentN,"allPolls":all_polls,"deptPolls":dep_polls,}
    return render(request, 'myapp/yearbook.html',context)
   


def userlogout(request):
    logout(request)
    return redirect("/")

def comingsoon(request):
    return render(request, 'myapp/comingsoon.html')

