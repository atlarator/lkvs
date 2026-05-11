#!/usr/bin/python3

# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2026 Intel Corporation

# Author: Kai Zhang <kai.zhang@intel.com>
#
# History:  May. 2026 - Kai Zhang - creation

import hexdump
import random
import re
import time

from provider import dmesg_router  # pylint: disable=unused-import
from avocado.utils import process
from virttest import error_context, env_process
from provider.cpu_utils import check_cpu_flags


@error_context.context_aware
def run(test, params, env):
    """
    TDX QGS socket test:
    1. Boot TDVM
    2. Pin a TD VM to a cpu, poweroff the cpu and shutdown the TD VM

    :param test: QEMU test object
    :param params: Dictionary with the test parameters
    :param env: Dictionary with test environment.
    """

    with open("/tmp/tsm_report.sh", "w") as f:
        f.write("#!/bin/sh\n")
        f.write("report=/sys/kernel/config/tsm/report/report0\n")
        f.write("mkdir -pv $report\n")
        f.write("dd if=/dev/urandom bs=64 count=1 > \"$report\"/inblob\n")

    params["start_vm"] = "yes"
    env_process.preprocess_vm(test, params, env, params["main_vm"])
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = params.get_numeric("login_timeout", 240)
    session = vm.wait_for_login(timeout=timeout)

    vm.copy_files_to("/tmp/tsm_report.sh", "/tmp/tsm_report.sh")
    session.cmd("chmod +x /tmp/tsm_report.sh")
    session.cmd("/tmp/tsm_report.sh")
    report_path = params.get("report_path")
    vm.copy_files_from(f"{report_path}/outblob", "/tmp/outblob")
    with open("/tmp/outblob", "rb") as f:
        hexdump.hexdump(f.read())

    # process.run("rm -f /tmp/tsm_report.sh /tmp/outblob")
    session.close()
