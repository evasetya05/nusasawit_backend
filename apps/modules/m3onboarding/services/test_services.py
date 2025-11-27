from typing import Dict, List, Optional, TypedDict
from django.urls import reverse

from apps.core.models.employee import Employee
from apps.modules.m2recruit.models import TestResult


class TestScore(TypedDict, total=False):
    scores: Optional[Dict]
    personality: Optional[str]


class InterviewAnswer(TypedDict):
    category: str
    skill: str
    question: str
    rating: int
    comment: str


class InterviewData(TypedDict, total=False):
    total_rating: Optional[Dict]
    answers: List[InterviewAnswer]
    submitted_at: Optional[str]


class TestResultData(TypedDict):
    has_data: bool
    big5: Optional[TestScore]
    dope: Optional[TestScore]
    interview: Optional[InterviewData]
    applicant_name: str
    applicant_email: str
    result_status: str
    test_result_id: Optional[int]
    big5_detail_url: str
    dope_detail_url: str
    interview_detail_url: str


def _get_default_test_result_data() -> TestResultData:
    """Return default test result data structure."""
    return {
        'has_data': False,
        'big5': None,
        'dope': None,
        'interview': None,
        'applicant_name': '',
        'applicant_email': '',
        'result_status': '',
        'test_result_id': None,
        'big5_detail_url': '',
        'dope_detail_url': '',
        'interview_detail_url': '',
    }


def _process_interview_answers(user_test) -> InterviewData:
    """Process interview answers from user test."""
    answers = []
    for answer in user_test.user_answer.all():
        question = answer.question
        trait = question.trait if question else None
        answers.append({
            'category': trait.name if trait else '',
            'skill': trait.description if trait and trait.description else '',
            'question': question.text if question else '',
            'rating': answer.answer_value,
            'comment': answer.comment or '',
        })
    return {
        'total_rating': user_test.score_summary,
        'answers': answers,
        'submitted_at': user_test.submitted_at,
    }


def _process_test_result(test_result: TestResult, data: TestResultData) -> None:
    """Process test result and update data dictionary."""
    data['test_result_id'] = test_result.id
    data['big5_detail_url'] = f"{reverse('personality_test_result')}?applicant={test_result.id}"
    data['dope_detail_url'] = f"{reverse('dope_test_result')}?applicant={test_result.id}"
    data['interview_detail_url'] = f"{reverse('interviews')}?applicant={test_result.id}"

    if test_result.user:
        data['applicant_name'] = test_result.user.name or ''
        data['applicant_email'] = test_result.user.email or ''

    if test_result.result:
        data['result_status'] = test_result.get_result_display()

    for user_test in test_result.user_test.all():
        test_name = (user_test.test.name or '').strip().lower()

        if test_name == 'big 5':
            data['big5'] = {'scores': user_test.score_summary or {}}
        elif test_name == 'dope':
            data['dope'] = {
                'personality': user_test.dope_personality,
                'scores': user_test.score_summary or {}
            }
        elif test_name == 'interview':
            data['interview'] = _process_interview_answers(user_test)

    data['has_data'] = any([data['big5'], data['dope'], data['interview']])


def get_recruitment_tests(employee: Optional[Employee]) -> TestResultData:
    """
    Retrieve and process recruitment test results for a given employee.

    Args:
        employee: Employee object containing email and company information

    Returns:
        TestResultData: Dictionary containing test results and related information
    """
    data = _get_default_test_result_data()

    if not employee or not employee.email or not employee.company:
        return data

    test_result = (
        TestResult.objects
        .filter(company=employee.company, user__email=employee.email)
        .prefetch_related(
            'user_test__test',
            'user_test__user_answer__question__trait'
        )
        .order_by('-id')
        .first()
    )

    if test_result:
        _process_test_result(test_result, data)

    return data
