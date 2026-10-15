"""Offline graph audit of ten linked successful private stationary save cycles.

Every real cycle is freshly re-audited. No emulator, polling, public gate, or
claim of ten consecutive attempts. CLI execution requires explicit --reaudit.
"""
from pathlib import Path
import argparse
import re
import sys

R = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEPENDENCIES = HERE if (HERE/'audit_native_battery_cycle.py').is_file() else R/'scripts/quality'
sys.path.insert(0,str(DEPENDENCIES))
import audit_native_battery_cycle as native
CHAIN_SOURCE_AT_LOAD=Path(__file__).read_bytes()

CHECKS = {'loaded_save_counter_exact','loaded_party_count_exact','loaded_party_exact',
          'loaded_storage_exact','loaded_position_exact','loaded_flags_vars_exact',
          'loaded_settings_exact','loaded_playtime_nondecreasing','loaded_saved_game_stat_exact',
          'loaded_money_exact','loaded_bag_items','loaded_bag_key_items','loaded_bag_balls',
          'loaded_bag_moves','loaded_bag_berries','full_flash_exact'}
SHA = re.compile('[0-9a-f]{64}')


def verify_graph(nodes):
    native.same(len(nodes),10,'Require exactly ten successful cycles; incomplete input is not qualified')
    seen=set();previous=None;worker=nodes[0]['worker_sha256']
    for node in nodes:
        native.require(node['directory'] not in seen,'Duplicate cycle directory')
        seen.add(node['directory'])
        native.same(node['rom'],native.ROM,'Cycle ROM differs')
        native.same(node['core'],native.REV,'Cycle core differs')
        native.same(node['worker_sha256'],worker,'Worker executable changed within chain')
        for field in ['before_sha256','after_sha256','native_state_sha256','native_flash_sha256',
                      'native_metadata_sha256','source_state_sha256','source_battery_sha256',
                      'source_metadata_sha256','worker_sha256']:
            native.require(type(node[field]) is str and SHA.fullmatch(node[field]) is not None,'Invalid hash: '+field)
        native.true(node['freshly_reaudited'],'Missing fresh native/browser re-audit')
        native.require(type(node['checks']) is dict and set(node['checks'])==CHECKS,'Missing native cold checks')
        for name in CHECKS:native.true(node['checks'][name],'Failed native cold check: '+name)
        for field in ['before_counter','after_counter']:
            native.worker_audit.num(node[field],field,integer=True,maximum=0xffffffff)
        native.same(node['after_counter'],(node['before_counter']+1)&0xffffffff,'Save counter is not +1')
        native.same(node['native_counter'],node['after_counter'],'Native consumed another save counter')
        native.same(node['native_flash_sha256'],node['after_sha256'],'Native Flash differs from cycle output')
        native.same(node['source_battery_sha256'],node['before_sha256'],'Boot battery differs from cycle input')
        native.same(node['party_count'],3,'This stationary fixture requires exactly three party monsters')
        native.same(node['boxed_count'],0,'This stationary fixture has no boxed monsters')
        if previous:
            for before,after,label in [('before_sha256','after_sha256','Flash edge'),
                                       ('source_state_sha256','native_state_sha256','cold-state edge'),
                                       ('source_battery_sha256','native_flash_sha256','native battery edge'),
                                       ('source_metadata_sha256','native_metadata_sha256','capture metadata edge')]:
                native.same(node[before],previous[after],'Broken '+label)
            native.same(node['before_counter'],previous['after_counter'],'Counter gap or cycle order differs')
        previous=node
    return dict(kind='private-linked-save-chain',passed=True,successful_linked_cycles=10,
                first_counter=nodes[0]['before_counter'],last_counter=nodes[-1]['after_counter'],
                worker_sha256=worker,rom=native.ROM,core=native.REV,
                fixture={'party_monsters':3,'boxed_monsters':0},consecutive_attempts_claimed=False,
                public_gate_qualified=False,cycles=nodes,
                scope='TEN LINKED SUCCESSFUL PRIVATE stationary cycles. Not ten consecutive attempts, '
                      'public persistence, populated-box coverage, campaign checkpoints or full release approval.')


def load_cycle(directory):
    native.private_path(directory)
    selected=directory/'native.final.json'
    if not selected.exists():selected=directory/'native.json'
    saved=native.read_json(selected)
    native.true(saved['passed'],'Stored cold audit failed')
    native.same(saved['kind'],'private-native-cold-cycle','Wrong stored cold audit kind')
    cold=Path(saved['capture_directory'])
    fresh=native.audit_cold(directory,cold)
    native.true(fresh['passed'],'Fresh cold audit failed')
    for field in ['checks','counter','full_flash_sha256','state_sha256','capture_metadata_sha256',
                  'browser_proof_sha256','rom','core']:
        native.same(saved[field],fresh[field],'Stored cold proof is stale: '+field)
    browser=native.read_json(directory/'browser.json')
    session=Path(browser['save_report']).parent
    identity=native.read_json(session/'identity.json')
    flash=native.flash_audit.audit_bytes((directory/'after.sav').read_bytes())
    return dict(directory=str(directory.resolve()),selected_native_proof=str(selected.resolve()),
                selected_native_proof_sha256=native.sha(selected.read_bytes()),
                browser_proof_sha256=native.sha((directory/'browser.json').read_bytes()),
                identity_sha256=native.sha((session/'identity.json').read_bytes()),
                before_sha256=browser['before_sha256'],after_sha256=browser['after_sha256'],
                before_counter=browser['before_counter'],after_counter=browser['after_counter'],
                native_counter=fresh['counter'],native_state_sha256=fresh['state_sha256'],
                native_flash_sha256=fresh['full_flash_sha256'],native_metadata_sha256=fresh['capture_metadata_sha256'],
                source_state_sha256=identity['files']['state.bin'],source_battery_sha256=identity['files']['battery.sav'],
                source_metadata_sha256=identity['source_state_metadata_sha256'],
                worker_sha256=identity['runtime']['worker-proof.js'],rom=fresh['rom'],core=fresh['core'],
                checks=fresh['checks'],freshly_reaudited=True,party_count=flash['domains']['party_count'],
                boxed_count=len(flash['stored']))


def audit_chain(directories):
    native.same(len(directories),10,'Require ten explicit cycle directories')
    native.same(len({str(path.resolve()) for path in directories}),10,'Duplicate cycle directories')
    # Fail once on missing input before any expensive raw-report re-audit.
    for directory in directories:
        native.private_path(directory)
        native.require(directory.is_dir(),'Incomplete chain: missing '+str(directory))
        for name in ['browser.json','before.sav','after.sav']:
            native.require((directory/name).is_file(),'Incomplete chain: missing '+str(directory/name))
        native.require((directory/'native.final.json').is_file() or (directory/'native.json').is_file(),
                       'Incomplete chain: missing native cold proof')
    return verify_graph([load_cycle(directory) for directory in directories])


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cycles',nargs=10,type=Path)
    parser.add_argument('--reaudit',action='store_true',required=True,help='Explicitly authorize fresh offline raw re-audits')
    parser.add_argument('--excluded-report',type=Path,required=True,help='Retained failed chain07 replay report')
    parser.add_argument('--out',type=Path,required=True,help='New private output directory')
    args=parser.parse_args(argv)
    native.private_path(args.out)
    native.require(not args.out.exists(),'Preserve existing chain audit output')
    native.private_path(args.excluded_report)
    excluded=native.read_json(args.excluded_report)
    native.same(excluded['kind'],'private-worker-proof-v1','Wrong excluded report kind')
    native.same(excluded['controllerReplay'],None,'Excluded report is not the missing-replay attempt')
    result=audit_chain(args.cycles)
    result['excluded_attempts']=[dict(report=str(args.excluded_report.resolve()),
                                     report_sha256=native.sha(args.excluded_report.read_bytes()),
                                     reason='Missing selected replay completion; retained and not counted')]
    sources=native.dependency_bytes()
    native.same(Path(__file__).read_bytes(),CHAIN_SOURCE_AT_LOAD,'Chain verifier changed during audit')
    sources['audit_save_chain.py']=CHAIN_SOURCE_AT_LOAD
    result['auditor_sha256']=native.sha(sources['audit_save_chain.py'])
    result['dependencies']={name:native.sha(data) for name,data in sources.items()}
    args.out.mkdir();(args.out/'dependencies').mkdir()
    for name,data in sources.items():
        with (args.out/'dependencies'/name).open('xb') as out:out.write(data)
    native.write_json(args.out/'summary.json',result)
    print('TEN LINKED SUCCESSFUL PRIVATE cycles; one excluded reporting attempt. No public gate approval.')


if __name__=='__main__':main()
