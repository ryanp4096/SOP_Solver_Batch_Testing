from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING: from .batch import Batch

import os

class Instance:
    default_end_lkh_table = {
        'ft70.4': 10,
        'p43.3': 5,
        'prob.42': 5,
        'rbg048a': 5,
        'rbg253a': 20,
        'R.200.1000.1': 10,
        'R.300.100.15': 70,
        'R.300.1000.15': 500,
        'R.400.100.15': 440,
        'R.400.1000.15': 130
    }
    time_estimate_table = {
        'ft70.4': 84,
        'p43.3': 1166,
        'prob.42': 43,
        'rbg048a': 316,
        'rbg253a': 96,
        'R.200.1000.1': 100,
        'R.300.100.15': 127,
        'R.300.1000.15': 613,
        'R.400.100.15': 479,
        'R.400.1000.15': 353,
        'ft53.1': 15000,
        'ft53.2': 14000,
        'ft70.1': 11300
    }

    def __init__(self, instance: str, batch: Batch):
        if os.path.exists(f'{batch.sop_solver_path}/tsplib/{instance}.sop'):
            self.path = f'tsplib/{instance}.sop'
            self.type = 'tsp'
            self.name = instance

        elif os.path.exists(f'{batch.sop_solver_path}/soplib/{instance}.sop'):
            self.path = f'soplib/{instance}.sop'
            self.type = 'sop'
            self.name = instance

        elif os.path.exists(f'{batch.sop_solver_path}/tsplib/{instance}'):
            self.path = f'tsplib/{instance}'
            self.type = 'tsp'
            self.name = instance.split('.sop')[0]

        elif os.path.exists(f'{batch.sop_solver_path}/soplib/{instance}'):
            self.path = f'soplib/{instance}'
            self.type = 'sop'
            self.name = instance.split('.sop')[0]

        else:
            raise Exception(f'Instance {instance} not found')
        
        self.default_end_lkh = Instance.default_end_lkh_table.get(self.name)
        self.time_estimate = Instance.time_estimate_table.get(self.name)

    def dump(self):
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type
        }
    
    @classmethod
    def load(cls, data, batch):
        return cls(data['name'], batch)