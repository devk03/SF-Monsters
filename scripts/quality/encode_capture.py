"""Encode native framebuffer captures and measured frame timing for local review."""
from pathlib import Path
import argparse, csv, json, subprocess
ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture',type=Path)
    parser.add_argument('--audio',type=Path)
    parser.add_argument('--silent-diagnostic',action='store_true')
    args=parser.parse_args()
    capture=args.capture.resolve()
    if not capture.is_relative_to(ROOT/'.tools'/'benchmarks'):
        parser.error('Capture must be inside ignored .tools/benchmarks')
    if not args.audio and not args.silent_diagnostic:
        parser.error('Scored comparison requires audio; silent captures are diagnostics only')
    with (capture/'capture.csv').open() as file:
        info=next(csv.DictReader(file))
    frames=int(info['frames']); frequency=int(info['frequency']); cycles=int(info['cycles_per_frame'])
    images=list(capture.glob('*.png'))
    if len(images)!=frames: parser.error('Captured frame count does not match metadata')
    if frames<1 or cycles<1: parser.error('Invalid capture timing')
    output=capture/'review.mp4'
    command=['ffmpeg','-y','-loglevel','warning','-framerate',f'{frequency}/{cycles}',
             '-i',str(capture/'%06d.png')]
    if args.audio: command.extend(['-i',str(args.audio.resolve()),'-c:a','aac','-b:a','192k'])
    command.extend(['-frames:v',str(frames),'-c:v','libx264','-crf','15','-pix_fmt','yuv444p',str(output)])
    subprocess.run(command,check=True)
    report={'frames':frames,'seconds':frames*cycles/frequency,'native_fps':frequency/cycles,
            'audio_present':bool(args.audio),'eligible_for_quality_review':False,
            'purpose':'frame diagnostics; scored review uses encode_native_video.py for native A/V sync',
            'first_frame':int(info['first_frame']),'output':str(output)}
    (capture/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
