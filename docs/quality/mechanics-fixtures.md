# Native mechanics fixtures

The catalogs contain **656 independently specified scenarios**, including
**57 double-battle interactions**. All656 pass on the approved Emerald reference
and current SFv51:24 base-damage,34 pairwise turn-order,40 generated-stat and21 complete
action-order cases,319 type-effect,54 accuracy,23 critical,16 PP,14 HP and38 status cases, plus55 capture-command and8 capture-to-delivery chain cases, plus10 move-script scenarios. This is partial evidence.
The300-case gate, including50 doubles and every required mechanic, remains open.

These are controlled function fixtures. The helper intentionally writes RAM and
CPU registers to establish isolated battle states, then executes the actual
Thumb functions in each ROM under pinned mGBA0.10.5. They are not normal gameplay,
trainer wins, campaign progress, save-transfer checks or performance traces.
The existing controller-only capture harness is unchanged.

## What the first catalog covers

`CalculateBaseDamage` returns an intermediate. The catalog tests physical versus
special type rules, stat stages and critical-stage bypass, burn/Guts, HugePower,
ThickFat, Blaze's exact HP threshold, rain/sun, Reflect/LightScreen, and spread
damage with one versus two defending battlers. Each case stores an explicit
integer expectation and its arithmetic derivation before execution. The runner
does not calculate expected values from observed results.

Final critical multiplication, STAB, effectiveness, random damage, accuracy,
status application, resource consumption and actual HP changes are outside this
function. Stat generation, priority/speed, held items, switching, capture and
the wider doubles interactions remain required. Type-chart pairs must also be
validated; repeating a neutral attack cannot fill the remaining coverage.

The test states use link-rule flags only to suppress campaign badge bonuses.
This does not implement or add multiplayer to the release scope. All four native
battler slots have explicit data and positions; absent flags select the intended
number of participants. Separate scratch RAM supplies the native resource flags.

## Identity and integrity

- Reference SHA256 is fixed to the supplied BPEE ROM. Candidate is the actual
  compiled SF ROM; both must have byte-identical ELF companion cartridges.
- Each input snapshot's metadata must match the ROM hash and pinned core revision.
- Native symbol sizes validate the88-byte battle-mon ABI and global allocations.
  Function bytes must match the provided ELF before the call.
- The helper rejects writes outside EWRAM/IWRAM and calls outside cartridge
  address space. It never exports a modified cartridge, save or campaign state.
- Each call has a2-million-instruction limit; each side has a60-second process
  limit. ROM hashes are checked again after execution. RNG is observed before
  and after every call. Arithmetic/non-tie cases must preserve it; declared
  tie cases must match their independently specified32-bit LCG transition.
- Every case resets its input snapshot. Duplicate IDs, ignored/misspelled
  controls, missing oracles and duplicate effective fixture commands are rejected.
- Raw commands, stdout/stderr, identities and individual results stay in the
  private benchmark directory. Failed attempts are preserved under separate names.

## Run locally

Use the independently verified native host core and supplied local ROMs. For the
recorded v48 checkpoint:

```sh
.tools/venv/bin/python scripts/quality/mechanics_fixtures.py \
  --reference-rom .tools/romhack-baseline/emerald-matching.gba \
  --reference-elf .tools/pokeemerald-host/pokeemerald.elf \
  --reference-state .tools/benchmarks/emerald-trainer-ref-30-calvin-east/capture.state \
  --candidate-rom .tools/romhack-drafts/0.0.48-sunset-facade-variety-preview/86bb0553cd5f8f5311f0ade096c3416a28ae571d4f176dda29710eb4a2b002dc/target.gba \
  --candidate-elf .tools/romhack-drafts/0.0.48-sunset-facade-variety-preview/86bb0553cd5f8f5311f0ade096c3416a28ae571d4f176dda29710eb4a2b002dc/target.elf \
  --candidate-state .tools/benchmarks/facade-variety-v48-fixed-coast/capture.state \
  --name mechanics-v48-base-damage-new-review
```

Choose a new evidence name. Inspect every failed result; do not replace its
expected value merely to match the implementation. `result.json` deliberately
keeps `full_mechanics_gate_complete=false`; a count alone does not prove coverage.
The public repository contains only our harness/vectors, never ROMs or snapshots.

Recorded initial evidence: `mechanics-v48-base-damage-initial` and guarded rerun
`mechanics-v48-base-damage-guarded` under `.tools/benchmarks`. Three separate
negative controls reject ROM writes, wrapped addresses and non-ROM calls while
preserving the reference file hash. These controls do not increase the24-case
mechanics count. Local `scripts/check.sh` runs the fixture-schema/ABI unit checks;
it does not claim these ROM-dependent native cases ran on another machine.


## Turn-order catalog

`turn-order.json` targets `GetWhoStrikesFirst`. Use the same invocation above
with `--cases data/quality/mechanics/turn-order.json` and a fresh evidence name.
The34 scenarios cover speed/stages, GenIII paralysis, MachoBrace, SwiftSwim,
Chlorophyll, active/absent partner weather suppression, QuickClaw's strict
activation threshold, priority brackets, ignoring chosen moves and equal-speed
RNG ties. Fixed item IDs come from the pinned native enum, not guessed values.

All four battle slots and chosen move slots are initialized. An absent slot
gets zero HP as well as its absent flag, so a stale partner ability cannot
incorrectly affect the field. A separate native scratch battle structure supplies
chosen move positions; no player party or battery save is rewritten.

Tie expectations explicitly include the seed and next state: LCG(0)=24691 and
LCG(3)=3310570426. This controlled seeding is fixture setup, not normal gameplay
RNG evidence. The winner and RNG transition must both match on each ROM.
Evidence: `mechanics-v48-turn-order-initial/result.json`. The24 damage cases
were rerun after shared setup changes at `mechanics-v48-base-after-turn-support`.
Pairwise turn comparison does not establish complete four-battler action sorting,
switch/item priorities, move execution or battle outcome correctness.


## Generated-stat catalog

`generated-stats.json` supplies40 scenarios for the actual native CreateMon,
SetMonData, CalculateMonStats and GetNature routines. Run
`scripts/quality/stat_fixtures.py` with the same six ROM/ELF/state arguments and
a new evidence name. Each scenario checks current/max HP, all five other stats,
level, nature and unchanged RNG; it counts once, not once per checked field.

Coverage includes all25 natures, IV0/31 and independent IV fields, level1/100,
EV3/4 and252/255 rounding, fainted/damaged HP when maximum HP changes, and
Shedinja's one-HP exception. Explicit expected vectors come from integer stat
equations and pinned base-stat inputs, never observed results. SF's three starter
base-stat changes are declared intentional content differences: each side has
its own explicit expected vector while using the same arithmetic rules. Read
reference bases from pinned Git, because the working engine tables contain SF
overlays.

The constructor uses fixed IV/personality and preset OT ID in scratch RAM.
Getter/recalculation calls operate on that private object; no player party or
save is changed. This does not test natural RNG distributions, actual EV award
caps or item/growth/evolution acquisition behavior. Per-file source fingerprints,
ELF/function bytes, snapshot/core identities, driver binary and source-commit
provenance accompany the records.

Final shared-driver verification: mechanics-v48-base-shared-final24/24,
mechanics-v48-turn-shared-final34/34 and mechanics-v48-stats-guarded-final40/40.
All98 scenarios pass on both ROMs;10 exercise doubles. The300-case/50-doubles
gate, full state resolution, type chart, accuracy/status, capture/resource and
campaign/performance/save gates remain incomplete.


## Complete action-order catalog

`action-order.json` supplies21 four-battler scenarios. Run
`scripts/quality/action_fixtures.py` with the same six ROM/ELF/state arguments
and a new evidence name. Each executes the actual full scheduling routine and
checks the entire battler/action arrays, next-turn callback, FocusPunch tracker
reset and unchanged RNG. Distinct effective speeds avoid accidental ties.

Coverage includes item/switch precedence, multiple simultaneous items/switches,
run selection, mixed positive/negative move priorities, weather and active ally
suppression, paralysis, MachoBrace, QuickClaw activation/strict threshold/priority,
and speed stages. All four participants are present. Link-rule flags suppress
campaign badge boosts; no multiplayer is added. Actual moves, switches, items
and flee outcomes are not executed by this fixture.

After shared setup extraction, all earlier catalogs pass again in
`mechanics-v48-{base,turn,stats}-after-actions`; complete sorting passes in
`mechanics-v48-action-order-guarded`. Total119 scenarios/31 doubles. At least181
additional broad scenarios/19 doubles remain; a count never replaces required
mechanics coverage or controller-only gameplay and human quality approvals.


## Type effects, STAB and blocking flags

`type-effects.json` adds 72 TypeCalc scenarios, using the main mechanics runner
with `--cases data/quality/mechanics/type-effects.json`. Each has independent
expectations for both intermediate damage and result flags. Coverage includes
all 17 standard attacking types, seven basic immunities, dual-type stacking and
cancellation, STAB and integer floors, Foresight, Levitate, Wonder Guard,
Struggle and minimum damage. This is not the full ordered type matrix.

A blocked attack need not have zero intermediate damage: Levitate can return
missed+immune flags while preserving that value; Wonder Guard can mark a
neutral/resisted attack missed. Later battle scripts determine actual HP loss.
The fixture checks these separately and does not claim complete HP resolution.

The native BattlePokemon ABI now explicitly initializes both types and status2.
One redundant monotype scenario was rejected before execution and omitted; the
failed evidence is preserved and adds no count. All 119 earlier cases pass after
this shared change. Evidence: `mechanics-v48-type-effects-deduplicated` and
`mechanics-v48-{base,turn,stats,action}-after-types`. Total 191 / 300 scenarios,
31 / 50 doubles; all other mechanics, campaign and quality gates stay open.


## Accuracy commands

`accuracy.json` adds 54 scenarios, including 15 doubles. Run
`scripts/quality/accuracy_fixtures.py` with the same six ROM/ELF/state arguments
and a fresh evidence name. It executes Cmd_accuracycheck on a scratch RAM script
and observes the next-script branch, result flags, miss message, hit-marker
consumption and exact final RNG. It does not execute the eventual attack.

Coverage includes exact chance boundaries, accuracy/evasion stages and clamps,
CompoundEyes, Hustle, evasion items, Foresight, weather Thunder, always-hit moves,
Protect, LockOn ownership and semi-invulnerable states. Doubles exercise both
partner slots, both weather-suppressing abilities, absence and spread-move miss
messages. Explicit precedence cases ensure always-hit mechanics do not bypass
Protect or airborne states unless a corresponding exception applies.

Seeds are independently selected using the native LCG equation to produce
specified percentile rolls; expected next states are stored in the catalog.
No-RNG branches must preserve the state. This is deterministic branch evidence,
not a statistical RNG-distribution claim.

Final results: `mechanics-v48-accuracy-guarded`54/54 and all earlier191 cases
rerun in `mechanics-v48-{base,turn,stats,action,types}-after-accuracy`. Total245
scenarios /46 doubles; at least55 broad cases /4 doubles remain. Status, capture,
resource consumption and complete move-resolution coverage remain required.


## Critical hits and resource commands

`critical.json`, `pp.json` and `hp.json` provide 23, 16 and 14 scenarios for
Cmd_critcalc, Cmd_ppreduce and Cmd_datahpupdate. Use
`scripts/quality/battle_command_fixtures.py` with `--cases` selecting one catalog
and the same six ROM/ELF/state arguments. Every scenario supplies a complete
expected observation object; omitted or ignored controls are rejected.

Critical checks cover stage odds/clamping, FocusEnergy, high-critical moves,
ScopeLens, correct/incorrect species-specific items and armor/status/tutorial
suppression. PP covers Pressure across opposing/all-field targets, saturation,
temporary moves, bypass markers and controller deferral. Six are meaningful
doubles. HP checks actual damage/healing saturation, retaliation and ShellBell
trackers, Bide's calculated-versus-actual distinction, missed/immune attacks,
passive damage, Substitute absorption/bypass and PainSplit.

An initial PP/HP run caught missing default RNG initialization in the fixture
setup. The harness now explicitly initializes it; unchanged oracles all pass
in `mechanics-v48-{critical,pp,hp}-seed-guarded`. Failed evidence remains. All
earlier245 cases pass again in the after-resources runs. Total298 scenarios /
52 doubles. **The mechanics gate stays open:** status/capture, the complete type
matrix, integrated move resolution and a coverage review remain required.
These isolated commands queue controller updates; durable party/save writes
and complete battle outcomes are separate controller-only checks.


## Status application

`status.json` adds 38 SetMoveEffect scenarios, including five doubles. Use the
battle-command runner with `--cases data/quality/mechanics/status.json`. Each
checks status1/status2, the native script destination and stack depth, queued
controller updates, effect byte, result/ability flags, hit markers and exact RNG.
Script expectations name whitelisted native status/prevention labels, resolved
against each verified ELF. No expectations come from observed return values.

Coverage includes poison, burn, freeze, paralysis, toxic, sleep and confusion;
sleep/confusion duration boundaries; prevention abilities and types; existing
status, fainting and Substitute; ShieldDust/Safeguard secondary prevention and
ability-origin bypass; sun freeze prevention, active/absent weather suppression
and ally Uproar/Soundproof. Scratch stack/history structures are initialized.

This isolates application. It does not execute outer move-script checks, the
secondary-effect chance roll, Synchronize, residual ticks, cures or animations.
GenIII rules remain intentional: Electric typing alone does not grant paralysis
immunity. An isolated primary function call is not an end-to-end status move.

All earlier298 scenarios pass again. Final results are in
`mechanics-v49-*-after-status`; total336 scenarios /57 doubles. Numerical
minimums are met. Capture, the complete ordered type matrix, integrated attack
resolution and the coverage review still prevent mechanics-gate completion.


## Capture command catalog

`capture.json` contains28 independently specified `Cmd_handleballthrow` outcomes.
The runner creates valid fixed-personality enemy/player Pokemon in scratch RAM,
sets the enemy's initial ball explicitly, seeds command RNG and observes animation,
script branch, exact RNG, attempt counter, Master flag, stored ball, message chooser
and party count. Wild flags are0; trainer/tutorial flags are explicit. No link-rule
controller protocol is inherited from the generic battle setup.

Coverage includes all five shake outcomes, strict threshold-below/equal cases,
Poké/Great/Ultra differences with the same seed, all six major status bonuses,
odds254 versus255, party-space/full messaging, busy deferral, trainer rejection,
tutorial precedence, attempt saturation and a low-rate Beldum. The pinned Master
case preserves the reference's one RNG draw before forced success: its linked
bonus-table predecessor is0 and its unsigned division-by-zero path returns0.
This is a pinned-engine observation, not a portable capture formula assumption.

Use `capture_fixtures.py` with the same six ROM/ELF/state arguments above,
`--cases data/quality/mechanics/capture.json` and a fresh evidence name. Evidence:
`mechanics-v51-capture-guarded`; all28 pass both cartridges. An initial attempt
exceeded the guarded helper's hex-write parser limit; preserved it and split
controller-buffer initialization into1024-byte writes. Expected outcomes were
specified before execution and were not changed to fit observed output.

This command does not consume a bag item, animate the queued scene, register a
new catalog entry, add the monster to a party or transfer it to storage. Those
integrations and the remaining ball types remain required. Total364/57 does
not close the full mechanics gate. No fixture produces a durable campaign save.


## Complete ordered type matrix

`type-matrix.json` adds247 previously missing ordered monotype pairs. Combined
with the42 canonical pairs in `type-effects.json`, all289 relationships among
the17 ordinary GenIII types are explicit and pass on reference/v51. The existing
30 STAB, dual-type, ability, immunity-bypass and integer-boundary cases remain.
The complete type catalogs contain319 scenarios, not72+289 duplicated scenarios.

The oracle comes from the pinned reference relationships before execution; every
unspecified pair is explicitly neutral. Mystery9 and the Foresight/end markers
are excluded from ordinary types; no Fairy or later-generation chart is assumed.
Distribution:179 neutral,57 resisted,46 super-effective and7 immune pairs.
The dataset guard requires exactly the full Cartesian product, no repeated pair,
42 old/247 new relationships and consistent flags/intermediate damage.

Run the existing mechanics runner with `--cases
data/quality/mechanics/type-matrix.json`. Evidence:
`mechanics-v51-type-matrix-initial`,247/247 on both cartridges. These results test
TypeCalc's flags and intermediate damage; they do not establish final randomized
attack resolution, all SF species mappings or human approval of an SF type chart.
The full mechanics gate remains open despite the611/57 numerical totals.


### All native ball-command branches

The capture catalog now has55 scenarios and all12 ball types. Added Net type
branches, Dive map context, Nest level boundaries, Timer cap/wrap behavior,
Luxury/Premier stored ball, Great integer rounding order, Repeat seen/caught
consistency and Safari catch factors. The suite now totals638/57 doubles.
Evidence: `mechanics-v51-capture-all-balls-initial`,55/55 both cartridges.

An intermediate47-case run passed46: the Dive fixture initialized cached
`gMapHeader`, but native `GetCurrentMapType` reads saved location through the ROM
map table. Preserve that failed run. Fixed audited scratch save blocks and observe
GetCurrentMapType itself before each command; all47 then passed with unchanged
capture expectations. The underwater fixture is reference-engine setup, not a
new non-SF game location or an obtainable Safari facility.

`capture_layout.c` compiles sizeof/offsetof with the actual pinned agbcc frontend
before execution. Modern ARM GCC produced incompatible nested save layouts and
was rejected as an ABI source. Native save sizes are0x3d88/0xf2c, Safari factor
offset0x7c; native seen/owned offsets are checked and compiler/source hashes saved.
Repeat uses audited national entry1 and native SET_SEEN/SET_CAUGHT calls. An
owned-only corruption case checks clearing all inconsistent mirrors. This does
not establish all SF species-to-catalog mappings.

Timer246/255 cases explicitly preserve pinned8-bit multiplier wrap and subsequent
integer-division behavior. No later-generation or floating-point formula is used.
Bag/Safari-ball consumption, actual acquisition/storage, Dex registration and
complete presentation/save paths remain separate required integrations.


## Capture-to-delivery function chains

`delivery.json` has eight independently specified shared-state chains: actual
Cmd_handleballthrow guaranteed capture followed by GiveMonToPlayer, with native
capacity checks before/after. Includes party slots2/6, full-PC but available party
space, first/last box slots, wrapping from box13 to0, the420th final available
slot, completely full refusal, and boxed PP restoration35/56 with PPups.

The runner creates valid encrypted Pokemon, fills occupied boxes with native
CopyMon, checks whole-party/whole-PC bytes outside the destination, PC boundary
canaries and independent decryption/checksum validation. Party retains HP/status/
low PP; boxed entries restore PP. Source and recipient share the normal wild
trainer ID. An initial mismatched-ID setup exposed that GiveMonToPlayer's direct
OT-ID setter does not re-encrypt a foreign trade; corrected creation precondition
without changing the independent expected outputs. Failed evidence is preserved.

Native sizeof/offset proofs use agbcc, including storage0x83d0/Pokemon100/boxed80.
Common native_abi helper is reused by capture; all55 capture cases pass after
that refactor. Delivery evidence: `mechanics-v51-delivery-boundary-guarded`,8/8
reference/v51. The three focused schema/decoder/canary tests and fullcheck.sh pass.

The negative full-capacity case deliberately calls delivery after a rejecting
preflight to verify refusal. This bypasses actual bag UI and the result-script
scene; it is not proof of that handler's no-spend branch. No bag decrement, Dex
registration, actual controller synchronization, whole-turn or save/export gate
is claimed. Total646/57 remains partial mechanics evidence.


## Native move-effect interpreter

`move-pipeline.json` contains ten independently specified executions of actual
BattleScript_EffectHit/BurnHit bytecode through the entry of BattleScript_MoveEnd.
Unlike isolated arithmetic commands, the interpreter sequences attack cancellation,
accuracy, PP/Pressure, critical calculation, base damage, STAB/type effects, random
adjustment, HP and secondary-effect selection/prevention. Cases cover neutral/STAB,
4x Water, Ghost immunity, critical/BattleArmor, Pressure, a Tackle miss, Ember burn
and Fire-type prevention, with exact final HP/PP/status/flags/RNG.

The unchanged C helper is driven through a finite PTY transport. Only whitelisted
controller writes/animation/audio commands are ACKed; requests needing a response
fail closed. Queued PP/HP/status packet values and native opcode paths must match
the independent oracle. ABI proofs use agbcc, scratch canaries detect overflow,
duplicate effective setups are rejected before execution and ROM hashes are
rechecked after driver close. Eight negative/schema/path/protocol tests pass.

Evidence `mechanics-v51-move-pipeline-split-transport`:10/10 reference/v51, following
main review and extraction of the bounded transport into its own module. Stop is
BEFORE move-end: residuals, fainting, party synchronization, obedience, next action,
full turns and all presentation/performance/save behavior remain outside this
profile. It does not close the full mechanics gate. Total656/57 doubles.
