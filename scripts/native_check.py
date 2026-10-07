"""Prepare an isolated native mGBA acceptance run, without touching player saves."""
from pathlib import Path
import subprocess, shutil
root=Path(__file__).resolve().parents[1]
build=root/'build';qa=build/'native-qa';qa.mkdir(parents=True,exist_ok=True)
# A fresh basename ensures the test starts without any battery save.
run=1
while (qa/f'route-{run}.gba').exists():run+=1
rom=qa/f'route-{run}.gba';shutil.copy2(build/'sf-mini-monsters.gba',rom)
symbols=subprocess.check_output(['arm-none-eabi-nm','-n',str(build/'sf-mini-monsters.elf')],text=True)
address=next(line.split()[0] for line in symbols.splitlines() if line.endswith(' b game'))
helper=build/'map-fixture'
subprocess.run(['clang','-std=c11',str(root/'game/content.c'),str(root/'tests/map_fixture.c'),'-o',str(helper)],check=True)
map_data=subprocess.check_output([str(helper)],text=True)
script=qa/f'route-{run}.lua'
script.write_text(f'local gameAddress = 0x{address}\n'+map_data+(root/'tests/native_route.lua').read_text())
print(f'Open {rom} in native mGBA, then Tools > Scripting > File > Load script: {script}')
