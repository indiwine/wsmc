from social_media.models import Suspect, ScreeningReport


class ScreeningRequest:
    def __init__(self, suspect: Suspect, report: ScreeningReport):
        self.suspect = suspect
        self.report = report
        self.score = 0

    def add_score(self, amount: int):
        self.score += amount
