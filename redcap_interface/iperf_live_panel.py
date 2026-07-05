#!/usr/bin/env python3

import os
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
target = os.path.join(script_dir, "bash_library", "fc_iperf_live_panel.py")
os.execv(sys.executable, [sys.executable, target, *sys.argv[1:]])
