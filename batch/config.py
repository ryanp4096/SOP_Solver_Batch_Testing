from .instance import Instance
from dataclasses import dataclass, asdict, fields

class TraceDetailLevel:
    NORMAL = 0
    COMPACT = 1

@dataclass
class Config:
    time_limit: int = None
    enable_end_lkh: bool = None
    end_lkh: int = None
    threads: int = None
    runs: int = None
    process_best_tour: bool = None
    reuse_thread: bool = None
    finish_lkh_before_bb: bool = None
    process_lkh_subpaths: bool = None
    subpath_history_table: bool = None
    subpath_length_limit: int = None
    lkh_subpaths_only: bool = None
    expected_lkh_cost: int = None
    trace: bool = None
    trace_detail_level: int = None
    background: bool = None
    branch: str = None
    tag: str = None
    
    @classmethod
    def merge(cls, *configs):
        merged = cls()
        merged.set(*configs)
        return merged

    def set(self, *configs, **kwargs):
        for config in configs:
            if config is None: continue
            for f in fields(self):
                x = config.__getattribute__(f.name)
                if x is not None: self.__setattr__(f.name, x)
        
        if kwargs:
            for f in fields(self):
                x = kwargs.get(f.name)
                if x is not None: self.__setattr__(f.name, x)
    
    def config_file(self, instance: Instance):
        return f'''
//Time limit for the input instance (in seconds)
Time_Limit = {self.time_limit}

//Size of the initial global workload pool
Global_Pool_Size = 32

//Assign workload level (total number of levels in the state tree)
Level = {250 if instance.type == 'sop' else 150}

//Memory_Restriction (in % from 0 - 1)
Restrict_Per = 0.9

//History table entry will always be added if depth is below this value
History_depth = -1

//Restart Exploitation/Exploration [%]
Ratio = 50

//Restart Sample Time [s]
Cycle_Time = 3600

//Restart group thread count
Group_Thread_Count = 4

//Work Stealing (1 for enable 0 for disable)
Enable = 1

//Thread Stopping (1 for enable 0 for disable)
Enable = 1

//Run in parallel with LKH (1 for enable 0 for disable)
Enable = 1

//Enable Progress Estimation (1 for enable 0 for disable)
Enable = 1

//Number of buckets for history table
Number_of_Buckets = 1

//Each bucket size for history table (pass 0 to split the entries in each bucket equally)
Bucket_size = 0

//Enable Heuristic: Treat 3 subtable as 1 table if the global pool is empty before hitting the first threshold
Enable = 0

// Stop LKH after this duration and re use the thread in the solver
END_LKH_TIME = {(self.end_lkh or instance.default_end_lkh or -1) if self.enable_end_lkh else -1}

// Time in seconds that decide wheather the LKH entry is stable i.e. unchanged for this amount of time and should be processed
STABLE_LKH_ENTRY_DURATION = 10

// Process the best lkh tour into the history table after lkh end time reached (1 for enable 0 for disable)
PROCESS_LKH_BEST_TOUR = {1 if self.process_best_tour else 0}

// Reuse lkh thread to run branch and bound after lkh end time reached (1 for enable 0 for disable)
REUSE_LKH_THREAD = {1 if self.reuse_thread else 0}

// Finish lkh before starting branch and bound, instead of running in parallel (for debugging) (1 for enable 0 for disable)
FINISH_LKH_BEFORE_BB = {1 if self.finish_lkh_before_bb else 0}

// Process each subpath of the lkh tour as a separate history table entry (1 for enable 0 for disable)
PROCESS_LKH_SUBPATHS = {1 if self.process_lkh_subpaths else 0}

// If trace is enabled, set the detail level of the trace (0 = normal, 1 = compact)
TRACE_DETAIL_LEVEL = {self.trace_detail_level}

// Enable separate history table for subpaths (1 for enable, 0 for disable)
ENABLE_SUBPATH_HISTORY_TABLE = {1 if self.subpath_history_table else 0}

// The maximum length of subpaths included in subpath history table (0 = no limit)
SUBPATH_LENGTH_LIMIT = {self.subpath_length_limit}

// Store only subpaths of LKH's best tour in the history table for faster processing (0 = enable, 1 = disable)
LKH_SUBPATHS_ONLY = {1 if self.lkh_subpaths_only else 0}

// For debugging: Keep running lkh after end time until this cost is reached (0 = disable)
// Only used to get consistent LKH behavior for debugging - do not use in official runs, as expected cost should be unknown
EXPECTED_LKH_COST = {self.expected_lkh_cost}
'''
    
    def dump(self):
        return asdict(self)
    
    @classmethod
    def load(cls, data):
        return cls(**data)


DEFAULT_CONFIG = Config(
    time_limit = 3600,
    enable_end_lkh = True,
    end_lkh = None,
    threads = 32,
    runs = 1,
    process_best_tour = True,
    reuse_thread = True,
    finish_lkh_before_bb = False,
    process_lkh_subpaths = True,
    subpath_history_table = False,
    subpath_length_limit = 0,
    lkh_subpaths_only = False,
    expected_lkh_cost = 0,
    trace = False,
    trace_detail_level = 0,
    background = False,
    branch = None,
    tag = None
)