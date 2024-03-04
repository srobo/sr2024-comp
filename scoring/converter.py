from __future__ import annotations

from sr.comp.match_period import Match


def render_int(value: int | None) -> int | None:
    """
    Process a maybe missing integer value towards a canonical display form.
    """
    if not value:
        # Display zeros as empty inputs
        return None
    return value


def parse_int(value: str | None) -> int:
    """
    Parse a maybe missing integer value towards an integer.
    """
    if value is None or value == '':
        return 0
    return int(value)


class Converter:
    def form_team_to_score(self, form, zone_id):
        """
        Prepare the part of the score dict for the given zone from the form data.
        """
        return {
            'zone': zone_id,
            'disqualified':
                form.get(f'disqualified_{zone_id}', None) is not None,
            'present':
                form.get(f'present_{zone_id}', None) is not None,
            'left_scoring_zone':
                form.get(f'left_scoring_zone_{zone_id}') is not None,
            'robot_asteroids':
                parse_int(form.get(f'robot_asteroids_{zone_id}')),
        }

    def form_to_score(self, match, form):
        """
        Prepare a score dict for the given match and form dict.

        This method is used to convert the submitted information for storage as
        YAML in the compstate.
        """
        zone_ids = range(len(match.teams))

        teams = {}
        for zone_id in zone_ids:
            tla = form.get(f'tla_{zone_id}', None)
            if tla:
                teams[tla] = self.form_team_to_score(form, zone_id)

        arena = {}
        for zone_id in zone_ids:
            arena[zone_id] = {
                'egg_on_planet': form.get(f'egg_on_planet_{zone_id}') is not None,
                'asteroids': parse_int(form.get(f'asteroids_{zone_id}')),
                'spaceships': parse_int(form.get(f'spaceships_{zone_id}')),
                'spaceship_asteroids': parse_int(form.get(f'spaceship_asteroids_{zone_id}')),
            }

        other = {
            'spaceships_no_planet': parse_int(form.get('spaceships_no_planet')),
        }

        return {
            'arena_id': match.arena,
            'match_number': match.num,
            'teams': teams,
            'arena_zones': arena,
            'other': other,
        }

    def score_to_form(self, score):
        """
        Prepare a form dict for the given score dict.

        This method is used when there is an existing score for a match.
        """
        form = {}

        for tla, info in score['teams'].items():
            zone_id = info['zone']
            form[f'tla_{zone_id}'] = tla
            form[f'disqualified_{zone_id}'] = info.get('disqualified', False)
            form[f'present_{zone_id}'] = info.get('present', True)

            form[f'left_scoring_zone_{zone_id}'] = info['left_scoring_zone']
            form[f'robot_asteroids_{zone_id}'] = render_int(info['robot_asteroids'])

        for zone_id, info in score.get('arena_zones', {}).items():
            form[f'asteroids_{zone_id}'] = render_int(info['asteroids'])
            form[f'spaceships_{zone_id}'] = render_int(info['spaceships'])
            form[f'spaceship_asteroids_{zone_id}'] = render_int(info['spaceship_asteroids'])
            form[f'egg_on_planet_{zone_id}'] = info['egg_on_planet']

        form['spaceships_no_planet'] = score['other']['spaceships_no_planet']

        return form

    def match_to_form(self, match: Match) -> dict[str, str | bool]:
        """
        Prepare a fresh form dict for the given match.

        This method is used when there is no existing score for a match.
        """

        form: dict[str, str | bool] = {}

        for zone_id, tla in enumerate(match.teams):
            if tla:
                form[f'tla_{zone_id}'] = tla
                form[f'disqualified_{zone_id}'] = False
                form[f'present_{zone_id}'] = False
                form[f'left_scoring_zone_{zone_id}'] = False
                form[f'egg_on_planet_{zone_id}'] = False

                form[f'robot_asteroids_{zone_id}'] = None
                form[f'asteroids_{zone_id}'] = None
                form[f'spaceships_{zone_id}'] = None
                form[f'spaceship_asteroids_{zone_id}'] = None

        form['spaceships_no_planet'] = None

        return form
