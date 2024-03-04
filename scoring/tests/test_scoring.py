#!/usr/bin/env python3

import copy
import pathlib
import sys
import unittest
from typing import TypedDict

import yaml

# Path hackery
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from score import (  # type: ignore[import-not-found]  # noqa: E402
    InvalidScoresheetException,
    Scorer,
)


class PlanetState(TypedDict):
    planet_asteroids: int
    spaceships: int
    spaceship_asteroids: int
    egg_on_planet: bool
    egg_in_spaceship: bool


class ScorerTests(unittest.TestCase):
    longMessage = True

    def add_third_and_fourth_planets(self) -> None:
        # For simplicity we mostly test on just two planets
        self.teams_data['GHI'] = copy.deepcopy(self.teams_data['ABC'])
        self.teams_data['GHI']['zone'] = 2
        self.teams_data['DEF'] = copy.deepcopy(self.teams_data['ABC'])
        self.teams_data['DEF']['zone'] = 3
        self.arena_data[2] = copy.deepcopy(self.arena_data[0])
        self.arena_data[3] = copy.deepcopy(self.arena_data[0])

    def construct_scorer(self, robot_asteroids, arena_data):
        return Scorer(
            {
                tla: {**info, 'robot_asteroids': robot_asteroids.get(tla, 0)}
                for tla, info in self.teams_data.items()
            },
            arena_data,
        )

    def assertScores(self, expected_scores, robot_asteroids, arena_data):
        scorer = self.construct_scorer(robot_asteroids, arena_data)
        scorer.validate(self.extra_data)
        actual_scores = scorer.calculate_scores()

        self.assertEqual(expected_scores, actual_scores, "Wrong scores")

    def assertInvalidScoresheet(self, robot_asteroids, arena_data, *, code):
        scorer = self.construct_scorer(robot_asteroids, arena_data)

        with self.assertRaises(InvalidScoresheetException) as cm:
            scorer.validate(self.extra_data)

        self.assertEqual(
            code,
            cm.exception.code,
            f"Wrong error code, message was: {cm.exception}",
        )

    def setUp(self) -> None:
        super().setUp()
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True, 'left_planet': False},
            'DEF': {'zone': 1, 'present': True, 'left_planet': False},
        }
        self.arena_data = {
            0: PlanetState({
                'planet_asteroids': 0,
                'spaceships': 1,
                'spaceship_asteroids': 0,
                'egg_on_planet': False,
                'egg_in_spaceship': False,
            }),
            1: PlanetState({
                'planet_asteroids': 0,
                'spaceships': 1,
                'spaceship_asteroids': 0,
                'egg_on_planet': False,
                'egg_in_spaceship': False,
            }),
        }
        self.extra_data = {
            'spaceships_no_planet': 2,
        }

    def test_template(self):
        template_path = ROOT / 'template.yaml'
        with template_path.open() as f:
            data = yaml.safe_load(f)

        teams_data = data['teams']
        arena_data = data.get('arena_zones')
        extra_data = data.get('other')

        scorer = Scorer(teams_data, arena_data)
        scores = scorer.calculate_scores()

        scorer.validate(extra_data)

        self.assertEqual(
            teams_data.keys(),
            scores.keys(),
            "Should return score values for every team",
        )

    # Scoring logic

    def test_default_positions(self) -> None:
        self.assertScores(
            {'ABC': 0, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_one_asteroid_in_robot(self) -> None:
        self.assertScores(
            {'ABC': 8, 'DEF': 0},
            robot_asteroids={'ABC': 1},
            arena_data=self.arena_data,
        )

    def test_one_asteroid_on_planet(self) -> None:
        self.arena_data[0]['planet_asteroids'] = 1
        self.assertScores(
            {'ABC': 12, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_one_asteroid_in_spaceship(self) -> None:
        self.arena_data[0]['spaceship_asteroids'] = 1
        self.assertScores(
            {'ABC': 40, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_asteroids_planet_and_spaceship(self) -> None:
        self.arena_data[0]['planet_asteroids'] = 1
        self.arena_data[0]['spaceship_asteroids'] = 1
        self.assertScores(
            {'ABC': 52, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_asteroids_planet_and_robot(self) -> None:
        self.arena_data[0]['planet_asteroids'] = 1
        self.assertScores(
            {'ABC': 20, 'DEF': 0},
            robot_asteroids={'ABC': 1},
            arena_data=self.arena_data,
        )

    def test_asteroids_robot_and_spaceship(self) -> None:
        self.arena_data[0]['spaceship_asteroids'] = 1
        self.assertScores(
            {'ABC': 48, 'DEF': 0},
            robot_asteroids={'ABC': 1},
            arena_data=self.arena_data,
        )

    def test_asteroids_robot_and_spaceship_other_team(self) -> None:
        self.arena_data[1]['spaceship_asteroids'] = 1
        self.assertScores(
            {'ABC': 0, 'DEF': 48},
            robot_asteroids={'DEF': 1},
            arena_data=self.arena_data,
        )

    def test_planet_egg_no_other_points(self) -> None:
        self.arena_data[0]['egg_on_planet'] = True
        self.assertScores(
            {'ABC': 0, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_spaceship_egg_no_other_points(self) -> None:
        self.arena_data[0]['egg_in_spaceship'] = True
        self.assertScores(
            {'ABC': 0, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_planet_egg(self) -> None:
        self.arena_data[0]['egg_on_planet'] = True
        self.arena_data[0]['planet_asteroids'] = 2
        self.teams_data['ABC']['left_planet'] = True
        self.arena_data[1]['planet_asteroids'] = 1
        self.assertScores(
            # (12 + 12 + 8 + 1) / 4 = 8.25
            {'ABC': 8.25, 'DEF': 12},
            robot_asteroids={'ABC': 1},
            arena_data=self.arena_data,
        )

    def test_spaceship_egg(self) -> None:
        self.arena_data[0]['egg_in_spaceship'] = True
        self.arena_data[0]['planet_asteroids'] = 2
        self.teams_data['ABC']['left_planet'] = True
        self.arena_data[1]['planet_asteroids'] = 1
        self.assertScores(
            {'ABC': 0, 'DEF': 12},
            robot_asteroids={'ABC': 1},
            arena_data=self.arena_data,
        )

    # Invalid states

    def test_negative_asteroids_in_robot(self) -> None:
        self.assertInvalidScoresheet(
            robot_asteroids={'ABC': -1},
            arena_data=self.arena_data,
            code='negative_asteroids',
        )

    def test_negative_asteroids_on_planet(self) -> None:
        self.arena_data[0]['planet_asteroids'] = -1
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='negative_asteroids',
        )

    def test_negative_asteroids_in_spaceship(self) -> None:
        self.arena_data[0]['spaceship_asteroids'] = -1
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='negative_asteroids',
        )

    def test_too_many_asteroids_in_robot(self) -> None:
        self.assertInvalidScoresheet(
            robot_asteroids={'ABC': 50},
            arena_data=self.arena_data,
            code='wrong_total_asteroids',
        )

    def test_too_many_asteroids_on_planet(self) -> None:
        self.arena_data[0]['planet_asteroids'] = 50
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_total_asteroids',
        )

    def test_too_many_asteroids_in_spaceship(self) -> None:
        self.arena_data[0]['spaceship_asteroids'] = 50
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_total_asteroids',
        )

    def test_too_many_asteroids_total(self) -> None:
        self.arena_data[0]['planet_asteroids'] = 12
        self.arena_data[1]['spaceship_asteroids'] = 12
        self.assertInvalidScoresheet(
            robot_asteroids={'DEF': 8, 'ABC': 8},
            arena_data=self.arena_data,
            code='wrong_total_asteroids',
        )

    def test_negative_spaceships_on_planet(self) -> None:
        self.arena_data[0]['spaceships'] = -1
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='negative_spaceships_on_planet',
        )

    def test_negative_spaceships_elsewhere(self) -> None:
        self.extra_data['spaceships_no_planet'] = -1
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='negative_spaceships_no_planet',
        )

    def test_missing_spaceships(self) -> None:
        self.extra_data['spaceships_no_planet'] = 0
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_total_spaceships',
        )

    def test_too_many_spaceships_one_planet(self) -> None:
        self.arena_data[0]['spaceships'] = 42
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_spaceship_disposition',
        )

    def test_too_many_spaceships_elsewhere(self) -> None:
        self.extra_data['spaceships_no_planet'] = 42
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='too_many_spaceships_no_planet',
        )

    def test_too_many_spaceships_overall(self) -> None:
        self.add_third_and_fourth_planets()

        self.extra_data['spaceships_no_planet'] = 0

        self.arena_data[0]['spaceships'] = 2
        self.arena_data[1]['spaceships'] = 2
        self.arena_data[2]['spaceships'] = 3
        self.arena_data[3]['spaceships'] = 2
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_total_spaceships',
        )

    def test_bad_spaceship_disposition(self) -> None:
        self.extra_data['spaceships_no_planet'] = 3
        self.arena_data[0]['spaceships'] = 2
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_spaceship_disposition',
        )

    def test_ok_spaceship_disposition_1(self) -> None:
        self.extra_data['spaceships_no_planet'] = 2
        self.arena_data[0]['spaceships'] = 2
        self.arena_data[1]['spaceships'] = 2
        self.assertScores(
            {'ABC': 0, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_ok_spaceship_disposition_2(self) -> None:
        self.extra_data['spaceships_no_planet'] = 3
        self.arena_data[0]['spaceships'] = 1
        self.arena_data[1]['spaceships'] = 1
        self.assertScores(
            {'ABC': 0, 'DEF': 0},
            robot_asteroids={},
            arena_data=self.arena_data,
        )

    def test_asteroids_in_spaceship_not_on_planet(self) -> None:
        self.extra_data['spaceships_no_planet'] = 3
        self.arena_data[0]['spaceships'] = 0
        self.arena_data[0]['spaceship_asteroids'] = 2
        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='impossible_asteroids_in_spaceships',
        )

    def test_egg_on_several_planets(self) -> None:
        self.add_third_and_fourth_planets()

        self.arena_data[0]['egg_on_planet'] = True
        self.arena_data[1]['egg_on_planet'] = True
        self.arena_data[2]['egg_on_planet'] = True

        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_egg_disposition',
        )

    def test_egg_in_several_spaceships(self) -> None:
        self.add_third_and_fourth_planets()

        self.arena_data[0]['egg_in_spaceship'] = True
        self.arena_data[1]['egg_in_spaceship'] = True
        self.arena_data[2]['egg_in_spaceship'] = True

        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_egg_disposition',
        )

    def test_egg_on_planet_and_spaceship_1(self) -> None:
        self.arena_data[0]['egg_on_planet'] = True
        self.arena_data[0]['egg_in_spaceship'] = True

        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_egg_disposition',
        )

    def test_egg_on_planet_and_spaceship_1(self) -> None:
        self.arena_data[0]['egg_on_planet'] = True
        self.arena_data[1]['egg_in_spaceship'] = True

        self.assertInvalidScoresheet(
            robot_asteroids={},
            arena_data=self.arena_data,
            code='wrong_egg_disposition',
        )


if __name__ == '__main__':
    unittest.main()
