"""Run native saved-event migration tests with address/undefined sanitizers."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
output=root/'.tools/cast-resume-tests';output.mkdir(parents=True,exist_ok=True)
folder=Path(tempfile.mkdtemp(prefix='case-',dir=output))
subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror',
                '-fsanitize=address,undefined',str(root/'tests/cast_resume_test.c'),
                '-o',str(folder/'test')],check=True)
subprocess.run([str(folder/'test')],check=True)
