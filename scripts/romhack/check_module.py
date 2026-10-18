"""Local contributor preflight; optional PR scope check, never a GitHub workflow."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from content_modules import ROOT, MODULES, load_modules, apply_module_layouts, script_with_module
from generate_world import generate
from world_contract import audit
from world_scripts import map_script


def check_scope(identifier, changed):
    prefix = 'romhack/modules/' + identifier + '/'
    return sorted(path for path in changed if not path.startswith(prefix))


def changed_paths(base):
    if not re.fullmatch(r'(?!-)[A-Za-z0-9_./-]+', base):
        raise ValueError('Base must be a Git ref, not a command option')
    commit = subprocess.check_output(['git', 'merge-base', 'HEAD', base], cwd=ROOT,
                                     text=True).strip()
    tracked = subprocess.check_output(['git', 'diff', '--name-only', '-z', commit, '--'], cwd=ROOT)
    extra = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    return {name.decode() for name in (tracked + extra).split(b'\0') if name}


def check(directory=MODULES):
    manifest = json.loads((ROOT / 'romhack/world/world.json').read_text())
    modules = load_modules(manifest, directory)
    plans = apply_module_layouts(generate(manifest), modules)
    world = audit(manifest, plans)
    if not world['passed']:
        raise ValueError('Module broke the shared world: ' + json.dumps(world['errors']))
    by_world = {m['contract']['world_id']: m for m in modules.values()}
    for plan in plans:
        script_with_module(map_script(manifest, plan), by_world.get(plan['world_id']))
    return modules, world


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', help='Assigned module ID; omit to check all')
    parser.add_argument('--base', help='Also reject PR/worktree changes outside this module')
    parser.add_argument('--modules-root', type=Path, default=MODULES)
    args = parser.parse_args()
    try:
        modules, world = check(args.modules_root)
        if args.module and args.module not in modules:
            raise ValueError('Unknown assigned module')
        if args.base:
            if not args.module:
                raise ValueError('PR scope checks require --module')
            outside = check_scope(args.module, changed_paths(args.base))
            if outside:
                raise ValueError('Changes need integrator review outside assigned module: ' + ', '.join(outside))
        selected = [args.module] if args.module else sorted(modules)
        print(json.dumps({'passed': True, 'world': world['counts'],
                          'modules': {name: modules[name]['meta']['status'] for name in selected},
                          'scope_checked': bool(args.base), 'native_build_tested': False,
                          'approved_for_merge': False}, indent=2))
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, 'Module check failed: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
