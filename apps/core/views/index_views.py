from django.shortcuts import render

from apps.extras.job.models import Jobs, Application


def index(request):
    jobs = Jobs.objects

    if request.user.is_authenticated:
        current_user = request.user
        if current_user.is_owner():
            return render(request, 'dashboard/hr-dashboard.html')

        elif current_user.is_employee():
            jobs = Jobs.objects.filter(team_lead=request.user)
            applications = Application.objects.filter(job_id__in=jobs)
            return render(request, 'dashboard/tl-dashboard.html',
                          context={'jobs': jobs.all(), 'applications': applications})

    return render(request, 'dashboard/i-dashboard.html', context={'jobs': jobs.all()})
