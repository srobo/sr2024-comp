#!/usr/bin/env python3

import pathlib
import random
import sys
import unittest

import yaml

# Path hackery
ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from score import (  # noqa: E402
    InvalidScoresheetException,
    Scorer,
)


def shuffled(text: str) -> str:
    values = list(text)
    random.shuffle(values)
    return ''.join(values)


class ScorerTests(unittest.TestCase):
    longMessage = True

    def construct_scorer(self, robot_contents, zone_tokens):
        return Scorer(
            {
                tla: {**info, 'robot_tokens': robot_contents.get(tla, "")}
                for tla, info in self.teams_data.items()
            },
            {x: {'tokens': y} for x, y in zone_tokens.items()},
        )

    def assertScores(self, expected_scores, robot_contents, zone_tokens):
        scorer = self.construct_scorer(robot_contents, zone_tokens)
        scorer.validate(None)
        actual_scores = scorer.calculate_scores()

        self.assertEqual(expected_scores, actual_scores, "Wrong scores")

    def assertInvalidScoresheet(self, robot_contents, zone_tokens, *, code):
        scorer = self.construct_scorer(robot_contents, zone_tokens)

        with self.assertRaises(InvalidScoresheetException) as cm:
            scorer.validate(None)

        self.assertEqual(
            code,
            cm.exception.code,
            f"Wrong error code, message was: {cm.exception}",
        )

    def setUp(self):
        self.teams_data = {
            'ABC': {'zone': 0, 'present': True, 'left_scoring_zone': False},
            'DEF': {'zone': 1, 'present': True, 'left_scoring_zone': False},
        }

    # Scoring logic

    ...

    # Invalid characters

    ...

    # Missing tokens

    ...

    # Extra tokens

    ...

    # Tolerable input deviances

    ...


    # Impossible scenarios

    ...


if __name__ == '__main__':
    unittest.main()
