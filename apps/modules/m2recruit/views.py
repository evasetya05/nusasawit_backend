from django.shortcuts import get_object_or_404, render, redirect

from apps.core.models import Company
from .models import (
    Applicant,
    Test,
    Question,
    UserTest,
    UserAnswer,
    TestResult,
    UserAnswerInterview,
)
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum
from itertools import groupby

from .forms import Big5TestForm, ApplicantForm, DopeTestForm, InterviewForm


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


def pertanyaan_interviews(request):
    interview_test = Test.objects.get(name="Interview")
    questions = Question.objects.filter(test=interview_test)

    if request.method == "POST":
        form = InterviewForm(request.POST, questions=questions)
        if form.is_valid():
            pelamar_id = request.POST.get("pelamar")
            test_result = get_object_or_404(TestResult, id=pelamar_id)
            user_test = UserTest.objects.create(
                result=test_result,
                test=interview_test,
            )
            for question in questions:
                rating = form.cleaned_data[f"rating_{question.id}"]
                comment = form.cleaned_data[f"comment_{question.id}"]
                UserAnswerInterview.objects.create(
                    user_test=user_test,
                    question=question,
                    answer_value=rating,
                    comment=comment,
                )
            total_rating = UserAnswerInterview.objects.filter(
                user_test=user_test
            ).aggregate(total=Sum("answer_value"))["total"]
            user_test.score_summary = total_rating
            user_test.save()
            return redirect("interviews")
    else:
        form = InterviewForm(questions=questions)

        tests = TestResult.objects.filter(company=request.user.company).select_related(
            "user"
        )

        # Get IDs of applicants who have already been interviewed
        interviewed_applicants = tests.filter(user_test__test=Test.objects.get(
            name='Interview')).values_list('user_id', flat=True)

        # Filter applicants who have NOT been interviewed
        available_tests = [
            test for test in tests if test.user.id not in interviewed_applicants
        ]

        return render(
            request,
            "m2recruit/interviews/pertanyaan_interviews.html",
            {
                "questions": questions,
                "applicants": available_tests,
                "form": form,
            },
        )


@login_required
def interviews(request):
    tested_applicants = UserTest.objects.filter(
        test=Test.objects.get(name="Interview"), result__company=request.user.company
    ).prefetch_related("user_answer")
    return render(
        request,
        "m2recruit/interviews/interviews.html",
        {
            "applicants": tested_applicants,
        },
    )


@login_required
def recruit_dashboard(request):
    if request.method == "POST":
        applicant_id = request.POST.get("applicant_id")
        new_status = request.POST.get("status")

        test_instance = get_object_or_404(
            TestResult, id=applicant_id, company=request.user.company)
        test_instance.result = new_status
        test_instance.save()

        return redirect("recruit_dashboard")

    user_test = UserTest.objects.filter(
        result__company=request.user.company).select_related('result', 'test').all()
    personality_data = list(user_test)
    personality_data.sort(key=lambda x: x.result_id)
    grouped_data = []
    for applicant, group in groupby(personality_data, key=lambda x: x.result):
        grouped = list(group)
        agg = {'applicant': applicant}
        for item in grouped:
            agg[item.test.name.replace(' ', '_')] = item.score_summary
            if item.test.name == 'Dope':
                agg['dope_personality'] = item.dope_personality

        grouped_data.append(agg)

    sorted_averages = sorted(
        grouped_data, key=lambda x: x['applicant'].id, reverse=True)

    return render(request, 'm2recruit/recruit_dashboard.html', {
        'applicants': sorted_averages,
    })


@login_required
def generate_link(request):
    user = request.user
    url = request.build_absolute_uri("/")
    link = f"{url}recruit/test_form/{user.company.id}/"

    return render(request, "m2recruit/generate_link.html", {"link": link})
