"""Reject a world ROM that silently replaces the authored courier with base art."""
import hashlib
import struct
import subprocess


def audit_courier(root, rom, elf):
    symbols = {}
    for line in subprocess.check_output(['arm-none-eabi-nm', '--defined-only', str(elf)], text=True).splitlines():
        fields = line.split()
        if len(fields) == 3:
            symbols[fields[2]] = int(fields[0], 16)
    data = rom.read_bytes()
    directory = root / 'assets/characters/courier-native'
    checked = {}
    for person in ('Brendan', 'May'):
        for mode, suffix in (('walk', 'Normal'), ('run', 'Running')):
            name = 'gObjectEventPic_' + person + suffix
            expected = (directory / (mode + '.4bpp')).read_bytes()
            offset = symbols[name] - 0x08000000
            if offset < 0 or data[offset:offset + len(expected)] != expected:
                raise ValueError('Compiled world avatar differs from authored courier: ' + name)
            checked[name] = hashlib.sha256(expected).hexdigest()
        name = 'gObjectEventGraphicsInfo_' + person + 'Normal'
        offset = symbols[name] - 0x08000000
        if struct.unpack_from('<H', data, offset + 2)[0] != 0x1124:
            raise ValueError('World avatar lost its isolated courier palette: ' + name)
    expected = (directory / 'courier.gbapal').read_bytes()
    offset = symbols['gObjectEventPal_SFCourier'] - 0x08000000
    if data[offset:offset + len(expected)] != expected:
        raise ValueError('Compiled world courier palette differs from authored palette')
    checked['palette'] = hashlib.sha256(expected).hexdigest()
    return {'passed': True, 'resources': checked,
            'scope': 'Exact linked walk/run graphics for both player choices and dedicated normal-view palette; traversal modes beyond walking/running remain separate work'}
