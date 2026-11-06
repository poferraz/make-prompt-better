"""Run a real terminal CLI with bounded, prompt-driven input."""
import os
import pty
import select
import subprocess
import time


def terminal_session(command, *, cwd, home, answers=(), env=None, timeout=20, input_data=None):
    master, slave = pty.openpty()
    child_env = dict(os.environ, HOME=str(home), **(env or {}))
    process = subprocess.Popen(command, cwd=cwd, env=child_env,
                               stdin=slave if input_data is None else subprocess.PIPE,
                               stdout=slave, stderr=slave)
    os.close(slave)
    if input_data is not None:
        process.stdin.write(input_data)
        process.stdin.close()
    output = b''
    pending = list(answers)
    cursor = 0
    deadline = time.monotonic() + timeout
    try:
        while True:
            if time.monotonic() >= deadline:
                raise AssertionError(f'Terminal session timed out: {output.decode(errors="replace")}')
            ready, _, _ = select.select([master], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                output += chunk
                if pending and pending[0][0] in output[cursor:]:
                    _, response = pending.pop(0)
                    cursor = len(output)
                    if isinstance(response, int):
                        process.send_signal(response)
                    else:
                        os.write(master, response)
            elif process.poll() is not None:
                break
        process.wait(timeout=5)
        return subprocess.CompletedProcess(command, process.returncode, output.decode(errors='replace'), '')
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        os.close(master)
