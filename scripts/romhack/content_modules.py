"""Load contributor packages without giving them ownership of the shared world."""
import json
import re
from copy import deepcopy
from pathlib import Path
from battle_content import trainer_record

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / 'romhack/modules'
COMMANDS = set(('return msgbox compare compare_var_to_value goto call goto_if_eq '
                'goto_if_ne goto_if_lt goto_if_gt goto_if_le goto_if_ge goto_if_set '
                'goto_if_unset setvar addvar subvar copyvar setflag clearflag checkflag '
                'checktrainerflag trainerbattle_single trainerbattle_double '
                'bufferpartymonnick bufferitemname playse waitse delay applymovement '
                'waitmovement walk_up walk_down walk_left walk_right face_up face_down '
                'face_left face_right step_end').split())


def local_file(directory, name):
    if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_-]*\.(inc|json)', name):
        raise ValueError('Module source must be a local .inc/.json filename')
    path = directory / name
    if path.is_symlink():
        raise ValueError('Module inputs cannot be symlinks')
    path.resolve().relative_to(directory.resolve())
    return path


def lint_script(source, contract):
    """Catch namespace/state escapes; this is a contribution contract, not a sandbox."""
    prefix = 'SFMod_' + contract['id'] + '_'
    definitions = set(re.findall(r'(?m)^([A-Za-z_][A-Za-z0-9_]*):{1,2}\s*$', source))
    if prefix + 'Run' not in definitions or any(not s.startswith(prefix) for s in definitions):
        raise ValueError('Every module label must use its assigned SFMod namespace')
    if len(re.findall(r'(?m)^' + re.escape(prefix) + r'Run::\s*$', source)) != 1:
        raise ValueError('Module must define its Run entry exactly once')
    flags = set(contract['flags'])
    trainers = set(contract['trainer_slots'])
    scratch = {'VAR_RESULT', 'VAR_TEMP_1', 'VAR_TEMP_2', 'VAR_TEMP_3'}
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith('@') or re.fullmatch(r'\w+:{1,2}', line):
            continue
        if line.startswith('.string '):
            match = re.fullmatch(r'\.string "([^"$]*)\$"', line)
            if not match or len(match[1]) > 240:
                raise ValueError('Use one bounded native string with a final dollar terminator')
            continue
        command, _, args = line.partition(' ')
        if command not in COMMANDS:
            raise ValueError('Unsupported module command: ' + command)
        if re.search(r'[^A-Za-z0-9_, |+-]', args):
            raise ValueError('Use one native command per line; no directives or command separators')
        parts = [part.strip() for part in args.split(',')]
        if command in ('setvar', 'addvar', 'subvar', 'copyvar') and parts[0] not in scratch:
            raise ValueError('Module cannot write shared story/save variables')
        if command in ('setflag', 'clearflag') and parts[0] not in flags:
            raise ValueError('Module cannot write another package or core flag')
        if command.startswith('trainerbattle') or command == 'checktrainerflag':
            if parts[0] not in trainers:
                raise ValueError('Module uses an unassigned trainer slot')
        for reference in re.findall(r'\bSFMod_\w+', args):
            if reference not in definitions:
                raise ValueError('Module references an external or missing label')
        if command == 'call' or command.startswith('goto'):
            if parts[-1] not in definitions:
                raise ValueError('Module control flow must remain inside its package')
    return source


def load_modules(manifest, directory=MODULES):
    directory = Path(directory)
    catalog = json.loads((directory / 'contracts.json').read_text())
    if catalog['schema_version'] != 1:
        raise ValueError('Unsupported module contract version')
    modules, targets, flags, trainers = {}, set(), set(), set()
    valid_targets = {a['id'] for a in manifest['areas']} | {g['id'] for g in manifest['gyms']}
    for contract in catalog['modules']:
        identifier = contract['id']
        if not re.fullmatch(r'(gym_[1-8]|mission_[a-z_]+)', identifier) or identifier in modules:
            raise ValueError('Module IDs must be valid and unique')
        target = contract['world_id']
        if contract['kind'] not in ('gym', 'mission'):
            raise ValueError('Unknown contributor module kind')
        if contract['kind'] == 'gym':
            gym = next((g for g in manifest['gyms'] if g['id'] == identifier), None)
            if not gym or (target, contract['area'], contract['grants_badge'], contract['requires_badge']) != (
                    gym['id'], gym['area'], gym['badge'], gym['badge'] - 1):
                raise ValueError('Gym contract disagrees with the core world progression')
        if target not in valid_targets or target in targets:
            raise ValueError('Module hook must name one unique existing world target')
        targets.add(target)
        owned = set(contract['flags'])
        if len(owned) != 3 or flags & owned or any(
                not re.fullmatch(r'FLAG_UNUSED_0x0[234][0-9A-F]', f) for f in owned):
            raise ValueError('Module persistent flags must be unique reserved unused slots')
        flags |= owned
        slots = set(contract['trainer_slots'])
        if len(slots) != len(contract['trainer_slots']) or trainers & slots:
            raise ValueError('Module trainer slots overlap')
        trainers |= slots
        package = directory / identifier
        package.resolve().relative_to(directory.resolve())
        meta = json.loads(local_file(package, 'module.json').read_text())
        if set(meta) != {'schema_version', 'id', 'status', 'owner', 'npcs', 'trainers'}:
            raise ValueError('Module metadata has missing or unsupported keys')
        if meta['schema_version'] != 1 or meta['id'] != identifier or meta['status'] not in (
                'stub', 'draft', 'ready_for_review'):
            raise ValueError('Module identity/status is invalid; approval is never self-declared')
        script = lint_script(local_file(package, 'content.inc').read_text(), contract)
        for team in meta['trainers']:
            if team['id'] not in slots:
                raise ValueError('Package edits an unassigned native team')
            trainer_record(team)
        if len({t['id'] for t in meta['trainers']}) != len(meta['trainers']):
            raise ValueError('Duplicate package trainer definition')
        for slot in re.findall(r'(?m)^\s*trainerbattle_\w+\s+(TRAINER_\w+)', script):
            if slot not in {t['id'] for t in meta['trainers']}:
                raise ValueError('A module battle needs its own trainer team definition')
        layout = local_file(package, 'layout.json')
        rows = json.loads(layout.read_text())['rows'] if layout.exists() else None
        if rows is not None and contract['kind'] != 'gym':
            raise ValueError('Shared neighborhood geometry remains core-owned')
        modules[identifier] = dict(contract=contract, meta=meta, script=script, rows=rows)
    if {m['contract']['id'] for m in modules.values() if m['contract']['kind'] == 'gym'} != {
            g['id'] for g in manifest['gyms']}:
        raise ValueError('All eight world gyms need contributor contracts')
    registered = set(modules)
    found = {p.parent.name for p in directory.glob('*/module.json')}
    if found != registered:
        raise ValueError('Unregistered or missing contributor package')
    return modules


def apply_module_layouts(plans, modules):
    result = deepcopy(plans)
    for module in modules.values():
        if module['meta']['status'] == 'stub':
            continue
        plan = next(p for p in result if p['world_id'] == module['contract']['world_id'])
        if module['rows'] is not None:
            rows = module['rows']
            if len(rows) != 24 or any(not isinstance(r, str) or len(r) != 32 for r in rows):
                raise ValueError('Contributor gym layout must remain 32 by 24')
            plan['rows'] = rows
        for npc in module['meta']['npcs']:
            if set(npc) != {'id', 'x', 'y', 'graphics', 'script'} or npc['id'] != len(plan['npcs']) + 1:
                raise ValueError('Append NPC IDs in native order after core objects')
            if not npc['script'].startswith('SFMod_' + module['contract']['id'] + '_'):
                raise ValueError('NPC script must belong to its own module')
            if not re.fullmatch(r'OBJ_EVENT_GFX_[A-Z0-9_]+', npc['graphics']):
                raise ValueError('Invalid native NPC graphics identifier')
            if npc['script'] + '::' not in module['script']:
                raise ValueError('Contributor NPC references an absent script')
            plan['npcs'].append(npc)
    return result


def script_with_module(source, module):
    if module is None or module['meta']['status'] == 'stub':
        return source
    c = module['contract']
    prefix = 'WB_' + c['world_id']
    hook = ('    call SFMod_' + c['id'] + '_Run\n'
            '    compare VAR_RESULT, 1\n'
            '    goto_if_ne ' + prefix + '_ModuleDone\n')
    anchor = c['success_anchor']
    if source.count(anchor) != 1:
        raise ValueError('Core-owned module hook changed; integrator must review')
    source = source.replace(anchor, hook + anchor, 1)
    if c['kind'] == 'mission' and not c.get('grants_checkpoint'):
        source = source.replace(hook + anchor, hook, 1)
    if c.get('requires_badge') and c['kind'] == 'mission':
        anchor = prefix + '_Info::\n    lock\n    faceplayer\n'
        source = source.replace(anchor, anchor +
            f'    goto_if_unset FLAG_BADGE{c["requires_badge"]:02d}_GET, {prefix}_ModuleDone\n', 1)
    if c['kind'] == 'gym':
        source = source.replace('BLOCKOUT ACCESS STAMP.', 'Contributor gym complete.')
        source = source.replace('No leader battle is built yet.', 'Badge recorded. Exit stays open.')
    source += '\n' + prefix + '_ModuleDone::\n    release\n    end\n\n' + module['script']
    return source
