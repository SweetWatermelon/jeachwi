from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.hashers import make_password
from .forms import RegisterForm, LoginForm, UploadFileForm
from .models import Users
from django import forms

import requests
import json
from django.conf import settings
from django.core.files.storage import FileSystemStorage

SERVING_IP = getattr(settings, "SERVING_IP", None)

# Create your views here.

def index(request):
    if request.session.get('user') == None:
        return redirect('/login')
    else:
        return render(request, 'index.html', { 'email': request.session.get('user') })

def image_cls(request):
    if request.method == 'POST':

        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'page/image_cls.html', {'uploaded_file_url':uploaded_file_url,'result': '#'})


    return render(request, 'page/image_cls.html')

def serving_exam(request):

    x_pred_list = []
    key_search = ['x_pred1', 'x_pred2', 'x_pred3']
    
    if request.method == 'POST':
        for k, v in request.POST.items():
            if k in key_search and v != '':
                x_pred_list.append(float(v))

        if len(x_pred_list) == 0 :
            return render(request, 'page/serving_sample.html')

        x_pred_load = {"instances": x_pred_list} #[1.0, 2.0, 5.0]
        r = requests.post(SERVING_IP, json=x_pred_load)
        y_pred = json.loads(r.content.decode('utf-8'))
        y_pred = y_pred['predictions']

        context = {
            'result': y_pred,
        }

        return render(request, 'page/serving_sample.html', context)

    elif request.method == 'GET':
        return render(request, 'page/serving_sample.html')

    return render(request, 'page/serving_exam.html')



def jmpark(request):
    return render(request, 'page/jmpark.html')

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = '/'

    def form_valid(self, form):
        user = Users(
            username= form.data.get('username'),
            email=form.data.get('email'),
            password=make_password(form.data.get('password')),
            level='user'
        )
        user.save()

        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        self.request.session['user'] = form.data.get('email')

        return super().form_valid(form)

def logout(request):
    if 'user' in request.session:
        del(request.session['user'])

    return redirect('/')

