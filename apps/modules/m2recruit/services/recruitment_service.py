from itertools import groupby
from ..models import TestResult


class RecruitmentService:
    """Service class for handling recruitment dashboard related operations."""
    
    status_order = [
        "lainnya",
        TestResult.ResultOptions.LULUS,
        TestResult.ResultOptions.DIPERTIMBANGAN,
        TestResult.ResultOptions.TIDAK_LULUS,
    ]

    def get_grouped_applicants(self, user_tests):
        """
        Process and group user test results by status.
        
        Args:
            user_tests: QuerySet of UserTest objects to process
            
        Returns:
            dict: Grouped and sorted applicant data by status
        """
        personality_data = list(user_tests)
        personality_data.sort(key=lambda x: x.result_id)
        
        grouped_data = self._group_test_results(personality_data)
        return self._group_by_status(grouped_data)

    def _group_test_results(self, personality_data):
        """Group test results by applicant."""
        grouped_data = []
        for applicant, group in groupby(personality_data, key=lambda x: x.result):
            grouped = list(group)
            agg = {'applicant': applicant}
            for item in grouped:
                agg[item.test.name.replace(' ', '_')] = item.score_summary
                if item.test.name == 'Dope':
                    agg['dope_personality'] = item.dope_personality
            grouped_data.append(agg)
        return grouped_data

    def _group_by_status(self, grouped_data):
        """Group and sort applicants by their status."""
        grouped_by_status = {status: [] for status in self.status_order}
        
        for data in grouped_data:
            status = data["applicant"].result
            key = status if status in grouped_by_status else "lainnya"
            grouped_by_status[key].append(data)

        for status in grouped_by_status:
            grouped_by_status[status].sort(key=lambda x: x["applicant"].id, reverse=True)
            
        return grouped_by_status
