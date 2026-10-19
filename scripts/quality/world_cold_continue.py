"""Observe native menu/field readiness instead of sending extra A presses."""
import struct


def cold_continue(c):
    def callback():
        return struct.unpack('<I', c.read(c.symbols['gMain'] + 4, 4))[0] & ~1

    def menu_ready():
        target = c.symbols['Task_HandleMainMenuInput'] & ~1
        for n in range(16):
            task = c.read(c.symbols['gTasks'] + n * 40, 5)
            if task[4] and (struct.unpack_from('<I', task)[0] & ~1) == target:
                return True
        return False

    c.step(0, 180)
    for _ in range(30):
        if menu_ready():
            break
        c.tap(8, 90)  # Historical cartridges may still have an attract/title.
    else:
        raise ValueError('Native Continue menu did not become ready')
    c.picture('continue-menu')
    c.tap(1, 90)
    for _ in range(60):
        if callback() == (c.symbols['CB2_Overworld'] & ~1):
            c.step(0, 180)
            return
        c.step(0, 30)
    raise ValueError('Native Continue did not restore the field')
