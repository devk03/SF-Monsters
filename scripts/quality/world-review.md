# Private all-town review packet

This exports existing native maps for critique. It does not redesign maps, build
a cartridge, publish the game or imply human acceptance. Full backgrounds omit
actors; controller-only gameplay views show residents and camera scale.

Keep captures and generated PDFs/HTML private: they can contain base-ROM pixels.
Only these original tooling sources belong in Git.

## Regenerate

Use the existing native QA environment for the first two commands. Its mGBA host,
ELF, cartridge and genuine earlier Save must match the intended candidate.
Choose fresh benchmark directories; extraction refuses to overwrite evidence.

```sh
.tools/venv/bin/python scripts/quality/review_world_scenes.py \
  --state .tools/benchmarks/town-v97-crosswalk-continue/returned.state \
  --name town-v97-full-review-tour --street-views
.tools/venv/bin/python scripts/quality/extract_world_review_maps.py \
  --tour .tools/benchmarks/town-v97-full-review-tour \
  --output .tools/benchmarks/world-v97-map-review
```

Then use a Python environment containing ReportLab and Pillow:

```sh
python scripts/quality/build_world_review_book.py \
  --data .tools/benchmarks/world-v97-map-review/maps.json \
  --review-date 2026-10-23
```

Current output filenames explicitly identify v97. Update filenames, template
labels and page counts together when the destination set or release changes.
The PDF cover also uses the matching native region-guide capture at
`.tools/benchmarks/town-v97-crosswalk-continue/city-map.png`.

## Review

- `output/pdf/sf-world-review-v97.pdf`: 25 landscape pages, contact sheets,
  nature comparison, all18 destination pages, missing Presidio Heights and
  critique priorities. Render all pages with Poppler and inspect before delivery.
- `output/review/sf-world-review-v97.html`: a self-contained offline gallery.
  All18 thumbnails open full maps and gameplay views. Filter urban/nature areas.
  Notes are browser-local when storage is available; download feedback JSON
  before closing if storage is unavailable. Nothing is submitted externally.
- Keep the sibling `pdf` and `review` directories together for its PDF link.
  Full maps and gameplay images are embedded, so no image server is required.
- `output/review/{urban,nature}-overview.png`: compact side-by-side images.

October23 verification: fresh18-destination controller tour and18native render
audits pass; all25PDF pages rendered and reviewed. Browser policy blocked opening
the local HTML file, so its interaction behavior is not browser-verified here.
Do not claim a live hosted gallery or an updated public cartridge.

Presidio Heights and the Presidio are missing; Pacific Heights is a separate
existing destination. Golden Gate Park/Richmond is currently one combined map.
Public v92 and root v80 are unchanged by creating these artifacts.
