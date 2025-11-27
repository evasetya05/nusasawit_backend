from django.contrib import admin
from .models import (
    Applicant,
    Test,
    Trait,
    Question,
    Answer,
    TestResult,
    UserTest,
    UserAnswerBig5,
    UserAnswerDope,
    UserAnswerInterview,
)


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'education')
    search_fields = ('name', 'email')


admin.site.register(Test)


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ('test', 'name', 'description')
    search_fields = ('name',)
    list_filter = ('test',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'trait', 'text')
    search_fields = ('text',)
    list_filter = ('test', 'trait')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'value')
    search_fields = ('text',)


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = ('result__user', 'test', 'result__company', 'score_summary')
    search_fields = ('result__user', 'test')
    list_filter = ('result__user', 'test')

    def has_add_permission(self, request):
        return False


@admin.register(UserAnswerBig5)
class UserAnswerBig5Admin(admin.ModelAdmin):
    list_display = ('user_test__result__user', 'question', 'answer_value')
    search_fields = ('user_test__result__user', 'question')
    list_filter = ('user_test__result__user',)

    def has_add_permission(self, request):
        return False


@admin.register(UserAnswerDope)
class UserAnswerDopeAdmin(admin.ModelAdmin):
    list_display = ('user_test__result__user', 'selected_answer',
                    'selected_answer__value')
    search_fields = ('user_test__result__user', 'selected_answer')
    list_filter = ('user_test__result__user',)

    def has_add_permission(self, request):
        return False


@admin.register(UserAnswerInterview)
class UserAnswerInterviewAdmin(admin.ModelAdmin):
    list_display = ('user_test__result__user',
                    'question', 'answer_value', 'comment')
    search_fields = ('user_test__result__user', 'question')
    list_filter = ('user_test__result__user',)

    def has_add_permission(self, request):
        return False

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'result')
    search_fields = ('user', 'company')
    list_filter = ('user', 'company')
