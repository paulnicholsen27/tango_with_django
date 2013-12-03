from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page, UserProfile
from forms import CategoryForm, PageForm, UserProfileForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime

def decode_url(url):
	return url.replace('_', ' ')

def index(request):
	request.session.set_test_cookie()
	context = RequestContext(request)
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories':category_list, 'pages':page_list}

	response = render_to_response('rango/index.html', context_dict, context)

	visits = int(request.COOKIES.get('visits', '0'))

	if request.COOKIES.has_key('last_visit'):
		last_visit = request.COOKIES['last_visit']
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if (datetime.now() - last_visit_time).days > 0:
			response.set_cookie('visits', visits+1)
			response.set_cookie('last_visit', datetime.now())

	else:
		response.set_cookie('last_visit', datetime.now())

	# for category in category_list:
	# 	category.url = category.name.replace('_', ' ')
	return response
def about(request):
	return HttpResponse("About Page <a href='/rango/'>Main page</a>")\


def category(request, category_name_url):
	context = RequestContext(request)

	category_name = decode_url(category_name_url)
	context_dict = {'category_name':category_name, 
					'category_name_url':category_name_url}
	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass
	return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(request):
	context = RequestContext(request)

	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors

	else:
		form = CategoryForm()

	return render_to_response('rango/add_category.html', {'form':form}, context)

@login_required
def add_page(request, category_name_url):
	print 'add_page called'
	context = RequestContext(request)

	category_name = decode_url(category_name_url)

	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			page = form.save(commit = False)

			cat = Category.objects.get(name = category_name)
			page.category = cat

			page.views = 0

			page.save()

			return category(request, category_name_url)

		else:
			print form.errors

	else:
		form = PageForm()

	return render_to_response('rango/add_page.html',
		{'category_name_url': category_name_url,
		'category_name': category_name, 'form':form},
		context)

def register(request):
	if request.session.test_cookie_worked():
		print ">>> test_cookie_worked"
		request.session.delete_test_cookie()
	else:
		print "no test cookie"
	context = RequestContext(request)

	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True

		else: 
			print user_form.errors, profile_form.errors

	else: 
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response(
		'rango/register.html',
		{'user_form' : user_form,
		 'profile_form' : profile_form,
		 'registered' : registered},
		 context)


def user_login(request):
	context = RequestContext(request)
	errors = []
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user is not None:

			if user.is_active:
				login(request,user)
				return HttpResponseRedirect('/rango/')
			else:
				errors.append("Your account is inactive.")

		else: 
			print "Invalid login details: {0}, {1}".format(username, password)
			errors.append("Invalid login details supplied.")
	return render_to_response('rango/login.html', {'errors': errors}, context)

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/rango/')

@login_required
def restricted(request):
	context = RequestContext(request)
	return render_to_response('rango/restricted.html', {}, context)