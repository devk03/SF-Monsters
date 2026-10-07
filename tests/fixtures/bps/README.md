# Independent BPS fixtures

These fixtures contain original ASCII data, not game bytes. Commands were
authored from byuu's public-domain BPS specification. Python's standard-library
CRC-32 produced their checksums; native Floating IPS independently applies them.

They cover SourceRead, TargetRead, forward/backward SourceCopy, overlapping
TargetCopy, and combinations. Expected output bytes are explicit. The browser
decoder tests also reject corrupt patches, wrong inputs and invalid bounds.

These are patch-format checks. They do not count toward the 300 battle-mechanics
reference cases or toward any Emerald presentation approval.
