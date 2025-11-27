from django.shortcuts import get_object_or_404
from django.db.models import Sum
from ..models import Test, Question, TestResult, UserTest, UserAnswerInterview

class InterviewService:
    @staticmethod
    def get_interview_test():
        return get_object_or_404(Test, name="Interview")

    @staticmethod
    def get_questions(interview_test):
        return Question.objects.filter(test=interview_test)

    @staticmethod
    def get_available_tests(company):
        interview_test = InterviewService.get_interview_test()
        tests_qs = TestResult.objects.filter(company=company).select_related("user")

        interviewed_test_ids = UserTest.objects.filter(
            test=interview_test,
            result__company=company
        ).values_list("result_id", flat=True)

        return tests_qs.exclude(id__in=interviewed_test_ids)

    @staticmethod
    def get_selected_applicant(test_result_id, available_tests):
        if not test_result_id:
            return available_tests.first()

        try:
            return available_tests.get(id=int(test_result_id))
        except (TypeError, ValueError, TestResult.DoesNotExist):
            return available_tests.first()

    @staticmethod
    def process_interview_form(form, selected_applicant, questions):
        if selected_applicant is None:
            form.add_error(None, "Tidak ada kandidat yang dipilih.")
            return None

        if not form.is_valid():
            return None

        interview_test = InterviewService.get_interview_test()
        user_test = UserTest.objects.create(
            result=selected_applicant,
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
        return user_test

    @staticmethod
    def get_context_data(selected_applicant, available_tests, form, questions):
        question_entries = [
            (
                question,
                form[f"rating_{question.id}"],
                form[f"comment_{question.id}"],
            )
            for question in questions
        ]

        return {
            "form": form,
            "selected_applicant": selected_applicant,
            "has_available": available_tests.exists(),
            "question_entries": question_entries,
        }
