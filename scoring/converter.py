from sr.comp.scorer import Converter as BaseConverter


class Converter(BaseConverter):
    def form_team_to_score(self, form, zone_id):
        raise NotImplementedError

    def score_to_form(self, score):
        raise NotImplementedError

    def match_to_form(self, match):
        raise NotImplementedError
