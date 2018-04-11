from django.shortcuts import render
from .models import Contact
from .forms import ContactForm
from django import forms
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST,require_http_methods
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Create your views here.

def index(request):
	context = {}
	return render(request , 'home/index.html', context)

@require_http_methods(['POST' , 'GET'])
def contactus(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            subject = request.POST.get('subject' , '')
            message = request.POST.get('message', '')
            forminstance = Contact(name = name,email = email,contact = contact,subject = subject,message = message)
            messages.success(request, 'Submitted successfully!')
            subject, from_email = 'New Contact Request', 'cryptotax@gmail.com'
            email_body_context = {'name':name, 'contact':contact, 'email':email}
            body = loader.render_to_string('home/contactadmin.txt', email_body_context)
            try:
                msg = EmailMultiAlternatives(subject, body, from_email, ['cryptotax@gmail.com'])
                msg.send()
            except ex:
                print(ex)
            forminstance.save()
    else:
        form = ContactForm()

    return render(request , 'home/contact-us.html')
