# SF Emerald ROM hack

The main game now uses Emerald's actual engine. The user approved this path and
a website that patches a locally supplied Emerald ROM on October 7, 2026.
The complete SF scope and quality gates remain in `docs/game-spec.md` section 15.

Our public repository contains original SF contributions and build/patch tools.
Full commercial and reconstructed cartridges stay under ignored `.tools`.
The release website distributes the patch and emulator; a player's base ROM
is validated and patched locally, without uploading it to a server.

Pinned sources:

- [pret/pokeemerald](https://github.com/pret/pokeemerald), commit
  `731ad5bfd6e6f265508d0efcca0ba42f9dcf5881`.
- [pret/agbcc](https://github.com/pret/agbcc), commit
  `da598c1d918402c42c0c0d7128ba14567f3175e9`.
- Official devkitARM container digest in `romhack/Dockerfile`; host libpng 1.6.39.

Prerequisites: Docker, Git and Python 3. Run
`python3 scripts/romhack/bootstrap.py` to build the original matching baseline.
The result must match SHA-1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7` and the
user-approved SHA-256 in the spec. Build evidence goes to
`.tools/romhack-baseline/build.json`; the local ROM stays beside it.
If an SF overlay was previously built, bootstrap preserves its modified inputs
in ignored storage before restoring the pinned base inputs. Run `make hack`
afterward to rebuild the SF overlay. No source or intermediate files are deleted.

Compiler variants build in separate work directories. Upstream cleanup actions
move temporary files into ignored preservation storage, respecting the project's
no-deletion instruction. Game/compiler C and assembly are not changed for this
adaptation. Failed stages and their logs remain available for inspection.

Exact baseline reproduction, SF patch application and local browser ROM upload
pass. The same cartridge reaches identical native-core/WebAssembly frame output.
Flash slot validation passes; actual campaign-save transfers and the SF campaign
remain outstanding gates.
Renaming stock maps alone does not complete an SF neighborhood adventure.

`make hack` builds the small `engine-probe.json` overlay, creates a BPS delta
with pinned Floating IPS, and independently reapplies it to the validated base.
Repeated builds must reproduce the same patch; changing a published version's
bytes requires a version bump. The public `romhack/releases` folder contains
patches and integrity manifests, never full ROMs.

The engine probe changes the opening dialogue and hometown label. Stock art,
creatures, maps and campaign remain scaffolding; it is not the SF campaign MVP.
Floating IPS is Alcaro's GPL-3.0 tool, pinned at
`ff216a75df0987047a67d7923567dc4482ce07ac`; its source/license stay in the local
checkout. Our browser decoder follows byuu's public-domain BPS format rather
than embedding Floating IPS code.
