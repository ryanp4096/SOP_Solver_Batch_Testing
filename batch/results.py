from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .batch import Batch

import os
from csv import DictWriter

from .script import PatchScript
from .item import Item, Run
from .parse import parse_run, get_median
from .util import read_file


class Results:
    def __init__(self, batch: Batch):
        self.batch = batch
    
    def extract_logs(self):
        self.patch: list[Run] = []
        for item in self.batch.items:
            self.extract_item(item)
        self.batch.to_json()

    def extract_item(self, item: Item):
        item.results = {}
        for i in range(1, item.config.runs + 1):
            if not os.path.exists(f'{item.path}/{i}.log'):
                self.patch.append(Run(item, index = i))
                continue
            result = parse_run(read_file(f'{item.path}/{i}.log'))
            item.results[i] = result
            if not result.final_time:
                self.patch.append(Run(item, index = i))
        
        result = get_median(item.results.values())
        if result: item.results['median'] = result

    def create_table(self):
        rows = []
        for item in self.batch.items:
            for index, result in item.results.items():
                rows.append({
                    'instance': item.instance.name,
                    'run': index,
                    'final_cost': result.final_cost,
                    'final_time': result.final_time,
                    'enumerated_nodes': result.enumerated_nodes,
                    'lkh_find_time': result.lkh_find_time,
                    'lkh_final_cost': result.lkh_final_cost,
                    'global_pool_size': result.global_pool_size,
                    'global_pool_remaining': result.global_pool_remaining,
                    'percent_work_done': result.percent_work_done,
                    'end_lkh': (item.config.end_lkh or item.instance.default_end_lkh or -1) if item.config.enable_end_lkh else -1,
                    'threads': item.config.threads,
                    'time_limit': item.config.time_limit,
                    'branch': item.config.branch,
                    'tag': item.config.tag
                })
        fields = [
            'instance',
            'run',
            'final_cost',
            'final_time',
            'enumerated_nodes',
            'lkh_find_time',
            'lkh_final_cost',
            'global_pool_size',
            'global_pool_remaining',
            'percent_work_done',
            'end_lkh',
            'threads',
            'time_limit',
            'branch',
            'tag'
        ]
        with open(f'{self.batch.path}/results.tsv', 'w', newline='') as file:
            writer = DictWriter(file, fieldnames=fields, delimiter='\t')
            writer.writeheader()
            writer.writerows(rows)
    
    def create_patch(self):
        if not self.patch: return

        script = PatchScript(self.batch, self.patch)
        script.create_builds()
        script.add_runs()
        script.process_results()
        script_path = script.create_file()
        return script_path