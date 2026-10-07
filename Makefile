PYTHON ?= .tools/venv/bin/python
.PHONY: setup rom web check native-qa
setup:
	python3 -m venv .tools/venv
	$(PYTHON) -m pip install -r requirements-build.txt
	cd web && npm ci
rom:
	$(PYTHON) scripts/build_rom.py
web: rom
	$(PYTHON) scripts/prepare_web.py
	cd web && npm run build
check:
	bash scripts/check.sh

native-qa: rom
	$(PYTHON) scripts/native_check.py
