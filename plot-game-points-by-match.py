#!/usr/bin/env python3

import argparse

import matplotlib.pyplot as plt
from colour import Color
from sr.comp.comp import SRComp

import plot_utils

comp = SRComp('.')


def game_point_by_match(tla, start_match_num):
    for (_, num), points in {**comp.scores.league.game_points, **comp.scores.knockout.game_points}.items():
        if num < start_match_num:
            continue
        if tla in points:
            yield num, points[tla]
        else:
            yield num, 0


def plot(start_match_num, final_match_num, tlas, highlight, output):
    if tlas is None:
        tlas = comp.teams.keys()

    if highlight is None:
        highlight = tlas

    fig, ax = plt.subplots()
    fig.set_size_inches(*plot_utils.SIZE_INCHES)
    final_val_order = []
    i = 0

    teams_and_hues = plot_utils.get_teams_with_hues(
        comp,
        final_match_num,
        tlas,
        highlight,
    )

    teams_and_colours = [
        (t, Color(hsl=(x, 1., .5)))
        for t, x in teams_and_hues
    ]

    for idx, (team, colour) in enumerate(teams_and_colours):
        z_order = 10
        if team.tla not in highlight:
            colour.luminance = 0.9
            z_order = 0

        score_list = sorted(game_point_by_match(team.tla, start_match_num))

        score_only = [score for (_, score) in score_list]

        score_cum = 0
        score_cum_list = []
        for score in score_only:
            score_cum += score
            score_cum_list.append(score_cum)

        ax.plot(
            score_cum_list,
            label=team.tla,
            color=colour.hex,
            zorder=z_order,
        )
        final_val_order.append((score_cum, idx))

    final_val_order.sort()
    final_val_order.reverse()
    order = [i for (_, i) in final_val_order]
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        [handles[idx] for idx in order],
        [labels[idx] for idx in order],
        loc='upper left',
    )
    plt.xlabel("Match Number")
    plt.ylabel("Game Points")
    plt.savefig(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start-match-num',
        help="Start from the given match number (inclusive, default: %(default)s)",
        type=int,
        default=0,
    )
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
        '--output',
        required=True,
        help='Where to save the plot',
    )

    args = parser.parse_args()

    plot(args.start_match_num, args.final_match_num, args.teams, args.highlight, args.output)
