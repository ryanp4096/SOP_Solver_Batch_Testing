from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .batch import Batch

import random
import os
import stat

from .config import DEFAULT_CONFIG
from .item import Run, Build
from .util import format_time_estimate, write_file

CREATE_BUILD_FUNCTION = """
create_build() {
    (
        set -e
        local branch=$1 custom=${2:-}
        [[ $# -ge 2 ]] && shift 2 || shift
        make clean
        git checkout $branch
        make $@ || { git checkout -; exit 1; }
        git checkout -
        mv sop_solver "$BUILDS/$branch$custom"
    ) &>> "$LOG"
}
"""


class Script:
    def __init__(self, batch: Batch):
        self.lines: list = []
        self.batch = batch
        self.log_path = f'{self.batch.path}/output.log'
        self.script_name = "run.sh"

        self.current_run = 0
        self.total_runs = sum(item.config.runs for item in self.batch.items)
        
        if self.batch.settings.time_estimate:
            self.total_time_estimate = 0
            for item in self.batch.items:
                est = item.time_estimate()
                if est is not None: self.total_time_estimate += est
            
    def build(self):
        self.append('#!/bin/bash')
        self.append(f"SOP_SOLVER={self.batch.sop_solver_path}") # set variables with paths
        self.append(f"RESULTS={self.batch.path}")
        self.append("LOG=$RESULTS/output.log")
        self.append(f"PYTHON={os.getcwd()}")
        self.append('')

        self.create_builds()
        self.add_runs()
        self.process_results()
    
    def create_builds(self, builds: set = None):
        if builds is None: builds = set(item.get_build() for item in self.batch.items)

        self.append("set -e")
        self.append("BUILDS=$(mktemp -d)")
        self.append('''trap 'rm -rf "$BUILDS"' EXIT''')
        self.append('cd "$SOP_SOLVER"')
        self.append(CREATE_BUILD_FUNCTION)
        
        for i, build in enumerate(builds):
            if build.trace:
                self.echo(f"Creating Build for {build.branch} (trace enabled) ({i+1}/{len(builds)})")
                self.append(f'create_build {build.branch} +t ENABLE_TRACE=1')
            else:
                self.echo(f"Creating Build for {build.branch} ({i+1}/{len(builds)})")
                self.append(f'create_build {build.branch}')
            self.append('')
        
        self.append('set +e')
        self.append('')

    def add_runs(self):
        runs: list = []
        items = self.batch.items
        if self.batch.settings.sort:
            items = items.copy()
            items.sort(key=lambda item: item.individual_time_estimate())

        for item in items:
            runs += item.create_runs()
        if self.batch.settings.shuffle:
            random.shuffle(runs)
            for item in items: item.run_index = 0 # reassign run indexes in order
            for run in runs: run.index = run.item.next_index()

        for run in runs:
            self.add_run(run)


    def add_run(self, run: Run):
        self.current_run += 1
        
        l = f'[{self.current_run}/{self.total_runs}]'
        l += f'  {run.item.index}. {run.item.instance.name}'
        if run.item.config.tag: l += f' [{run.item.config.tag}]'
        l += f'  ({run.index}/{run.item.config.runs})'
        if self.batch.settings.time_estimate: l += f'  ({format_time_estimate(self.total_time_estimate)} remaining)'
        # l += f'  {run.item.path}/{run.index}.log'
        self.echo(l)

        if self.batch.settings.time_estimate:
            est = run.time_estimate()
            if est is not None: self.total_time_estimate -= est
        
        trace_indicator = '+t' if run.item.config.trace else ''
        build = f'"$BUILDS/{run.item.config.branch}{trace_indicator}"'
        instance_path = run.item.instance.path
        thread_count = run.item.config.threads
        config_path = f'"$RESULTS/{run.item.id}/config.txt"'
        log_path = f'"$RESULTS/{run.item.id}/{run.index}.log"'
        trace_path = f'"$RESULTS/{run.item.id}/{run.index}_trace.bin"' if run.item.config.trace else ''
        self.append(f'{build} {instance_path} {thread_count} {config_path} {trace_path} > {log_path}')
        self.append('')

    def append(self, line: str):
        self.lines.append(line)

    def echo(self, line: str):
        self.append(f'''echo "{line}" | tee -a "$LOG"''')

    def process_results(self):
        self.append('set -e')
        self.echo("Processing Results")
        self.append('cd "$PYTHON"')
        self.append(f'python3 -m batch.process "$RESULTS"')
        self.echo("Batch Completed")
        
        table_path = f'{self.batch.path}/results.tsv'
        rel_path = './' + os.path.relpath(table_path, os.getcwd())
        if len(rel_path) <= len(table_path): table_path = rel_path

        self.echo(f'Go to \\"{table_path}\\" to view results')

    def create_file(self):
        script_path = f'{self.batch.path}/{self.script_name}'
        rel_path = './' + os.path.relpath(script_path, os.getcwd())
        if len(rel_path) <= len(script_path): script_path = rel_path
        write_file(script_path, '\n'.join(self.lines) + '\n')
        os.chmod(script_path, os.stat(script_path).st_mode | stat.S_IXUSR)
        return script_path
    
class PatchScript(Script):
    def __init__(self, batch: Batch, runs: list):
        super().__init__(batch)

        self.current_run = 0
        self.patch_runs = runs
        self.total_runs = len(self.patch_runs)
        self.script_name = "patch.sh"
        
        if self.batch.settings.time_estimate:
            self.total_time_estimate = 0
            for run in self.patch_runs:
                est = run.time_estimate()
                if est is not None: self.total_time_estimate += est

    def create_builds(self, builds: set = None):
        if builds is None: builds = set(run.item.get_build() for run in self.patch_runs)
        super().create_builds(builds=builds)

    def add_runs(self):
        runs: list = self.patch_runs.copy()
        if self.batch.settings.shuffle:
            random.shuffle(runs)

        for run in runs:
            self.add_run(run)
