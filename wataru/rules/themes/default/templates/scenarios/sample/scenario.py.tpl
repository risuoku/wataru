from wataru.workflow.scenario import Scenario
from .provider import SampleProvider


class SampleScenario(Scenario):
    provider_cls = [
        SampleProvider
    ]

    def load(self):
        return {
        }


def create():
    return SampleScenario().build()
