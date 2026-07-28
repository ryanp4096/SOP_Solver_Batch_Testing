import statistics
import subprocess

def write_file(path: str, content: str):
    with open(path, 'w') as file:
        file.write(content)

def read_file(path: str):
    with open(path) as file:
        content = file.read()
    return content

def get_git_branch(cwd=None):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except Exception as e:
        return None

def total_time_estimate(estimates: list):
    total_seconds = 0
    unknown_instances = set()

    for instance, seconds in estimates:
        if seconds is None: unknown_instances.add(instance)
        else: total_seconds += seconds
    
    line = format_time_estimate(total_seconds, short=False)
    if len(unknown_instances) > 0:
        line += f", plus unknown time from {len(unknown_instances)} instances: {', '.join(unknown_instances)}"
    
    return line

def format_time_estimate(seconds: int, short=True):
    seconds = round(seconds)

    if short:
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    else:
        if seconds < 60:
            return f"{seconds} secs"
        elif seconds < 3600:
            return f"{seconds // 60} mins, {seconds % 60} secs"
        else:
            return f"{seconds // 3600} hrs, {(seconds % 3600) // 60} mins"
        
def median_helper(lst):
    lst = [x for x in lst if x is not None]
    if not lst: return None
    else: return statistics.median(lst)

def match_helper(lst):
    lst = [x for x in lst if x is not None]
    if not lst: return None
    for x in lst:
        if x != lst[0]: return None
    return lst[0]
