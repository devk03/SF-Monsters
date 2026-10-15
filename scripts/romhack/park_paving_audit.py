"""Independent decoded South Park paving delta; no visual or gameplay approval."""
import hashlib
import json
from pathlib import Path
import struct

BASELINE={
    'tiles.4bpp':('gTilesetTiles_SFSouthPark',16096,'1028cc530238a128ba379d2de5f8153cdbf2eb6c1054f67501f5e4900ce2b6c8'),
    'metatiles.bin':('gMetatiles_SFSouthPark',2400,'c5a357ba4d453bb0e856b09a594334303b50ead542ef7081b92a243a7269a0c8'),
    'attributes.bin':('gMetatileAttributes_SFSouthPark',300,'5d75b62c2517473238cfe7967401f492d506a41ffbbd5de58ea9c99ad39eab2f'),
    'palettes.gbapal':('gTilesetPalettes_SFSouthPark',512,'73e3ba1b6d1f0a9385e97e92eba6a4a2d1268384e4cdf6f45f452a49fda512db'),
}
GRAY_PALETTE=struct.pack('<16H',0,27|(27<<5)|(27<<10),23|(23<<5)|(23<<10),*([0]*13))
BASELINE_ROM='9335199708e8d38a95d705074f8f6e38c340026a83d7a1318f9fb8972de821f7'


def sha(data):return hashlib.sha256(data).hexdigest()


def paving_quadrant(record,quadrant):
    return (record in (16,19) and quadrant>=4) or (40<=record<150 and quadrant<4)


def candidate_quadrants(pixels):
    if len(pixels)!=256 or any(v not in (1,2) for v in pixels):
        raise ValueError('Paving must be256 opaque bank4 indices1/2.')
    quadrants=[bytes(pixels[(qy*8+y)*16+qx*8+x] for y in range(8) for x in range(8))
               for qy in range(2) for qx in range(2)]
    if len(set(quadrants))!=1:raise ValueError('Paving must repeat one native8x8 master in16x16.')
    return quadrants


def validate_resources(resources):
    raw,records,attrs,palettes=resources
    if not 0<len(raw)<=504*32 or len(raw)%32 or len(records)!=150*16 or len(attrs)!=150*2 or len(palettes)!=512:
        raise ValueError('Require150 records/attributes,512 palette bytes and1..504 resident8x8 tiles.')


def decode_quadrant(raw,word):
    tile=(word&1023)-512
    if tile<0 or tile>=len(raw)//32 or (word&1023)>=1016:
        raise ValueError('Quadrant leaves resident secondary tiles or enters reserved door VRAM.')
    return bytes((raw[tile*32+(7-y if word&0x800 else y)*4+(7-x if word&0x400 else x)//2] >>
                  (4*((7-x if word&0x400 else x)%2)))&15 for y in range(8) for x in range(8))


def compare_paving(baseline,actual,pixels):
    """Compare all1200 native quadrant roles, accepting tile repacking/flips."""
    validate_resources(baseline);validate_resources(actual)
    candidates=candidate_quadrants(pixels)
    raw,records,attrs,palettes=actual
    old_raw,old_records,old_attrs,old_palettes=baseline
    checks=[]
    def compare(name,expected,value,**details):
        checks.append({'name':name,'passed':expected==value,'expected_sha256':sha(expected),
                       'actual_sha256':sha(value),**details})
    compare('all150_attributes',old_attrs,attrs)
    compare('all512_palette_bytes',old_palettes,palettes)
    checked,paving,literal=0,0,0
    for record in range(150):
        row={'name':'metatile_%03d'%record,'passed':False,'quadrants':8}
        expected,observed=bytearray(),bytearray()
        try:
            for quadrant in range(8):
                old=struct.unpack_from('<H',old_records,record*16+quadrant*2)[0]
                word=struct.unpack_from('<H',records,record*16+quadrant*2)[0]
                tile=old&1023
                if tile==0 or tile>=1016:
                    # Primary blank and nonresident animated-door words have no
                    # secondary pixels. Preserve all bits instead of inventing art.
                    expected.extend(b'L'+struct.pack('<H',old));observed.extend(b'L'+struct.pack('<H',word));literal+=1
                else:
                    old_pixels=decode_quadrant(old_raw,old)
                    target=paving_quadrant(record,quadrant)
                    expected.extend(b'R'+bytes([4 if target else old>>12])+(candidates[quadrant%4] if target else old_pixels))
                    observed.extend(b'R'+bytes([word>>12])+decode_quadrant(raw,word))
                    paving+=int(target)
                checked+=1
            row.update(passed=expected==observed,expected_sha256=sha(expected),actual_sha256=sha(observed))
        except (ValueError,struct.error) as error:row['error']=str(error)
        checks.append(row)
    return {'passed':all(row['passed'] for row in checks),'checks':checks,
            'counts':{'total':len(checks),'matched':sum(row['passed'] for row in checks),
                      'logical_quadrants_checked':checked,'paving_quadrants':paving,
                      'exact_nonresident_words':literal,'resident_tiles':len(raw)//32}}


def audit_paving(rom,elf,root):
    from check_creature_resources import Cartridge,decode_lz
    result={'passed':False,'checks':[],'counts':{'total':0,'matched':0},'hashes':{},'errors':[],
            'quality_approval':'pending','scope':'All150 South Park metatiles decoded against frozen original SF v74 art; '
            'only ground16/19 upper and facade40..149 lower quadrants may change to bank4 grayscale paving. '
            'No visual, animation, collision, map binding, save, campaign or performance approval.'}
    def source(path):
        data=path.read_bytes();result['hashes'][str(path)]=sha(data);return data
    try:
        result['hashes'].update(rom=sha(rom.read_bytes()),elf=sha(elf.read_bytes()))
        source(Path(__file__));source(Path(__file__).parents[1]/'quality/check_creature_resources.py')
        directory=Path(root)/'assets/tiles/south-park-paving-v1'
        receipt=json.loads(source(directory/'baseline-v74/receipt.json'))
        if receipt.get('target_sha256')!=BASELINE_ROM or set(receipt.get('files',{}))!=set(BASELINE):
            raise ValueError('Require the exact original-only v74 resource baseline receipt.')
        baseline=[]
        for filename,(symbol,length,digest) in BASELINE.items():
            data=source(directory/'baseline-v74'/filename)
            if len(data)!=length or sha(data)!=digest or receipt['files'][filename]!={'symbol':symbol,'bytes':length,'sha256':digest}:
                raise ValueError('Frozen original baseline differs: '+filename)
            baseline.append(data)
        pixels=source(directory/'paving.indices')
        gray=source(directory/'paving.gbapal')
        if gray!=GRAY_PALETTE:
            raise ValueError('Paving source must be exact neutral RGB555 gray27/23,transparent0 and thirteen zero colors.')
        cart=Cartridge(rom,elf)
        actual=[cart.data(symbol) for symbol,_,_ in BASELINE.values()]
        actual[0]=decode_lz(actual[0])
        result.update(compare_paving(tuple(baseline),tuple(actual),pixels))
        primary=cart.data('gTilesetPalettes_SFParkFrontage')
        if len(primary)!=512:raise ValueError('Require the complete512-byte primary palette allocation.')
        bank=primary[128:160]
        row={'name':'primary_paving_gray_bank4','passed':bank==GRAY_PALETTE,
             'expected_sha256':sha(GRAY_PALETTE),'actual_sha256':sha(bank)}
        result['checks'].append(row)
        result['counts']['total']+=1;result['counts']['matched']+=int(row['passed'])
        result['passed']=result['passed'] and row['passed']
    except (OSError,ValueError,TypeError,KeyError,struct.error) as error:
        result['passed']=False;result['errors'].append(str(error))
    return result
