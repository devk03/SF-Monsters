"""Reproducible freestanding GBA build; does not need an existing game ROM."""
from pathlib import Path
import subprocess, sys, shutil
ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build';BUILD.mkdir(exist_ok=True)
subprocess.run([sys.executable,str(ROOT/'scripts/compile_assets.py')],check=True)
flags=['-mcpu=arm7tdmi','-mthumb','-mthumb-interwork','-Os','-ffreestanding','-fno-builtin',
       '-fno-strict-aliasing','-Wall','-Wextra','-Werror','-I'+str(ROOT/'game'),'-I'+str(BUILD)]
objects=[]
for source in [ROOT/'game'/name for name in ['core.c','content.c','render.c','main.c','runtime.c']]+[BUILD/'assets.c']:
    obj=BUILD/(source.stem+'.o');objects.append(str(obj))
    subprocess.run(['arm-none-eabi-gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
start=BUILD/'start.o'
subprocess.run(['arm-none-eabi-gcc','-mcpu=arm7tdmi','-c',str(ROOT/'game/start.s'),'-o',str(start)],check=True)
elf=BUILD/'sf-mini-monsters.elf';rom=BUILD/'sf-mini-monsters.gba'
subprocess.run(['arm-none-eabi-gcc','-mcpu=arm7tdmi','-mthumb-interwork','-nostdlib',
               '-T'+str(ROOT/'game/gba.ld'),str(start),*objects,'-lgcc','-o',str(elf)],check=True)
subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(rom)],check=True)
# Standard cartridge handshake header; this is not a displayed branding asset.
logo=bytes.fromhex('24ffae51699aa2213d84820a84e409ad11248b98c0817f21a352be199309ce2010464a4af82731ec58c7e83382e3cebf85f4df94ce4b09c194568ac01372a7fc9f844d73a3ca9a615897a327fc039876231dc7610304ae56bf38840040a70efdff52fe036f9530f197fbc08560d68025a963be03014e38e2f9a234ffbb3e0344780090cb88113a9465c07c6387f03cafd625e48b380aac7221d4f807')
data=bytearray(rom.read_bytes());data[4:160]=logo
assert len(logo)==156
data[160:172]=b'SF MONSTERS '.ljust(12,b' ')
data[172:176]=b'SFMM';data[176:178]=b'00';data[178]=0x96
data[179:189]=bytes(10);data[189]=(-sum(data[160:189])-0x19)&255
data.extend(bytes((-len(data))%4));rom.write_bytes(data)
public=ROOT/'web/public/game';public.mkdir(parents=True,exist_ok=True)
shutil.copy2(rom,public/rom.name)
print(f'Built {rom.name}: {len(data):,} bytes; valid GBA header.')
