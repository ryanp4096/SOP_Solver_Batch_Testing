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
        'rbg253a': 25, # 20
        'R.200.1000.1': 15, # 10    # not optimal
        'R.300.100.15': 70,         # not optimal
        'R.300.1000.15': 500,       # not optimal
        'R.400.100.15': 440,        # not optimal
        'R.400.1000.15': 130,       # not optimal
        'ESC78': 60,
        'ft53.1': 60,
        'ft53.2': 60,
        'ft53.3': 60,
        'ft70.1': 60,
        'ft70.3': 60,
        'p43.1': 60,
        'p43.2': 60,
        'R.200.100.15': 180,
        'ry48p.1': 60,
        'rbg358a': 540,
        'ft70.2': 60,       # reaches best known upper bound
        'kro124p.1': 60,    # reaches best known upper bound
        'kro124p.2': 60,    # reaches best known upper bound
        'kro124p.3': 100,   # reaches best known upper bound
        'kro124p.4': 60,    # reaches best known upper bound
        'ry48p.2': 60,      # reaches best known upper bound
        'ry48p.3': 60,      # reaches best known upper bound
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
        'ft70.1': 11300,
        'R.200.100.15': 130,
        'R.200.1000.15': 74,
        'R.500.100.15': 1487,
        'R.500.1000.1': 1769,
        'R.500.1000.15': 1721,
        'R.600.100.15': 1073,
        'R.600.1000.1': 1192,
        'R.700.100.15': 3092,
        'br17.10': 1,
        'br17.12': 1,
        'ESC07': 1,
        'ESC11': 1,
        'ESC12': 1,
        'ESC25': 1,
        'ESC47': 1,
        'ESC63': 1,
        'ft53.4': 3,
        'p43.4': 1,
        'R.200.100.1': 5,
        'R.200.100.30': 1,
        'R.200.100.60': 1,
        'R.200.1000.30': 1,
        'R.200.1000.60': 1,
        'R.300.100.1': 3,
        'R.300.100.30': 1,
        'R.300.100.60': 1,
        'R.300.1000.1': 11,
        'R.300.1000.30': 1,
        'R.300.1000.60': 1,
        'R.400.100.1': 5,
        'R.400.100.30': 1,
        'R.400.100.60': 1,
        'R.400.1000.30': 2,
        'R.400.1000.60': 1,
        'R.500.100.1': 18,
        'R.500.100.30': 3,
        'R.500.100.60': 1,
        'R.500.1000.30': 3,
        'R.500.1000.60': 1,
        'R.600.100.1': 19,
        'R.600.100.30': 4,
        'R.600.100.60': 2,
        'R.600.1000.30': 5,
        'R.600.1000.60': 1,
        'R.700.100.1': 26,
        'R.700.100.30': 7,
        'R.700.100.60': 2,
        'R.700.1000.30': 6,
        'R.700.1000.60': 3,
        'rbg050c': 9,
        'rbg109a': 1,
        'rbg150a': 1,
        'rbg174a': 8,
        'ry48p.4': 2,
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