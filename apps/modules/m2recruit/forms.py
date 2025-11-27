from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Question, Applicant


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['name', 'email', 'education',
                  'age', 'work_experience_1', 'work_experience_2']
        help_texts = {
            'education': 'Contoh: Sarjana Teknik Mesin.',
            'work_experience_1': 'Contoh: Saya bekerja sebagai Software Engineer dengan job desc mengembangkan aplikasi web dari tahun 2020 ke 2023.',
            'work_experience_2': 'Contoh: Saya bekerja sebagai Data Analyst dengan job desc menganalisis data perusahaan dari tahun 2018 ke 2020.',
        }


LIKERT_SCALE = (
    (1, 'Sangat Tidak Setuju'),
    (2, 'Tidak Setuju'),
    (3, 'Netral'),
    (4, 'Setuju'),
    (5, 'Sangat Setuju'),
)


class Big5TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for question in questions:
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=LIKERT_SCALE,
                widget=forms.RadioSelect,
                required=True,
                label=question.text,
            )


class DopeTestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for question in questions:
            choices = [(answer.id, answer.text)
                       for answer in question.answer_set.all()]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=True,
                label=_('Question'),
            )


class InterviewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for question in questions:
            self.fields[f'rating_{question.id}'] = forms.IntegerField(
                widget=forms.NumberInput(attrs={'min': 1, 'max': 5}),
                min_value=1,
                max_value=5,
                required=True,
            )
            self.fields[f'comment_{question.id}'] = forms.CharField(
                widget=forms.Textarea,
                required=False,
            )

    def clean(self):
        cleaned_data = super().clean()

        rating_fields = [name for name in self.fields if name.startswith('rating_')]
        missing_ratings = [name for name in rating_fields if cleaned_data.get(name) in (None, '')]

        if missing_ratings:
            raise forms.ValidationError(_('Semua penilaian wajib diisi.'))

        comment_fields = [name for name in self.fields if name.startswith('comment_')]
        has_comment = any(cleaned_data.get(name, '').strip() for name in comment_fields)

        if not has_comment:
            raise forms.ValidationError(_('Minimal satu komentar harus diisi.'))

        return cleaned_data
