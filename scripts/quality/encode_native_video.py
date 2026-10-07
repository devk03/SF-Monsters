"""Prepare a scored-review excerpt from mGBA's synchronized native A/V recording."""
from pathlib import Path
import argparse, json, subprocess
ROOT=Path(__file__).resolve().parents[2]

def probe(path):
    result=subprocess.check_output(['ffprobe','-v','error','-show_streams',
        '-show_format','-of','json',str(path)],text=True)
    return json.loads(result)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recording',type=Path)
    parser.add_argument('--start',type=float,default=0)
    parser.add_argument('--seconds',type=float,default=45)
    parser.add_argument('--name',required=True)
    args=parser.parse_args()
    path=args.recording.resolve()
    if not path.is_relative_to(ROOT/'.tools'/'benchmarks'):
        parser.error('Keep reference recordings inside ignored .tools/benchmarks')
    if not 30<=args.seconds<=60 or args.start<0:
        parser.error('Review excerpts must be 30–60 seconds with a nonnegative start')
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in args.name):
        parser.error('Name must use lowercase letters, numbers, hyphens or underscores')
    source=probe(path)
    video=next((s for s in source['streams'] if s['codec_type']=='video'),None)
    audio=next((s for s in source['streams'] if s['codec_type']=='audio'),None)
    if not video or not audio: parser.error('Native recording must contain both video and audio')
    if (video['width'],video['height'])!=(240,160):
        parser.error('Record at native 240x160 so the comparison preserves original pixels')
    available=float(source['format']['duration'])
    if available+0.02<args.start+args.seconds: parser.error('Recording is shorter than the requested excerpt')
    output=path.parent/f'{args.name}.mp4'
    if output.exists(): parser.error('Use a new name to preserve previous review evidence')
    subprocess.run(['ffmpeg','-loglevel','warning','-ss',str(args.start),'-i',str(path),
        '-t',str(args.seconds),'-map','0:v:0','-map','0:a:0','-fps_mode','passthrough',
        '-c:v','libx264','-crf','15','-pix_fmt','yuv444p','-c:a','aac','-b:a','192k',str(output)],check=True)
    encoded=probe(output)
    report={'source':str(path),'output':str(output),'source_start_seconds':args.start,
        'seconds':float(encoded['format']['duration']),'source_frame_rate':video['avg_frame_rate'],
        'source_av_sync_preserved':True,'user_quality_approval':'pending'}
    (output.with_suffix('.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
