"""Encode raw native-core A/V at the original GBA rate, preserving synchronization."""
from pathlib import Path
import argparse
import json
import subprocess
import gzip
import uuid
from frame_storage import verify_frames

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory', type=Path)
args = parser.parse_args()
directory = args.directory.resolve()
directory.relative_to(ROOT / '.tools/benchmarks')
prefix = directory / 'capture'
metadata = json.loads(prefix.with_suffix('.json').read_text())
if metadata['trace_only']:
    parser.error('This capture contains no video.')
duration = metadata['frames'] * metadata['frame_cycles'] / metadata['frequency']
audio_duration = metadata['audio_samples'] / metadata['sample_rate']
if abs(duration - audio_duration) > 0.001:
    parser.error('Native video/audio clocks disagree by more than 1 ms.')
try:
    verify_frames(prefix, metadata)
except (ValueError, OSError) as error:
    parser.error(str(error))
if prefix.with_suffix('.pcm').stat().st_size != metadata['audio_samples'] * 4:
    parser.error('Incomplete native audio data.')
output = directory / 'review.mp4'
if output.exists():
    output = directory / ('review-' + uuid.uuid4().hex[:10] + '.mp4')
rate = f'{metadata["frequency"]}/{metadata["frame_cycles"]}'
compressed = metadata.get('video_storage', {}).get('encoding') == 'gzip'
command = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-n',
    '-f', 'rawvideo', '-pixel_format', 'rgba', '-video_size', '240x160',
    '-framerate', rate, '-i', 'pipe:0' if compressed else str(prefix.with_suffix('.rgba')),
    '-f', 's16le', '-ar', str(metadata['sample_rate']), '-ac', '2',
    '-i', str(prefix.with_suffix('.pcm')), '-c:v', 'libx264', '-crf', '15',
    '-pix_fmt', 'yuv444p', '-fps_mode', 'passthrough', '-c:a', 'aac',
    '-b:a', '192k', '-movflags', '+faststart', str(output)]
if compressed:
    with subprocess.Popen(command, stdin=subprocess.PIPE) as process:
        with gzip.open(prefix.with_suffix('.rgba'), 'rb') as frames:
            while block := frames.read(1024 * 1024):
                process.stdin.write(block)
        process.stdin.close()
        if process.wait():
            raise subprocess.CalledProcessError(process.returncode, command)
else:
    subprocess.run(command, check=True)
metadata.update({
    'clip': str(output.relative_to(ROOT)), 'seconds': duration,
    'audio_video_skew_ms': (audio_duration - duration) * 1000,
    'eligible_duration_for_review': 30 <= duration <= 60,
    'contains_audible_signal': metadata.get('audio_peak', 0) > 0,
    'user_quality_approval': 'pending'
})
(directory / 'review.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(f'Encoded {duration:.2f}s native 240x160 A/V: {output}')
