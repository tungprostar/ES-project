from django.core.files.storage import FileSystemStorage
# Create your views here.
from django.shortcuts import render
from testOMR import grader


def home(request):
    return render(request, 'opencv/index.html')

def result(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        url = fs.url(name)
        filepath = r'.' + url
        correctanswer = grader.grading(filepath)
        print(filepath)
    return render(request, 'opencv/result.html', {'img_url' : url, 'correct': correctanswer})