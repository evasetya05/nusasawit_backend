from django.shortcuts import render

def dope(request):
    return render(request, 'psychometric/dope.html')