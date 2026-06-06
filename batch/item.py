from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .batch import Batch

import os
from dataclasses import asdict

from .instance import Instance
from .config import Config, DEFAULT_CONFIG
from .util import write_file
from .parse import ParsedRun

class Item:
    def __init__(self, index: int, batch: Batch, instance: Instance, config: Config, path: str, id: str, results: dict):
        self.index = index
        self.batch = batch
        self.instance = instance
        self.config = config
        self.path = path
        self.id = id
        self.run_index = 0
        self.results = results

    @classmethod
    def create(cls, batch, instance: Instance, *configs: Config):
        return cls(
            index = batch.next_index(),
            batch = batch,
            instance = instance,
            config = Config.merge(DEFAULT_CONFIG, batch.config, *configs),
            path = None,
            id = None,
            results = None
        )
    
    def individual_time_estimate(self):
        if self.instance.time_estimate is None: return
        estimate = self.instance.time_estimate * (32 / self.config.threads)
        if estimate > self.config.time_limit: estimate = self.config.time_limit
        return estimate
    
    def time_estimate(self):
        est = self.individual_time_estimate()
        if est is None: return
        return est * self.config.runs

    def create_runs(self):
        return [
            Run(self)
            for i in range(self.config.runs)
        ]
    
    def create_directory(self):
        self.id = f'{self.index}_{self.instance.name}'
        self.path = f'{self.batch.path}/{self.id}'
        os.mkdir(self.path)
        write_file(f'{self.path}/config.txt', self.config.config_file(self.instance))

    def next_index(self):
        self.run_index += 1
        return self.run_index
    
    def dump(self):
        return {
            'index': self.index,
            'instance': self.instance.dump(),
            'config': self.config.dump(),
            'path': self.path,
            'id': self.id,
            'results': {index: asdict(result) for index, result in self.results.items()} if self.results else None
        }
    
    @classmethod
    def load(cls, data, batch):
        return cls(
            index = data['index'],
            batch = batch,
            instance = Instance.load(data['instance'], batch),
            config = Config.load(data['config']),
            path = data['path'],
            id = data['id'],
            results = {index: ParsedRun(**result) for index, result in data['results'].items()} if data['results'] else None
        )


class Run:
    def __init__(self, item: Item, index: int = None):
        self.item = item
        if index is None:
            self.index = item.next_index()
        else:
            self.index = index

    def time_estimate(self):
        return self.item.individual_time_estimate()