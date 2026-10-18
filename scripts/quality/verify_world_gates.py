"""Negative native traversal checks using earned controller-only checkpoints."""
import argparse
import json
from pathlib import Path
from world_probe import Controller, ROOT
from walk_world import Walker


def verify(state, name, stage):
    engine = ROOT / '.tools/pokeemerald-world-host'
    c = Controller(engine / 'sf-world-blockout.gba', engine / 'sf-world-blockout.elf',
                   ROOT / '.tools/benchmarks' / name, state=state,
                   battery=state.with_suffix('.sav'))
    w = Walker(c, json.loads((ROOT / 'romhack/world/world.json').read_text()))
    try:
        if stage == 7:
            w.travel('gym_8'); w.interact()
            if w.badge(8):
                raise ValueError('Final stamp bypassed the required crisis checkpoints')
            w.travel('league_route'); w.go((16, 13))
            direction, blocked_badge = 'up', 8
        else:
            w.travel('route_17'); w.go((5, 12))
            direction, blocked_badge = 'right', 5
        if w.badge(blocked_badge):
            raise ValueError('Negative test checkpoint already has the tested badge')
        before = w.location()
        try:
            w.walk(direction, wet=True)
        except ValueError as error:
            if 'Native movement blocked' not in str(error):
                raise
        else:
            raise ValueError('Native traversal crossed a locked gate')
        if w.location() != before:
            raise ValueError('Locked traversal changed the native position')
        c.checkpoint('blocked')
        result = {'passed': True, 'stage': stage, 'blocked_badge': blocked_badge,
                  'position': c.position(), 'controller_only': True,
                  'final_stamp_before_crisis_blocked': stage == 7}
        (c.output / 'gate-result.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        c.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True, type=Path)
    parser.add_argument('--stage', required=True, type=int, choices=[4, 7])
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    verify(args.state.resolve(), args.name, args.stage)


if __name__ == '__main__':
    main()
