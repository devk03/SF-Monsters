# SF Emerald ROM hack

The main game now uses Emerald's actual engine. The user approved this path and
a website that patches a locally supplied Emerald ROM on October 7, 2026.
The complete SF scope and quality gates remain in `docs/game-spec.md` section 15.

Our public repository contains original SF contributions and build/patch tools.
Full commercial and reconstructed cartridges stay under ignored `.tools`.
The release website will distribute the patch and emulator; a player's base ROM
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

Compiler variants build in separate work directories. Upstream cleanup actions
move temporary files into ignored preservation storage, respecting the project's
no-deletion instruction. Game/compiler C and assembly are not changed for this
adaptation. Failed stages and their logs remain available for inspection.

The exact baseline reproduction passes. SF content patching, browser ROM upload,
Flash save compatibility, native/web play and the campaign are subsequent gates.
Renaming stock maps alone does not complete an SF neighborhood adventure.
