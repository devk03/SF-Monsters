"""Lossless storage for native frame evidence; never discard captured pixels."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import uuid

ROOT = Path(__file__).resolve().parents[2]
FRAME_BYTES = 240 * 160 * 4


def digest_stream(stream):
    digest, size = hashlib.sha256(), 0
    while block := stream.read(1024 * 1024):
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def verify_frames(prefix, metadata):
    path = prefix.with_suffix('.rgba')
    storage = metadata.get('video_storage', {'encoding': 'raw'})
    encoding = storage['encoding']
    if encoding not in ['raw', 'gzip']:
        raise ValueError('Unknown native frame storage encoding.')
    opener = gzip.open if encoding == 'gzip' else open
    with opener(path, 'rb') as stream:
        digest, size = digest_stream(stream)
    if size != metadata['frames'] * FRAME_BYTES:
        raise ValueError('Incomplete native frame data.')
    if encoding == 'gzip' and (digest != storage['sha256'] or size != storage['bytes']):
        raise ValueError('Stored native frames failed lossless integrity verification.')
    return digest, size


def compress_capture(directory):
    directory = Path(directory).resolve()
    directory.relative_to(ROOT / '.tools/benchmarks')
    prefix = directory / 'capture'
    metadata_path = prefix.with_suffix('.json')
    metadata = json.loads(metadata_path.read_text())
    if metadata['trace_only']:
        raise ValueError('Trace-only captures have no video to compress.')
    if metadata.get('video_storage', {}).get('encoding') == 'gzip':
        verify_frames(prefix, metadata)
        return 0
    digest, size = verify_frames(prefix, metadata)
    path = prefix.with_suffix('.rgba')
    # Keep the original until the compressed copy decodes to exactly its bytes.
    # Failed temporary copies remain available for diagnosis; nothing is removed.
    candidate = path.with_name(path.name + '.lossless-' + uuid.uuid4().hex)
    with open(path, 'rb') as source, gzip.open(candidate, 'wb', compresslevel=9) as output:
        while block := source.read(1024 * 1024):
            output.write(block)
    with gzip.open(candidate, 'rb') as source:
        if digest_stream(source) != (digest, size):
            raise ValueError('Compression changed native frame evidence; original retained.')
    storage = {'encoding': 'gzip', 'sha256': digest, 'bytes': size}
    # A receipt permits recovery if interrupted between replacement and metadata.
    receipt = candidate.with_suffix(candidate.suffix + '.json')
    receipt.write_text(json.dumps({'destination': str(path), **storage}) + '\n')
    compressed_size = candidate.stat().st_size
    os.replace(candidate, path)
    metadata['video_storage'] = storage
    staged_metadata = metadata_path.with_name(metadata_path.name + '.lossless-' + uuid.uuid4().hex)
    staged_metadata.write_text(json.dumps(metadata, indent=2) + '\n')
    os.replace(staged_metadata, metadata_path)
    verify_frames(prefix, metadata)
    return size - compressed_size


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    saved = compress_capture(args.directory)
    print(f'Preserved every native frame; frame storage shrank by {saved / 1024 / 1024:.1f} MiB.')
