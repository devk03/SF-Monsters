# SF world exploration preview

This BPS patch reconstructs native target `c955f48d…` from the supported
USA/Europe Emerald ROM. Players provide their own ROM; it is patched locally.
The full cartridge and private QA saves are not distributed here.

18 compact destinations,19 connectors,13 service interiors and18 local activities
form the shared world. Eight gym sites and contributor mission hooks are reserved.
The level100loan and temporary gym access stamps are exploration tools; they are
not finished battles, campaign progression or balance. Art/world-feel review is open.

World save identity is0x5743/schema1. `/world` uses a separate device-local save
slot and rejects v80 and injected QA saves. The existing v80 patch remains at `/`.
Use Start → SF Map for connections; speak to each gym marker in badge order.
The late route visits Treasure Island, Sutro Tower and Lands End before gym8,
then travels from North Beach to Angel Island with Surf and Waterfall.

The complete58-map native return circuit and the same110,450-frame WASM replay
match all294,912guest RAM bytes. Source generation, compiled resources, doors,
local rewards, older saves and land/Surf recovery have separately scoped proofs
in `docs/game-spec.md` §15.1. These checks do not grant Emerald parity approval.
The older long-browser-session issue remains open despite a clean30sec smoke.

The manifest records the build's checkout-base commit, frozen-input digest,
staging-base commit and linked route proof. It does not claim the staging commit
alone reproduces the build. Full frozen native inputs remain in private receipts.
