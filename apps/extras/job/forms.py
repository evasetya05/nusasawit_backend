from django.forms import ModelForm
from .models import Jobs


class JobForm(ModelForm):
    class Meta:
        model = Jobs
        exclude = ['', ]
