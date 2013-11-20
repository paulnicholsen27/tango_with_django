from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
	boldmessage = "I am a bold message!"
	return render_to_response('rango/index.html', {'boldmessage':boldmessage}, RequestContext(request))

def about(request):
	return HttpResponse("About Page <a href='/rango/'>Main page</a>")