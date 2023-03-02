from fixtures_mongoengine import Fixture
from apps.tasks.models import Goal


class FixtureGoal(Fixture):
    document_class = Goal
    data = {
        'goal1': {
            'text': 'Joyce asfak akejnaskjasdnak asa',
            'relevancy': 2
        },
        'goal2': {
            'text': 'asda egmgkl asoca',
            'relevancy': 5
        },
        'goal3': {
            'text': 'df,dl;b,dl asda',
            'relevancy': 3
        }
    }
