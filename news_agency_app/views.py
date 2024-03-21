from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import Authors, News
import json
from datetime import date as Date
from datetime import datetime as STRPDATETIME

# Create your views here.
@csrf_exempt
def loginURL(request):
  if request.method == 'POST':
    if request.user.is_authenticated:
      return JsonResponse({'message': 'You are already logged in'}, status=200)
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
      login(request, user)
      request.session.save()
      author = Authors.objects.get(author_username=username)
      return JsonResponse({'message': 'Login successful. Welcome, ' + author.author_name}, status=200)
    else:
      return JsonResponse({'message': 'Login failed. Invalid username or password'}, status=401)
  else:
    return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def logoutURL(request):
  if request.method == 'POST':
    if request.user.is_authenticated:
      logout(request)
      request.session.save()
      return JsonResponse({'message': 'Logout successful'}, status=200)
    else:
      return JsonResponse({'message': 'You are not logged in'}, status=401)
  else:
    return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def storiesURL(request):
  if not request.user.is_authenticated:
    return JsonResponse({'message': 'You are not logged in'}, status=401)
  if request.method == 'POST':
    request_body = request.body.decode('utf-8')
    json_data = json.loads(request_body)

    headline = json_data.get('headline')
    category = json_data.get('category')
    region = json_data.get('region')
    details = json_data.get('details')

    if (headline is None) or (headline == '') or (len(headline) > 64):
      return JsonResponse({'message': 'Service Unavailable'}, status=503)
    if (category is None) or (category == '') or (category not in ['pol', 'art', 'tech', 'trivia']):
      return JsonResponse({'message': 'Service Unavailable'}, status=503)
    if (region is None) or (region == '') or (region not in ['uk', 'eu', 'w']):
      return JsonResponse({'message': 'Service Unavailable'}, status=503)
    if (details is None) or (details == '') or (len(details) > 128):
      return JsonResponse({'message': 'Service Unavailable'}, status=503)
    
    author = Authors.objects.get(author_username=request.user.username)
    datetime = Date.today()
    news = News(headline=headline, category=category, region=region, author=author, datetime=datetime, details=details)
    news.save()

    return JsonResponse({'message': 'Story posted successfully'}, status=201)
  elif request.method == 'GET':
    category = request.GET.get('story_cat')
    region = request.GET.get('story_region')
    date = request.GET.get('story_date')

    if category is None:
      category = '*'
    if category is not None and category not in ['pol', 'art', 'tech', 'trivia', '*']:
      return JsonResponse({'message': 'Invalid category'}, status=400)
    if region is None:
      region = '*'
    if region is not None and region not in ['uk', 'eu', 'w', '*']:
      return JsonResponse({'message': 'Invalid region'}, status=400)
    if date is None:
      date = '*'
    if date is not None and date != '*':
      try:
        date = STRPDATETIME.strptime(date, '%d/%m/%Y')
      except ValueError:
        return JsonResponse({'message': 'Invalid date format'}, status=400)

    if category == '*' and region == '*' and date == '*':
      stories = News.objects.all()
    elif category != '*' and region == '*' and date == '*':
      stories = News.objects.filter(category=category)
    elif category == '*' and region != '*' and date == '*':
      stories = News.objects.filter(region=region)
    elif category == '*' and region == '*' and date != '*':
      stories = News.objects.filter(datetime__gte=date)
    elif category != '*' and region != '*' and date == '*':
      stories = News.objects.filter(category=category, region=region)
    elif category != '*' and region == '*' and date != '*':
      stories = News.objects.filter(category=category, datetime__gte=date)
    elif category == '*' and region != '*' and date != '*':
      stories = News.objects.filter(region=region, datetime__gte=date)
    else:
      stories = News.objects.filter(category=category, region=region, datetime__gte=date)
    
    if stories.count() == 0:
      return JsonResponse({'message': 'No stories found'}, status=404)
    
    story_list = []
    for story in stories:
      story_data = {
        'key': str(story.id),
        'headline': story.headline,
        'story_cat': story.category,
        'story_region': story.region,
        'author': story.author.author_name,
        'story_date': str(story.datetime),
        'story_details': story.details
      }
      story_list.append(story_data)

    return JsonResponse({'stories': story_list}, status=200)
  else:
    return JsonResponse({'message': 'Invalid request'}, status=400)

@csrf_exempt
def delete_storyURL(request, key):
  if not request.user.is_authenticated:
    return JsonResponse({'message': 'You are not logged in'}, status=401)
  if request.method == 'POST':
    news_id = request.POST.get('key')
    if news_id is None:
      return JsonResponse({'message': 'Invalid ID'}, status=503)
    try:
      news = News.objects.get(id=news_id)
      if news.author.author_username == request.user.username:
        news.delete()
        return JsonResponse({'message': 'Story deleted successfully'}, status=200)
      else:
        return JsonResponse({'message': 'You are not the author of this story'}, status=503)
    except News.DoesNotExist:
      return JsonResponse({'message': 'Story not found'}, status=503)
  else:
    return JsonResponse({'message': 'Invalid request'}, status=400)
