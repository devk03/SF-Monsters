"""Verify cartridge return masks from linked map/event bytes, independently."""
def check_masks(read, table, index, identity, width, height, blocks, actors, triggers, exits, sides):
    group, number, w, h, *pointers = read(table + index * 16, '4B3I')
    if (group, number, w, h) != (*identity, width, height):
        return ['compiled return-mask identity or dimensions differ']
    occupied = set()
    for x, y, rx, ry in actors:
        occupied.update((a, b) for a in range(x-rx, x+rx+1) for b in range(y-ry, y+ry+1))
    forbidden = occupied | (set(triggers) - set(exits))
    seeds = set(exits)
    for side in sides:
        if side in (1, 2):
            seeds.update((width//2+d, height-1 if side == 1 else 0) for d in (-1, 0, 1))
        else:
            seeds.update((0 if side == 3 else width-1, height//2+d) for d in (-1, 0, 1))
    errors = []
    for stage, pointer in zip((0, 5, 8), pointers):
        available = set()
        for offset, block in enumerate(blocks):
            point = (offset % width, offset // width)
            tile = block & 1023
            if block & 0xC00 or point in forbidden: continue
            if tile == 368 and stage < 5 or tile == 179 and stage < 8: continue
            available.add(point)
        reachable = seeds & available
        frontier = list(reachable)
        while frontier:
            x, y = frontier.pop()
            for point in ((x, y-1), (x, y+1), (x-1, y), (x+1, y)):
                if point in available and point not in reachable:
                    reachable.add(point)
                    frontier.append(point)
        expected = bytearray((width*height+7)//8)
        for x, y in reachable:
            expected[(y*width+x)//8] |= 1 << ((y*width+x)%8)
        if bytes(read(pointer, str(len(expected))+'B')) != expected:
            errors.append(f'compiled return mask differs at traversal stage {stage}')
    return errors
