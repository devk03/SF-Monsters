"""Native dimensions and centered seam alignment for larger destinations.

Keep contributor interiors and connectors independently sized. Connection
offsets are measured in the source map's perpendicular coordinate axis.
"""

DESTINATION_SIZE = (96, 64)
LEGACY_SIZE = (32, 24)
MIN_DESTINATION_AREA = 32 * 24 * 8


def destination_ids(manifest):
    result = {area['id'] for area in manifest['areas']}
    if manifest['league'].get('venue'):
        result.add(manifest['league']['venue'])
    return result


def dimensions(manifest, identifier):
    rooms = {room['id']: room for room in manifest.get('interiors', [])}
    if identifier in rooms:
        return tuple(rooms[identifier].get('size', LEGACY_SIZE))
    spec = manifest.get('destination_geometry')
    if spec and identifier in destination_ids(manifest):
        width, height = spec['width'], spec['height']
        if (type(width) is not int or type(height) is not int
                or width < 32 or height < 24
                or width * height < MIN_DESTINATION_AREA):
            raise ValueError('Destination geometry must provide at least6144 tiles')
        return width, height
    return manifest['geometry']['width'], manifest['geometry']['height']


def connection_offset(direction, source_size, target_size):
    if direction not in ('up', 'down', 'left', 'right'):
        raise ValueError('Unknown native connection direction')
    axis = 0 if direction in ('up', 'down') else 1
    return source_size[axis] // 2 - target_size[axis] // 2


def connection_point(direction, point, source_size, target_size):
    """Translate a source boundary tile into its reciprocal destination tile."""
    offset = connection_offset(direction, source_size, target_size)
    x, y = point
    if direction == 'up':
        return x - offset, target_size[1] - 1
    if direction == 'down':
        return x - offset, 0
    if direction == 'left':
        return target_size[0] - 1, y - offset
    return 0, y - offset
