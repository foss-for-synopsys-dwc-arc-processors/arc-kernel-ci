#!/usr/bin/env python3
import shutil
import sys
import time
import logging
import pexpect


def main():
    logging.basicConfig(stream=sys.stderr, format='%(levelname)s: %(message)s',
                        level=logging.INFO)

    if not (len(sys.argv) == 3):
        logging.error("Error: incorrect number of arguments")
        logging.error("""Usage: boot-nsim-image.py <vmlinux> <propsfile>""")
        sys.exit(1)

    kernel = sys.argv[1]
    propsfile = sys.argv[2]

    nsim_path = shutil.which('nsimdrv')
    if nsim_path is None:
        logging.error('nSIM emulator was not found')
        sys.exit(1)

    args = []

    if propsfile:
        args += ['-propsfile', propsfile]

    if kernel:
        args += [kernel]

    child = pexpect.spawn(nsim_path, args, timeout=5, encoding='utf-8')

    child.logfile = sys.stdout
    time.sleep(1)

    try:
        child.expect(['.*login:'], timeout=60)
    except pexpect.EOF as e:
        logging.error("Connection problem, exiting.")
        sys.exit(1)
    except pexpect.TIMEOUT:
        logging.error("System did not boot in time, exiting.")
        sys.exit(1)

    child.sendline("root\r")

    try:
        child.expect(["# "], timeout=60)
    except pexpect.EOF:
        logging.error("Cannot connect to shell")
        sys.exit(1)
    except pexpect.TIMEOUT:
        logging.error("Timeout while waiting for shell")
        sys.exit(1)

    child.sendline("poweroff\r")

    try:
        child.expect(["System halted"], timeout=60)
        child.expect(pexpect.EOF)
    except pexpect.EOF:
        pass
    except pexpect.TIMEOUT:
        logging.error("Cannot halt machine")
    sys.exit(0)


if __name__ == "__main__":
    main()
