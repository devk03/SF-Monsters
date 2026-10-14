"""Package three observed native music loops; reference recordings stay private."""
import argparse
from array import array
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import wave

ROOT=Path(__file__).resolve().parents[2]
REFERENCE='a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af'
CORE='26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
FRAME_SECONDS=280896/16777216


def loop_boundaries(rows,rom,ticks):
    """Require actual first-track GOTO instructions, not arbitrary backward jumps."""
    boundaries=[]
    if not rows or ticks<=0:raise ValueError('Missing music trace or invalid loop ticks.')
    for index,row in enumerate(rows):
        if row['capture_frame']!=index:
            raise ValueError('Need uninterrupted first-track observation.')
        if row['status']&0x80000000 or not row['status']&1:
            raise ValueError('Music paused or the observed first track stopped.')
        if index==0:continue
        previous=rows[index-1]
        if (row['song'],row['track'])!=(previous['song'],previous['track']):
            raise ValueError('Song/track changed during the listening capture.')
        if not 0<=row['clock']-previous['clock']<=2:
            raise ValueError('Music clock reset or skipped beyond the supported tempo.')
        if row['command']>=previous['command']:continue
        # Calls/returns may move the cursor backward without looping the song.
        if row['pattern_level'] or previous['pattern_level']:continue
        offset=previous['command']-0x08000000
        if not 0<=offset<len(rom)-5 or rom[offset]!=0xb2:
            raise ValueError('Backward cursor jump is not a native GOTO opcode.')
        target=struct.unpack_from('<I',rom,offset+1)[0]
        if not 0x08000000<=target<=row['command']<previous['command']:
            raise ValueError('Native GOTO target does not explain the observed cursor.')
        boundaries.append({'frame':index,'clock':row['clock'],
                           'goto':previous['command'],'target':target})
    if len(boundaries)<4:raise ValueError('Need four observed boundaries for three complete loops.')
    for before,after in zip(boundaries,boundaries[1:]):
        if (before['goto'],before['target'])!=(after['goto'],after['target']) or \
           after['clock']-before['clock']!=ticks:
            raise ValueError('Loop address or native tick period changed.')
    return boundaries


def load_capture(directory,cartridge,ticks):
    directory=directory.resolve();directory.relative_to(ROOT/'.tools/benchmarks')
    metadata=json.loads((directory/'capture.json').read_text())
    rom=cartridge.read_bytes()
    if hashlib.sha256(rom).hexdigest()!=metadata['rom_sha256']:
        raise ValueError('Cartridge identity differs from the captured audio.')
    if metadata.get('controller_only') is not True or metadata.get('mgba_revision')!=CORE or \
       not metadata.get('runtime','').startswith('native mGBA') or not metadata.get('music_observation'):
        raise ValueError('Need pinned controller-only native music observation.')
    if (metadata['frequency'],metadata['frame_cycles'])!=(16777216,280896):
        raise ValueError('Native GBA clock differs.')
    trace=(directory/'capture.music.csv').read_bytes()
    rows=[{k:int(v) for k,v in row.items()} for row in csv.DictReader(trace.decode().splitlines())]
    if len(rows)!=metadata['frames']:raise ValueError('Incomplete per-frame music trace.')
    boundaries=loop_boundaries(rows,rom,ticks)
    pcm=(directory/'capture.pcm').read_bytes();rate=metadata['sample_rate']
    if len(pcm)!=metadata['audio_samples']*4 or \
       abs(metadata['audio_samples']/rate-metadata['frames']*FRAME_SECONDS)>.001:
        raise ValueError('Native PCM completeness/clock check failed.')
    # Preserve extra audio around frame-resolved events; do not claim sample-exact phase.
    padding=.25
    start=max(0,round((boundaries[0]['frame']*FRAME_SECONDS-padding)*rate))
    end=min(metadata['audio_samples'],round(((boundaries[3]['frame']+1)*FRAME_SECONDS+padding)*rate))
    excerpt=pcm[start*4:end*4];samples=array('h',excerpt)
    if sys.byteorder!='little':samples.byteswap()
    peak=max(map(abs,samples));rms=math.sqrt(sum(v*v for v in samples)/len(samples))
    if not rms or peak>=32767:raise ValueError('Silent or clipped review audio.')
    receipt={'capture':str(directory.relative_to(ROOT)),'rom_sha256':metadata['rom_sha256'],
             'input_sha256':metadata['input_sha256'],'state_input_sha256':metadata.get('state_input_sha256'),
             'pcm_sha256':hashlib.sha256(pcm).hexdigest(),'trace_sha256':hashlib.sha256(trace).hexdigest(),
             'music_observation':metadata['music_observation'],'loop_ticks':ticks,'boundaries':boundaries,
             'first_three_periods_seconds':[(b['frame']-a['frame'])*FRAME_SECONDS
                                          for a,b in zip(boundaries[:3],boundaries[1:4])],
             'command_boundary_frame_resolution_seconds':FRAME_SECONDS,'padding_seconds':padding,
             'audio_phase':'Frame-resolved event with uncalibrated audio-buffer alignment; not sample-exact',
             'sample_bounds':[start,end],
             'raw_rms':rms,'raw_peak':peak,'sample_rate':rate,
             'observed_first_track_periods':3,'other_tracks_runtime_cursors_observed':False}
    return excerpt,receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for side in ('reference','candidate'):
        parser.add_argument('--'+side,type=Path,required=True)
        parser.add_argument('--'+side+'-rom',type=Path,required=True)
        parser.add_argument('--'+side+'-ticks',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve()
    output.relative_to(ROOT/'.tools/benchmarks')
    if output.exists():parser.error('Preserve existing evidence; choose a new output directory.')
    captures=[load_capture(getattr(args,side),getattr(args,side+'_rom'),getattr(args,side+'_ticks'))
              for side in ('reference','candidate')]
    if captures[0][1]['rom_sha256']!=REFERENCE or captures[1][1]['rom_sha256']==REFERENCE:
        parser.error('Use the genuine reference on the left and a distinct SF candidate.')
    target_rms=min(item[1]['raw_rms'] for item in captures)
    output.mkdir()
    for side,(pcm,receipt) in zip(('reference','candidate'),captures):
        raw=output/(side+'-three-loops-raw.wav')
        with wave.open(str(raw),'wb') as audio:
            audio.setnchannels(2);audio.setsampwidth(2);audio.setframerate(receipt['sample_rate'])
            audio.writeframes(pcm)
        gain=target_rms/receipt['raw_rms'];receipt['review_gain']=gain
        receipt['gain_db']=20*math.log10(gain)
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-i',str(raw),
                        '-af',f'volume={gain:.12f}','-ar','48000','-codec:a','libmp3lame','-q:a','2',
                        str(output/(side+'-three-loops-level-matched.mp3'))],check=True)
    (output/'review.json').write_text(json.dumps({
        'scope':'Clinic soundtrack subset; no human quality approval inferred',
        'gain_method':'One constant RMS-matching gain per whole excerpt; no limiter/crossfade',
        'reference_stays_private':True,'click_underrun_performance_gate':'not established',
        'human_approval':'pending','reference':captures[0][1],'candidate':captures[1][1]},indent=2)+'\n')
    print('Three observed first-track periods per side; raw WAVs and separate listening copies:',output)


if __name__=='__main__':main()
