from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import Person, Company


class Applicant(Person):
    education = models.CharField(max_length=225, blank=True)
    age = models.IntegerField(blank=True, null=True)
    work_experience_1 = models.CharField(max_length=225, blank=True)
    work_experience_2 = models.CharField(max_length=225, blank=True)


class Test(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Trait(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    trait = models.ForeignKey(Trait, on_delete=models.SET_NULL, null=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    value = models.JSONField()

    def __str__(self):
        return self.text


class TestResult(models.Model):
    class ResultOptions(models.TextChoices):
        LULUS = "lulus", _("Lulus")
        TIDAK_LULUS = "tidak_lulus", _("Tidak Lulus")
        DIPERTIMBANGAN = "dipertimbangkan", _("Dipertimbangkan")

    user = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name='test_result')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    result = models.CharField(
        max_length=20, choices=ResultOptions.choices, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.result}"


class UserTest(models.Model):
    result = models.ForeignKey(
        TestResult, on_delete=models.CASCADE, related_name='user_test')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score_summary = models.JSONField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.result.user} - {self.test}"

    @property
    def dope_personality(self):
        if self.test.name == "Dope":
            d, i, s, c = (
                self.score_summary["D"],
                self.score_summary["I"],
                self.score_summary["S"],
                self.score_summary["C"],
            )
            if (c + i) >= (s + d):
                return "Owl (Burung Hantu)"
            elif (s + d) >= (c + i):
                return "Peacock (Merak)"
            elif (s + i) >= (c + d):
                return "Dove (Merpati)"
            elif (c + d) >= (s + i):
                return "Eagle (Elang)"
            else:
                return "Undefined"
        return None


class UserAnswer(models.Model):
    user_test = models.ForeignKey(
        UserTest, on_delete=models.CASCADE, related_name="user_answer"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_value = models.IntegerField(null=True, blank=True)
    selected_answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.selected_answer:
            return f"{self.user_test} - {self.question} - {self.selected_answer.text}"
        else:
            return f"{self.user_test} - {self.question} - {self.answer_value}"


class AnswerBig5Manager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user_test__test__name="Big 5")


class UserAnswerBig5(UserAnswer):
    objects = AnswerBig5Manager()

    class Meta:
        proxy = True
        verbose_name = "User Answer Big 5"
        verbose_name_plural = "User Answers Big 5"


class AnswerDopeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user_test__test__name="Dope")


class UserAnswerDope(UserAnswer):
    objects = AnswerDopeManager()

    class Meta:
        proxy = True
        verbose_name = "User Answer Dope"
        verbose_name_plural = "User Answers Dope"


class AnswerInterviewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user_test__test__name="Interview")


class UserAnswerInterview(UserAnswer):
    objects = AnswerInterviewManager()

    class Meta:
        proxy = True
        verbose_name = "User Answer Interview"
        verbose_name_plural = "User Answers Interview"
