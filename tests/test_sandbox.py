import subprocess

import pytest
import os
import uuid
from rh_lab.helpers.sandbox import run_python_process_limited, run_in_docker


@pytest.fixture
def python_file_maker():
    files = []

    def _make_python_file(content: str, filename: str = None):
        if filename is None:
            filename = f"temp_{uuid.uuid4().hex}.py"
        with open(filename, "w") as f:
            f.write(content)
        files.append(filename)
        return filename

    yield _make_python_file
    for filename in files:
        os.remove(filename)


def test_process_limited_success(python_file_maker):
    # Test a simple Python program that should pass
    filename = python_file_maker("print('Hello, World!')")
    returncode, stdout, stderr = run_python_process_limited(filename, timeout=1)
    assert returncode == 0
    assert stdout.strip() == "Hello, World!"
    assert stderr == ""


def test_process_limited_failure(python_file_maker):
    # Test a Python program that should fail
    filename = python_file_maker("import sys; sys.exit(1)")
    returncode, stdout, stderr = run_python_process_limited(filename, timeout=1)
    assert returncode == 1


def test_process_limited_timeout(python_file_maker):
    # Test a Python program that should timeout
    filename = python_file_maker("while True: pass")
    with pytest.raises(TimeoutError):
        run_python_process_limited(filename, timeout=1)


def test_run_in_docker_success(python_file_maker):
    # Test a simple Python program that should pass in Docker
    filename = python_file_maker("print('Hello from Docker!')")
    run_in_docker(["python", filename], out_dir="output/docker_out")


def test_run_in_docker_raise(python_file_maker):
    filename = python_file_maker("raise ValueError('This should fail')")
    with pytest.raises(subprocess.CalledProcessError):
        run_in_docker(["python", filename], out_dir="output/docker_out")


def test_run_in_docker_exit_code(python_file_maker):
    filename = python_file_maker("import sys; sys.exit(1)")
    with pytest.raises(subprocess.CalledProcessError):
        run_in_docker(["python", filename], out_dir="output/docker_out")


def test_run_in_docker_readonly(python_file_maker):
    filename = python_file_maker(
        "with open('test.txt', 'w') as f: f.write('This should fail')"
    )
    with pytest.raises(subprocess.CalledProcessError):
        run_in_docker(["python", filename], out_dir="output/docker_out")

    filename = python_file_maker(
        "with open('/work/test.txt', 'w') as f: f.write('This should fail')"
    )
    with pytest.raises(subprocess.CalledProcessError):
        run_in_docker(["python", filename], out_dir="output/docker_out")


def test_run_in_docker_writable(python_file_maker):
    out_dir = "output/tests_out"
    text = "This should work"
    filename = python_file_maker(
        f"with open('/out/test.txt', 'w') as f: f.write('{text}')"
    )

    run_in_docker(["python", filename], out_dir=out_dir)
    assert os.path.exists(f"{out_dir}/test.txt")
    assert open(f"{out_dir}/test.txt").read() == text

    os.remove(f"{out_dir}/test.txt")
