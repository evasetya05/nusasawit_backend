from django.shortcuts import render

def ir8(request):
    return render(request, 'ir8/industrial_relation_dashboard.html')