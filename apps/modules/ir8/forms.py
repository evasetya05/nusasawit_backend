from django import forms
from .models import Complaint

class ComplaintCreateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description', 'attachments', 'is_anonymous']
        widgets = {
            'description': forms.Textarea(attrs={'rows':4}),
        }

class ComplaintReviewForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'review_notes']
