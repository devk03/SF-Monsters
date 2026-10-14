"""Finite, line-buffered transport for the unchanged native RAM/function driver."""
import os
import pty
import select
import subprocess
import time


class Driver:
    """Line-buffer the unchanged C driver through a private PTY, never a shell."""
    def __init__(self, executable, rom, state, prefix):
        self.master, slave = pty.openpty()
        self.stderr = prefix.with_suffix('.stderr.txt').open('wb')
        self.process = subprocess.Popen([str(executable), str(rom), str(state)],
            stdin=subprocess.PIPE, stdout=slave, stderr=self.stderr)
        os.close(slave)
        self.pending = b''
        self.deadline = time.monotonic() + 120
        self.commands = prefix.with_suffix('.commands.txt').open('w')
        self.output = prefix.with_suffix('.stdout.txt').open('w')

    def exchange(self, commands, lines):
        if time.monotonic() >= self.deadline:
            raise ValueError('Native pipeline process exceeded its 120-second bound.')
        payload = '\n'.join(commands) + '\n'
        self.commands.write(payload); self.commands.flush()
        self.process.stdin.write(payload.encode()); self.process.stdin.flush()
        result, deadline = [], min(self.deadline, time.monotonic() + 10)
        while len(result) < lines:
            if b'\n' not in self.pending:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not select.select([self.master], [], [], remaining)[0]:
                    raise ValueError('Native pipeline response timeout.')
                try:
                    chunk = os.read(self.master, 65536)
                except OSError as error:
                    raise ValueError('Native pipeline driver exited early.') from error
                if not chunk:
                    raise ValueError('Native pipeline response was truncated.')
                self.pending += chunk
            else:
                line, self.pending = self.pending.split(b'\n', 1)
                value = line.decode().rstrip('\r'); result.append(value)
                self.output.write(value + '\n'); self.output.flush()
        return result

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate(); self.process.wait(timeout=5)
        os.close(self.master); self.stderr.close(); self.commands.close(); self.output.close()


def writes(address, data):
    return [f'write {address + offset:x} {data[offset:offset+1024].hex()}'
            for offset in range(0, len(data), 1024)]

