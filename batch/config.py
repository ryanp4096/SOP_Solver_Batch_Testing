from .instance import Instance

class Config:
    def __init__(
            self,
            time_limit: int = None,
            enable_end_lkh: bool = None,
            end_lkh: int = None,
            threads: int = None,
            runs: int = None,
            process_best_tour: bool = None,
            reuse_thread: bool = None,
            finish_lkh_before_bb: bool = None,
            process_lkh_subpaths: bool = None,
            trace: bool = None,
            branch: str = None,
            tag: str = None
        ):
        self.time_limit = time_limit
        self.enable_end_lkh = enable_end_lkh
        self.end_lkh = end_lkh
        self.threads = threads
        self.runs = runs
        self.process_best_tour = process_best_tour
        self.reuse_thread = reuse_thread
        self.finish_lkh_before_bb = finish_lkh_before_bb
        self.process_lkh_subpaths = process_lkh_subpaths
        self.trace = trace
        self.branch = branch
        self.tag = tag

    @classmethod
    def merge(cls, *configs):
        merged = cls()
        for config in configs:
            if config is None: continue
            merged.set(
                time_limit = config.time_limit,
                enable_end_lkh = config.enable_end_lkh,
                end_lkh = config.end_lkh,
                threads = config.threads,
                runs = config.runs,
                process_best_tour = config.process_best_tour,
                reuse_thread = config.reuse_thread,
                finish_lkh_before_bb = config.finish_lkh_before_bb,
                process_lkh_subpaths = config.process_lkh_subpaths,
                trace = config.trace,
                branch = config.branch,
                tag = config.tag
            )
        return merged

    def set(
            self,
            time_limit: int = None,
            enable_end_lkh: bool = None,
            end_lkh: int = None,
            threads: int = None,
            runs: int = None,
            process_best_tour: bool = None,
            reuse_thread: bool = None,
            finish_lkh_before_bb: bool = None,
            process_lkh_subpaths: bool = None,
            trace: bool = None,
            branch: str = None,
            tag: str = None
        ):
        if time_limit is not None: self.time_limit = time_limit
        if enable_end_lkh is not None: self.enable_end_lkh = enable_end_lkh
        if end_lkh is not None: self.end_lkh = end_lkh
        if threads is not None: self.threads = threads
        if runs is not None: self.runs = runs
        if process_best_tour is not None: self.process_best_tour = process_best_tour
        if reuse_thread is not None: self.reuse_thread = reuse_thread
        if finish_lkh_before_bb is not None: self.finish_lkh_before_bb = finish_lkh_before_bb
        if process_lkh_subpaths is not None: self.process_lkh_subpaths = process_lkh_subpaths
        if trace is not None: self.trace = trace
        if branch is not None: self.branch = branch
        if tag is not None: self.tag = tag
    
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
'''
    
    def dump(self):
        return {
            'time_limit': self.time_limit,
            'enable_end_lkh': self.enable_end_lkh,
            'end_lkh': self.end_lkh,
            'threads': self.threads,
            'runs': self.runs,
            'process_best_tour': self.process_best_tour,
            'reuse_thread': self.reuse_thread,
            'finish_lkh_before_bb': self.finish_lkh_before_bb,
            'process_lkh_subpaths': self.process_lkh_subpaths,
            'trace': self.trace,
            'branch': self.branch,
            'tag': self.tag
        }
    
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
    trace = False,
    branch = None,
    tag = None
)