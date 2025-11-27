from django import forms
from .models import OcaiQuestion
from collections import defaultdict


class OcaiForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = OcaiQuestion.objects.all().order_by('dimension')
        for question in questions:
            self.fields[f'current_score_{question.id}'] = forms.IntegerField(
                min_value=0, max_value=100, required=True,
                widget=forms.NumberInput(attrs={'class': 'form-control current_score', 'data-dimensi': question.dimension})
            )
            self.fields[f'expected_score_{question.id}'] = forms.IntegerField(
                min_value=0, max_value=100, required=True,
                widget=forms.NumberInput(attrs={'class': 'form-control expected_score', 'data-dimensi': question.dimension})
            )

    def clean(self):
        cleaned_data = super().clean()
        questions = OcaiQuestion.objects.all().order_by('dimension')

        scores_by_dimension = defaultdict(lambda: {'current': [], 'expected': []})
        for question in questions:
            current_score_key = f'current_score_{question.id}'
            expected_score_key = f'expected_score_{question.id}'

            current_score = cleaned_data.get(current_score_key)
            expected_score = cleaned_data.get(expected_score_key)

            if current_score is not None:
                scores_by_dimension[question.dimension]['current'].append(current_score)
            if expected_score is not None:
                scores_by_dimension[question.dimension]['expected'].append(expected_score)

        for dimension, scores in scores_by_dimension.items():
            current_total = sum(scores['current'])
            if current_total != 100:
                self.add_error(
                    None, f'Total skor "Sekarang" untuk dimensi {dimension} harus 100, bukan {current_total}.')

            expected_total = sum(scores['expected'])
            if expected_total != 100:
                self.add_error(
                    None, f'Total skor "Diharapkan" untuk dimensi {dimension} harus 100, bukan {expected_total}.')

        return cleaned_data
