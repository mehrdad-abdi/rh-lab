"""runs one Python program in an isolated process and returns status (pass, fail, error, timeout), exit code and truncated output"""

import os
import signal
import subprocess
import sys
import resource


def _set_limits():
    # Limit CPU time to 5 seconds (soft limit, hard limit)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

    # Limit virtual memory (address space) to 1 GB
    max_mem = 1024 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))


def run_python_process_limited(program: str, timeout: int = 5):
    # Run the Python program in a subprocess
    proc = subprocess.Popen(
        [sys.executable, "-s", "-E", program],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
        preexec_fn=_set_limits,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)

        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

        stdout, stderr = proc.communicate()
        raise TimeoutError(f"Command timed out after {timeout}s; process group killed.")


def run_in_docker(
    cmds: list[str],
    out_dir: str = "output/docker_out",
    image: str = "rh-sandbox:1",
    extra: list = None,
):
    if not extra:
        extra = []
    project = os.getcwd()
    out = os.path.abspath(out_dir)
    os.makedirs(out, exist_ok=True)
    cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--memory",
        "4g",
        "--cpus",
        "4",
        "--pids-limit",
        "512",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,size=1g",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "-v",
        f"{project}:/work:ro",  # code: read-only
        "-v",
        f"{out}:/out",  # results: the only writable mount
        "-w",
        "/work",
        *extra,
        image,
        *cmds,
    ]

    subprocess.run(cmd, check=True)
