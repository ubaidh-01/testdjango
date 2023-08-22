from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate,login,logout
from .models import Room,Topic,Message,User
from django.db.models import Q
# Forms
from .forms import RoomForm
from .forms import UserForm,MyUserCreationForm


# Create your views here.


# LOGIN
def loginPage(request):
    # bcs both register and login are in same page so we have to specify the page by if statement.We write if statement in login_register.html for that reason
    page='login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method=="POST":
        email=request.POST.get('email').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request, 'User doesnot exists')
        
        user=authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password doesnot exist')
    context={
        'page':page
    }
    return render(request,'discord/login_register.html',context)




# LOGOUT USER
def logoutUser(request):
    logout(request)
    return redirect('home')
    


# REGISTER
def registerPage(request):
    form = MyUserCreationForm()
    if request.method =="POST":
        form=MyUserCreationForm(request.POST)
        if form.is_valid():
            # 2:57:45
            user = form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')


    return render(request,'discord/login_register.html',{'form':form})




# HOME
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # rooms=Room.objects.filter(topic__name__icontains=q)
    rooms=Room.objects.filter(

        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)

        )
    
    room_count=rooms.count()
    topics=Topic.objects.all()[0:5]
    room_messages=Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context={
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages

    }
    return render(request,'discord/home.html',context)




def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={
        'user':user,
        'rooms':rooms,
        'topics':topics,
        'room_messages':room_messages,
    }
    return render(request,'discord/profile.html',context)



# ROOM
def room(request,pk):
    room=Room.objects.get(id=pk)
    # message=model name, we are quering all the messages related to specific room[3:3:55]
    room_messages=room.message_set.all().order_by('-created')
    participants=room.participants.all()

    if request.method=="POST":
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
        
    context={
        'room':room,
        'room_messages':room_messages,
        'participants':participants
    }
    return render(request,'discord/room.html',context)




# CREATE ROOM
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics=Topic.objects.all()

    if request.method =='POST':
          topic_name=request.POST.get('topic')
          topic, created = Topic.objects.get_or_create(name=topic_name)
          Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description ')
           )
          return redirect('home')
         
    context ={
        'form':form,
        'topics':topics
    }
    return render(request,'discord/room_form.html',context)




# UPDATE ROOM
@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics=Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You Are Not Allowed Here")


    if request.method == 'POST':
          topic_name=request.POST.get('topic')
          topic, created = Topic.objects.get_or_create(name=topic_name)
          room.name=request.POST.get('name')
          room.topic=topic
          room.description = request.POST.get('description')
          room.save()
          
          return redirect('home')
         
    context={
        'form':form,
        'topics':topics,
        'room':room
    }
    return render(request,'discord/room_form.html',context)




# DELETE ROOM
@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You Are Not Allowed Here")

    if request.method == "POST":
        room.delete()
        return redirect('home')
    
    return render(request,'discord/delete.html',{'obj':room})


            
        
# UPDATE_USER
@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)

    if request.method == "POST":
        # request.FILES -> for profile image
        form = UserForm(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
            
    context={
        'form':form
    }

    return render(request,'discord/update-user.html',context)




# DELETE MESSAGE
@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You Are Not Allowed Here")

    if request.method == "POST":
        message.delete()
        return redirect('home')
    
    return render(request,'discord/delete.html', {'obj': message}) 

    

         
# FOR MOBILE RESPONSIVENESS & Topics component(more):

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context={
        'topics':topics

    }
    return render(request,'discord/topics.html',context)



def activityPage(request):
    room_messages=Message.objects.all()
    context={
        'room_messages':room_messages

    }
    return render(request,'discord/activity.html',context)
