class InvalidScoresheetException(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


# Rule 8
PLANET_ASTEROID_POINTS = 12
# Rule 10
SPACESHIP_ASTEROID_POINTS = 40
# Rule 13
ROBOT_ASTEROID_POINTS = 8

# Rule 18
LEFT_PLANET_POINTS = 1

NUM_ASTEROIDS = 16
# Asteroids can be on one or two Planets, or in a Spaceship, or in a robot
MAX_NUM_ASTEROIDS = 16 * 2

NUM_SPACESHIPS = 4


def score_team_zone(zone_info, team_info):
    if zone_info['egg_in_ship']:
        # Rule 16
        return 0

    score = sum((
        # Rule 8
        zone_info['planet_asteroids'] * PLANET_ASTEROID_POINTS,
        # Rule 10
        zone_info['spaceship_asteroids'] * SPACESHIP_ASTEROID_POINTS,
        # Rule 13
        team_info['robot_asteroids'] * ROBOT_ASTEROID_POINTS,
    ))

    if team_info['left_planet']:
        # Rule 18
        score += LEFT_PLANET_POINTS

    if zone_info['egg_on_planet']:
        # Rule 15
        score /= 4

    return score


class Scorer:
    def __init__(self, teams_data, arena_data):
        self._teams_data = teams_data
        self._arena_data = arena_data

    def calculate_scores(self):
        return {
            tla: score_team_zone(
                self._arena_data[team_info['zone']],
                team_info,
            )
            for tla, team_info in self._teams_data.items()
        }

    def validate(self, other_data):
        spaceships_no_planet = other_data['spaceships_no_planet']
        if spaceships_no_planet > NUM_SPACESHIPS:
            raise InvalidScoresheetException(
                "Too many Spaceships recorded as being not on a Planet. "
                f"Expected at most {NUM_SPACESHIPS}, but got {spaceships_no_planet}.",
                code='too_many_spaceships_no_planet',
            )
        if spaceships_no_planet < 0:
            raise InvalidScoresheetException(
                "Cannot record negative numbers of spaceships (not on a planet), "
                f"got {spaceships_no_planet}.",
                code='negative_spaceships_no_planet',
            )

        spaceships = {
            f'planet-{zone_id}': info['spaceships']
            for zone_id, info in self._arena_data.items()
        }
        negative_spaceships = {x: y for x, y in spaceships.items() if y < 0}
        if negative_spaceships:
            raise InvalidScoresheetException(
                "Cannot record negative numbers of spaceships (on a planet), "
                f"got {negative_spaceships!r}.",
                code='negative_spaceships_on_planet',
            )

        # Spaceships not on planets can only be in one place.
        # Spaceships on planets can be on at most two planets.
        expected_planet_spaceships = (NUM_SPACESHIPS - spaceships_no_planet)
        max_planet_spaceships = expected_planet_spaceships * 2

        excess_planet_spaceships = {x: y for x, y in spaceships.items() if y > expected_planet_spaceships}
        if excess_planet_spaceships:
            raise InvalidScoresheetException(
                "Invalid disposition of Spaceships recorded.\n"
                f"Given {spaceships_no_planet} Spaceships not on Planets, expected "
                f"at most {expected_planet_spaceships} on any planet but saw: "
                f"{excess_planet_spaceships!r}.",
                code='wrong_spaceship_disposition',
            )

        total_planet_spaceships = sum(spaceships.values())
        if not (expected_planet_spaceships <= total_planet_spaceships <= max_planet_spaceships):
            raise InvalidScoresheetException(
                "Wrong total number of Spaceships.\n"
                f"Given {spaceships_no_planet} Spaceships not on Planets, expected "
                f"between {expected_planet_spaceships} and {max_planet_spaceships} on "
                f"planets (in total) but saw {total_planet_spaceships}: {spaceships!r}.",
                code='wrong_total_spaceships',
            )

        asteroids = {
            f'on-planet-{zone_id}': info['planet_asteroids']
            for zone_id, info in self._arena_data.items()
        } | {
            f'in-spaceship-on-{zone_id}': info['spaceship_asteroids']
            for zone_id, info in self._arena_data.items()
        } | {
            f'''robot-{team_info['zone']}''': team_info['robot_asteroids']
            for team_info in self._teams_data.values()
        }

        negative_asteroids = {x: y for x, y in asteroids.items() if y < 0}
        if negative_asteroids:
            raise InvalidScoresheetException(
                "Cannot record negative numbers of asteroids, "
                f"got {negative_asteroids!r}.",
                code='negative_asteroids',
            )

        num_asteroids = sum(asteroids.values())
        if num_asteroids > MAX_NUM_ASTEROIDS:
            raise InvalidScoresheetException(
                "Unexpected number of asteroids. Expected at most "
                f"{MAX_NUM_ASTEROIDS}, but saw {num_asteroids}: {asteroids!r}.",
                code='wrong_number_asteroids',
            )

        impossible_spaceship_asteroids = [
            f'planet-{zone_id}'
            for zone_id, info in self._arena_data.items()
            if info['spaceship_asteroids'] and not info['spaceships']
        ]
        if impossible_spaceship_asteroids:
            raise InvalidScoresheetException(
                "Some planets have asteroids in spaceships but no recorded "
                f"""spaceships: {", ".join(impossible_spaceship_asteroids)}""",
                code='impossible_asteroids_in_spaceships',
            )


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
