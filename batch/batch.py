import os
import json
from copy import copy
from datetime import datetime
from dataclasses import asdict, dataclass

from .config import Config, DEFAULT_CONFIG
from .util import format_time_estimate, get_git_branch
from .instance import Instance
from .item import Item
from .script import Script
from .results import Results


@dataclass
class BatchSettings:
    time_estimate: bool = True
    shuffle: bool = False
    sort: bool = False


class Batch:
    def __init__(self, sop_solver_path, results_path='./tests', name: str = None):
        if not os.path.exists(sop_solver_path): raise Exception(f"Could not find path {sop_solver_path}")
        if not os.path.exists(results_path):
            if results_path == './tests': os.mkdir('tests')
            else: raise Exception(f"Could not find path {results_path}")
        
        self.sop_solver_path = os.path.abspath(sop_solver_path)
        self.results_path = os.path.abspath(results_path)
        
        self.config = copy(DEFAULT_CONFIG)
        self.config.branch = get_git_branch(self.sop_solver_path)
        self.index = 0
        self.items: list = []
        self.timestamp = datetime.now()
        self.name = name
        self.date = None
        self.id = None
        self.path = None
        self.settings = BatchSettings()
    
    def next_index(self):
        self.index += 1
        return self.index
    
    def add(self, instance: str, *configs: Config, **kwargs):
        self.items.append(Item.create(self, Instance(instance, self), *configs, Config(**kwargs)))

    def wait_background(self):
        if not self.items: return
        self.items[-1].wait_background = True

    def total_time_estimate(self):
        unknown = set()
        background_time = 0
        time_elapsed = 0
        
        for item in self.items:
            if item.config.background:
                est = item.individual_time_estimate()
                if est is not None and est > background_time:
                    background_time = est
            else:
                est = item.time_estimate()
                if est is not None:
                    time_elapsed += est
                    background_time -= est
                    if background_time < 0: background_time = 0
            if est is None:
                unknown.add(item.instance.name)
            
            if item.wait_background:
                time_elapsed += background_time
                background_time = 0
        
        time_elapsed += background_time
        
        return time_elapsed, unknown

    def create(self):
        print(f'Batch: {len(self.items)} items, {sum(item.config.runs for item in self.items)} runs')
        if self.settings.time_estimate:
            estimate, unknown = self.total_time_estimate()
            line = format_time_estimate(estimate, short=False)
            if len(unknown) > 0:
                line += f", plus unknown time from {len(unknown)} instances: {', '.join(unknown)}"
            print(f'Time Estimate: {line}')
        for item in self.items:
            tag = f" [{item.config.tag}]" if item.config.tag else ""
            print(f'{item.index}. {item.instance.name}{tag} ({item.config.runs} runs)')
        name = input('Enter name to create: ')
        if name: self.name = name

        self.create_directory()
        for item in self.items:
            item.create_directory()
        self.to_json()

        script = Script(self)
        script.build()
        script_path = script.create_file()
        print('Run this script to start the tests: ' + script_path)

    def process(self):
        results = Results(self)
        results.extract_logs()
        results.create_table()
        patch_path = results.create_patch()
        if patch_path:
            print(f'{len(results.patch)} unfinished runs detected')
            print('Run this script to fix these the tests: ' + patch_path)

    def create_directory(self):
        self.date = self.timestamp.strftime("%Y-%m-%d")
        date_folder = os.path.join(self.results_path, self.date)
        if not os.path.exists(date_folder): os.mkdir(date_folder)
        
        self.id = self.timestamp.strftime("%H%M")
        if self.name: self.id += f'_{self.name}'
        if os.path.exists(os.path.join(date_folder, self.id)):
            alt = 1
            while os.path.exists(os.path.join(date_folder, f'{self.id}_{alt}')): alt += 1
            self.id = f'{self.id}_{alt}'
        
        self.path = os.path.join(date_folder, self.id)
        os.mkdir(self.path)

    def dump(self):
        return {
            'name': self.name,
            'date': self.date,
            'id': self.id,
            'sop_solver_path': self.sop_solver_path,
            'results_path': self.results_path,
            'path': self.path,
            'timestamp': self.timestamp.isoformat(),
            'items': [item.dump() for item in self.items],
            'settings': asdict(self.settings)
        }
    
    @classmethod
    def load(cls, data):
        batch = cls(sop_solver_path = data['sop_solver_path'], results_path = data['results_path'])
        batch.name = data['name']
        batch.date = data['date']
        batch.id = data['id']
        batch.path = data['path']
        batch.timestamp = datetime.fromisoformat(data['timestamp'])
        batch.items = [
            Item.load(item, batch) for item in data['items']
        ]
        batch.settings = BatchSettings(**data['settings'])
        return batch

    def to_json(self):
        with open(f'{self.path}/data.json', 'w') as file:
            json.dump(self.dump(), file)

    @classmethod
    def from_json(cls, path):
        with open(f'{path}/data.json') as file:
            data = json.load(file)
        return cls.load(data)