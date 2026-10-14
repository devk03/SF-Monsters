"""Source safety guards for SF hints; native campaign captures prove execution."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARCEL = 'VAR_UNUSED_0x40F7'
RELAYS = 'VAR_UNUSED_0x40DB'
STARTER = 'FLAG_SYS_POKEMON_GET'
BADGE = 'FLAG_BADGE01_GET'


def script_program():
    labels, commands = {}, []
    for raw in (ROOT/'romhack/content/sunset.inc').read_text().splitlines():
        line = raw.strip()
        match = re.fullmatch(r'(\w+)::?', line)
        if match:
            if match[1] in labels:
                raise ValueError('Duplicate event label.')
            labels[match[1]] = len(commands)
        elif line and not line.startswith('@'):
            operation, _, operands = line.partition(' ')
            if '\t' in operation:
                operation, _, operands = line.partition('\t')
            commands.append((operation, [value.strip() for value in operands.split(',')]))
    return labels, commands


def acknowledged_dialogue(entry, parcel, relays, *, starter=True, badge=False):
    """Bounded source control-flow check, not an Emerald bytecode emulator."""
    labels, commands = script_program()
    variables = {PARCEL: parcel, RELAYS: relays}
    flags = {STARTER: starter, BADGE: badge}
    messages, heals, money = [], 0, 0
    pc = labels[entry]
    for _ in range(128):
        op, args = commands[pc]; pc += 1
        if op in ('lock', 'faceplayer', 'release', 'waitfanfare'):
            continue
        if op == 'playfanfare':
            if args != ['MUS_HEAL']:
                raise ValueError('Unexpected healing fanfare.')
        elif op == 'special':
            if args != ['HealPlayerParty']:
                raise ValueError('Hint introduced an unexpected native effect.')
            heals += 1
        elif op == 'goto_if_set':
            if flags[args[0]]:
                pc = labels[args[1]]
        elif op in ('goto_if_eq', 'goto_if_ge'):
            value, expected = variables[args[0]], int(args[1], 0)
            matches = value == expected if op == 'goto_if_eq' else value >= expected
            if matches:
                pc = labels[args[2]]
        elif op == 'goto':
            pc = labels[args[0]]
        elif op == 'msgbox':
            if args[1] != 'MSGBOX_DEFAULT' or args[0] not in labels:
                raise ValueError('Invalid hint text binding.')
            messages.append(args[0])
        elif op == 'addmoney':
            money += int(args[0], 0)
        elif op == 'setvar':
            variables[args[0]] = int(args[1], 0)
        elif op == 'end':
            return messages, heals, money, variables
        else:
            raise ValueError('Unexpected hint operation: '+op)
    raise ValueError('Hint did not terminate.')


class StoryHints(unittest.TestCase):
    def test_mentor_points_to_the_actual_next_required_objective(self):
        cases = [(2,0,False,'Heal'), (3,0,False,'HealReturn'),
                 (4,0,False,'HealTransit'), (4,1,False,'HealInput'),
                 (4,2,False,'HealOutput'), (4,3,False,'HealChallenge'),
                 (4,4,True,'HealBadge')]
        for parcel, relays, badge, expected in cases:
            with self.subTest(parcel=parcel, relays=relays, badge=badge):
                messages, heals, money, variables = acknowledged_dialogue(
                    'SF_Karpathy', parcel, relays, badge=badge)
                self.assertEqual(messages, ['SF_Text_'+expected])
                self.assertEqual((heals,money), (1,0))
                self.assertEqual(variables, {PARCEL:parcel, RELAYS:relays})

    def test_no_starter_means_choose_a_companion_without_healing_or_rewards(self):
        messages, heals, money, variables = acknowledged_dialogue(
            'SF_Karpathy', 1, 0, starter=False)
        self.assertEqual((messages,heals,money), (['SF_Text_Choose'],0,0))
        self.assertEqual(variables, {PARCEL:1, RELAYS:0})

    def test_earned_badge_takes_priority_over_older_relay_state(self):
        mentor = acknowledged_dialogue('SF_Karpathy',4,0,badge=True)
        roon = acknowledged_dialogue('SF_Roon',4,0,badge=True)
        self.assertEqual(mentor[:3], (['SF_Text_HealBadge'],1,0))
        self.assertEqual(roon[:3], (['SF_Text_RoonAfterBadge'],0,0))

    def test_returned_sensor_is_not_requested_again_after_delivery_or_badge(self):
        for relays, badge, expected in [(0,False,'RoonAfter'),
                                      (1,False,'RoonAfterDelivery'),
                                      (2,False,'RoonAfterDelivery'),
                                      (3,False,'RoonAfterDelivery'),
                                      (4,True,'RoonAfterBadge')]:
            with self.subTest(relays=relays, badge=badge):
                messages, heals, money, variables = acknowledged_dialogue(
                    'SF_Roon', 4, relays, badge=badge)
                self.assertEqual((messages,heals,money), (['SF_Text_'+expected],0,0))
                self.assertEqual(variables, {PARCEL:4, RELAYS:relays})

    def test_recovery_reward_still_happens_once_before_new_repeat_hints(self):
        first = acknowledged_dialogue('SF_Roon',3,0)
        self.assertEqual(first, (['SF_Text_RoonReturn'],0,500,{PARCEL:4,RELAYS:0}))
        repeat = acknowledged_dialogue('SF_Roon',first[3][PARCEL],0)
        self.assertEqual(repeat[2],0)
        self.assertEqual(repeat[0],['SF_Text_RoonAfter'])


if __name__ == '__main__':
    unittest.main()
