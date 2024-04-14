#!/usr/bin/env python3

import argparse
import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
from colour import Color
from sr.comp.comp import SRComp

import plot_utils

comp = SRComp('.')


def game_point_by_period(tla, match_periods):
    for period in match_periods:
        total = 0
        for slot in period.matches:
            for match in slot.values():
                if tla in match.teams:
                    scores = getattr(comp.scores, match.type.value)
                    match_id = (match.arena, match.num)
                    try:
                        total += scores.game_points[match_id][tla]
                    except KeyError:
                        # not scored yet
                        pass
        yield total


def plot(final_match_num, tlas, highlight, periods, output):
    if tlas is None:
        tlas = comp.teams.keys()

    if highlight is None:
        highlight = tlas

    fig, ax = plt.subplots()
    fig.set_size_inches(*plot_utils.SIZE_INCHES)

    teams_and_hues = plot_utils.get_teams_with_hues(
        comp,
        final_match_num,
        tlas,
        highlight,
    )

    teams_and_colours = [
        (t, Color(hsl=(x, .85, 0.65)))
        for t, x in teams_and_hues
    ]

    match_periods = comp.schedule.match_periods
    if periods:
        match_periods = [match_periods[x] for x in periods]

    n_cols = len(teams_and_colours) + 3
    width = 1 / n_cols
    offset = n_cols / 2
    cols = np.arange(len(match_periods))

    for idx, (team, colour) in enumerate(teams_and_colours, start=1):
        if team.tla not in highlight:
            colour.luminance = 0.9

        score_only = list(game_point_by_period(team.tla, match_periods))

        ax.bar(
            cols + (idx - offset) * width,
            score_only,
            width=width,
            label=team.tla,
            color=colour.hex,
        )

    plt.legend(loc='upper left', bbox_to_anchor=(1.007, 1.013))
    plt.xticks(cols, [x.description for x in match_periods])
    plt.ylabel("Game Points")
    plt.savefig(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--final-match-num',
        help='Exclude Teams not present at this match number',
        type=int,
        default=144,
    )
    parser.add_argument(
        '--teams',
        help='list of TLAs of teams to plot',
        nargs='+',
    )
    parser.add_argument(
        '--highlight',
        help='list of TLAs of teams to highlight in plot',
        nargs='+',
    )
    parser.add_argument(
        '--periods',
        help="Set explicit periods by index",
        type=int,
        nargs=argparse.ONE_OR_MORE,
        required=False,
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Where to save the plot',
    )

    args = parser.parse_args()

    plot(args.final_match_num, args.teams, args.highlight, args.periods, args.output)
