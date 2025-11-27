from django.shortcuts import get_object_or_404, render, redirect

from apps.core.models import Company
from .models import (
    Applicant,
    Test,
    UserTest,
    UserAnswer,
    TestResult,
)
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import Big5TestForm, ApplicantForm, DopeTestForm, InterviewForm

from .services.recruitment_service import RecruitmentService
from .services.interview_service import InterviewService


# View for the test form (public)
def test_form(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    error_message = None

    if request.method == "POST":
        form = ApplicantForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            education = form.cleaned_data["education"]
            age = form.cleaned_data["age"]
            work_experience_1 = form.cleaned_data["work_experience_1"]
            work_experience_2 = form.cleaned_data["work_experience_2"]

        if name and email:
            # Cek apakah email sudah digunakan
            if Applicant.objects.filter(email=email).exists():
                error_message = "Email sudah digunakan. Silakan gunakan email lain."
            else:
                applicant = Applicant.objects.create(
                    name=name,
                    email=email,
                    education=education,
                    age=age,
                    work_experience_1=work_experience_1,
                    work_experience_2=work_experience_2,
                )

                test_result = TestResult.objects.create(
                    user=applicant,
                    company=company,
                )

                request.session["applicant_id"] = applicant.id
                request.session["company_id"] = company_id
                request.session["test_result_id"] = test_result.id

                return redirect("personality_test")
        else:
            error_message = "Nama dan email wajib diisi."

    form = ApplicantForm()
    return render(
        request,
        "m2recruit/test_form.html",
        {"company": company, "error_message": error_message, "form": form},
    )


def big5_test_view(request):
    applicant_id = request.session.get("applicant_id")
    company_id = request.session.get("company_id")
    test_result_id = request.session.get("test_result_id")
    applicant = Applicant.objects.get(id=applicant_id)
    company = Company.objects.get(id=company_id)
    big5_test = Test.objects.get(name="Big 5")
    questions = big5_test.question_set.all()
    if request.method == "POST":
        form = Big5TestForm(request.POST, questions=questions)
        if form.is_valid():
            user_test = UserTest.objects.create(
                result_id=test_result_id,
                test=big5_test,
            )
            # Save the responses
            for question in questions:
                response = form.cleaned_data[f"question_{question.id}"]
                UserAnswer.objects.create(
                    user_test=user_test,
                    question=question,
                    answer_value=response,
                )

            avg_user_answer = (
                UserAnswer.objects.filter(user_test=user_test)
                .values("question__trait__name")
                .annotate(average=Avg("answer_value"))
            )
            user_test.score_summary = {
                trait["question__trait__name"]: trait["average"]
                for trait in avg_user_answer
            }
            user_test.save()

            return redirect("dope_test")
    else:
        form = Big5TestForm(questions=questions)
    return render(
        request,
        "m2recruit/personality_test/big5_test.html",
        {"form": form, "applicant": applicant, "company": company},
    )


@login_required
def personality_test_result(request):
    tested_applicants = UserTest.objects.filter(
        test=Test.objects.get(name="Big 5"), result__company=request.user.company
    ).prefetch_related("user_answer")

    applicant_id = request.GET.get("applicant")
    if applicant_id:
        try:
            tested_applicants = tested_applicants.filter(result_id=int(applicant_id))
        except (TypeError, ValueError):
            tested_applicants = tested_applicants.none()
    return render(
        request,
        "m2recruit/personality_test/personality_test_result.html",
        {"applicant_results": tested_applicants},
    )


def dope_test(request):
    applicant_id = request.session.get("applicant_id")
    company_id = request.session.get("company_id")
    applicant = Applicant.objects.get(id=applicant_id)
    company = Company.objects.get(id=company_id)
    dope_test = Test.objects.get(name="Dope")
    questions = dope_test.question_set.all()
    if request.method == "POST":
        form = DopeTestForm(request.POST, questions=questions)
        if form.is_valid():
            user_test = UserTest.objects.create(
                result_id=request.session.get("test_result_id"),
                test=dope_test,
            )
            # Save the responses
            for question in questions:
                response = form.cleaned_data[f"question_{question.id}"]
                UserAnswer.objects.create(
                    user_test=user_test,
                    question=question,
                    selected_answer_id=response,
                )

            count_user_answer = (
                UserAnswer.objects.filter(user_test=user_test)
                .values("selected_answer__value")
                .annotate(count=Count("selected_answer__value"))
            )
            user_test.score_summary = {
                answer["selected_answer__value"]: answer["count"]
                for answer in count_user_answer
            }
            user_test.save()

            return redirect("thank_you")
    else:
        form = DopeTestForm(questions=questions)
    return render(
        request,
        "m2recruit/dope/dope_test.html",
        {"form": form, "applicant": applicant, "company": company},
    )


@login_required
def dope_test_result(request):
    tested_applicants = UserTest.objects.filter(
        test=Test.objects.get(name="Dope"), result__company=request.user.company
    ).prefetch_related("user_answer")

    applicant_id = request.GET.get("applicant")
    if applicant_id:
        try:
            tested_applicants = tested_applicants.filter(result_id=int(applicant_id))
        except (TypeError, ValueError):
            tested_applicants = tested_applicants.none()

    return render(
        request,
        "m2recruit/dope/dope_test_result.html",
        {
            "applicant_responses": tested_applicants,
        },
    )


def thank_you(request):
    del request.session["applicant_id"]
    del request.session["company_id"]
    del request.session["test_result_id"]
    return render(request, "m2recruit/thank_you.html")


class PertanyaanInterviewView(LoginRequiredMixin, View):
    template_name = "m2recruit/interviews/pertanyaan_interviews.html"
    service = InterviewService()

    def get(self, request, *args, **kwargs):
        interview_test = self.service.get_interview_test()
        questions = self.service.get_questions(interview_test)
        available_tests = self.service.get_available_tests(request.user.company)

        selected_id = request.GET.get("test_result")
        selected_applicant = self.service.get_selected_applicant(selected_id, available_tests)

        form = InterviewForm(questions=questions)

        context = self.service.get_context_data(
            selected_applicant=selected_applicant,
            available_tests=available_tests,
            form=form,
            questions=questions
        )

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        interview_test = self.service.get_interview_test()
        questions = self.service.get_questions(interview_test)
        available_tests = self.service.get_available_tests(request.user.company)

        selected_id = request.POST.get("test_result")
        selected_applicant = self.service.get_selected_applicant(selected_id, available_tests)

        form = InterviewForm(request.POST, questions=questions)

        user_test = self.service.process_interview_form(form, selected_applicant, questions)

        if user_test:
            return redirect("interviews")

        context = self.service.get_context_data(
            selected_applicant=selected_applicant,
            available_tests=available_tests,
            form=form,
            questions=questions
        )

        return render(request, self.template_name, context)


@login_required
def interviews(request):
    tested_applicants = UserTest.objects.filter(
        test=Test.objects.get(name="Interview"), result__company=request.user.company
    ).prefetch_related("user_answer")

    applicant_id = request.GET.get("applicant")
    if applicant_id:
        try:
            tested_applicants = tested_applicants.filter(result_id=int(applicant_id))
        except (TypeError, ValueError):
            tested_applicants = tested_applicants.none()

    return render(
        request,
        "m2recruit/interviews/interviews.html",
        {
            "applicants": tested_applicants,
        },
    )


class RecruitDashboardView(LoginRequiredMixin, View):
    template_name = 'm2recruit/recruit_dashboard.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recruitment_service = RecruitmentService()

    def post(self, request, *args, **kwargs):
        applicant_id = request.POST.get("applicant_id")
        new_status = request.POST.get("status")

        test_instance = get_object_or_404(
            TestResult, id=applicant_id, company=request.user.company)
        test_instance.result = new_status
        test_instance.save()

        return redirect("recruit_dashboard")

    def get(self, request, *args, **kwargs):
        user_tests = UserTest.objects.filter(
            result__company=request.user.company
        ).select_related('result', 'test').all()

        grouped_by_status = self.recruitment_service.get_grouped_applicants(user_tests)

        return render(request, self.template_name, {
            'applicants_grouped': grouped_by_status,
        })


@login_required
def generate_link(request):
    user = request.user
    url = request.build_absolute_uri("/")
    link = f"{url}recruit/test_form/{user.company.id}/"

    return render(request, "m2recruit/generate_link.html", {"link": link})
