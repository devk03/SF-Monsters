"""Package a private, provenance-labelled native field-art comparison."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from frame_storage import verify_frames

ROOT=Path(__file__).resolve().parents[2]
REFERENCE='a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af'
CORE='26b7884bc25a5933960f3cdcd98bac1ae14d42e2'


def validate_pair(left,right):
    if left.get('rom_sha256')!=REFERENCE:
        raise ValueError('Left capture must use the user-approved Emerald reference.')
    if right.get('rom_sha256')==REFERENCE or not re.fullmatch('[0-9a-f]{64}',right.get('rom_sha256','')):
        raise ValueError('Right capture must identify a distinct SF cartridge.')
    for capture in (left,right):
        if capture.get('controller_only') is not True or capture.get('trace_only') is not False:
            raise ValueError('Both sides need complete controller-only video captures.')
        if capture.get('mgba_revision')!=CORE or (capture.get('width'),capture.get('height'))!=(240,160):
            raise ValueError('Both sides must use the pinned native GBA core and resolution.')
        if (capture.get('frequency'),capture.get('frame_cycles'))!=(16777216,280896):
            raise ValueError('Comparison must preserve the native GBA clock.')
    for field in ('frames','input_sha256'):
        if left.get(field)!=right.get(field) or not left.get(field):
            raise ValueError('Both sides must use equal frame counts and the same controller sequence.')
    seconds=left['frames']*280896/16777216
    if not 30<=seconds<=60:
        raise ValueError('Field review needs 30–60 seconds of normal gameplay.')
    return seconds


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--left',type=Path,required=True)
    parser.add_argument('--right',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--candidate-label',default='SF OFFICE',
                        help='Visible candidate scene name in uppercase letters and spaces.')
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Z][A-Z ]{1,39}',args.candidate_label):
        parser.error('Candidate label must use 2–40 uppercase letters/spaces.')
    directories=[p.resolve() for p in (args.left,args.right,args.output)]
    for path in directories:path.relative_to(ROOT/'.tools/benchmarks')
    left,right,output=directories
    if output.exists():parser.error('Preserve existing review evidence; choose a new output directory.')
    metadata=[json.loads((path/'capture.json').read_text())for path in (left,right)]
    seconds=validate_pair(*metadata)
    targets=[json.loads(p.read_text()).get('target_sha256') for p in
             list((ROOT/'romhack/releases').glob('*/manifest.json'))+
             list((ROOT/'.tools/romhack-drafts').glob('*/*/manifest.json'))]
    if metadata[1]['rom_sha256'] not in targets:
        parser.error('SF capture must match a verified patch target.')
    for path,data in zip((left,right),metadata):
        verify_frames(path/'capture',data)
        if not (path/'review.mp4').is_file():parser.error('Encode each complete capture first.')
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
                         '-show_entries','stream=width,height,nb_frames','-of','json',str(path/'review.mp4')]))['streams'][0]
        if (probe['width'],probe['height'],int(probe['nb_frames']))!=(240,160,data['frames']):
            parser.error('Encoded review does not match its native capture.')
    output.mkdir()
    labels=['EMERALD LAB  '+metadata[0]['rom_sha256'][:8],
            args.candidate_label+'  '+metadata[1]['rom_sha256'][:8]]
    filters=[]
    for i,label in enumerate(labels):
        filters.append(f'[{i}:v]scale=720:480:flags=neighbor,pad=720:524:0:32:color=0x102333,'+
                       f"drawtext=text='{label}':x=14:y=8:fontsize=16:fontcolor=white[v{i}]")
    filters.append('[v0][v1]hstack=inputs=2[v]')
    video=output/'comparison.mp4'
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n',
                    '-i',str(left/'review.mp4'),'-i',str(right/'review.mp4'),
                    '-filter_complex',';'.join(filters),'-map','[v]','-map','0:a','-map','1:a',
                    '-metadata:s:a:0','handler_name=Emerald reference','-metadata:s:a:1','handler_name=SF candidate',
                    '-c:v','libx264','-crf','15','-pix_fmt','yuv444p','-fps_mode','passthrough',
                    '-c:a','copy','-movflags','+faststart',str(video)],check=True)
    subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-ss','4',
                    '-i',str(video),'-frames:v','1',str(output/'comparison.png')],check=True)
    receipt={'scope':'Interior art/readability and walking presentation only; full domains incomplete',
             'seconds':seconds,'frames_per_side':metadata[0]['frames'],'scale':'equal nearest 3x',
             'same_controller_input':True,'audio_tracks':['Emerald reference','SF candidate'],
             'audio_quality_approval_requested':False,'left':metadata[0],'right':metadata[1],
             'human_approval':'pending','commercial_reference_stays_private':True}
    (output/'comparison.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Private matched field review: {video} ({seconds:.2f}s)')


if __name__=='__main__':main()
