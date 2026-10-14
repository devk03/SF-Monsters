# Native mechanics fixtures

The catalogs contain **58 independently specified scenarios**, including
**10 double-battle interactions**. All58 pass on the approved Emerald reference
and SFv48:24 base-damage cases plus34 turn-order cases. This is partial evidence.
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
