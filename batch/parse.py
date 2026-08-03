from dataclasses import dataclass
import re

from .util import median_helper, match_helper

@dataclass
class ParsedRun:
    instance: str
    final_cost: int
    final_time: float
    enumerated_nodes: int
    lkh_find_time: float
    lkh_final_cost: int
    global_pool_size: int
    global_pool_remaining: int
    percent_work_done: float


def parse_run(run_text: str):
    # Instance name
    instance_match = re.search(r'Input file is .*\/(.+?\.sop)', run_text)
    if not instance_match:
        instance_match = re.search(r'^(.*\.sop)', run_text, re.MULTILINE)
    instance = instance_match.group(1).strip() if instance_match else 'Unknown'

    # LKH best entry Cost
    # lkh_costs = re.findall(
    #     r'Best Cost temp\s*=\s*(\d+)\s+updated by LKH', run_text)
    # final_lkh_cost = float(lkh_costs[-1]) if lkh_costs else None
    lkh_cost_match = re.search(r'Processing Best Tour with cost: (\d+)', run_text)
    final_lkh_cost = float(lkh_cost_match.group(1)) if lkh_cost_match else None

    # Time taken for LKH to find its best entry
    lkh_find_time = re.findall(r'setting last updated at.*?([\d.]+)', run_text)
    final_lkh_find_time = float(lkh_find_time[-1]) if lkh_find_time else None

    # Enumerated nodes
    nodes_match = re.search(r'Total enumerated nodes:\s+(\d+)', run_text)
    enumerated_nodes = int(nodes_match.group(1)) if nodes_match else None

    # Extract gp const
    gp_const_match = re.search(r'gp const:\s*(\d+)', run_text, re.IGNORECASE)
    gp_const = int(gp_const_match.group(1)) if gp_const_match else None

    # Extract gp remaining
    gp_remaining_match = re.search(
        r'gp remaining:\s*(\d+)', run_text, re.IGNORECASE)
    gp_remaining = int(gp_remaining_match.group(
        1)) if gp_remaining_match else None

    # Extract percentage of work done
    percent_work_done_match = re.search(
        r'Percentage of work done:\s*((\d|\.)+)%', run_text, re.IGNORECASE)
    percent_work_done = float(percent_work_done_match.group(
        1)) if percent_work_done_match else None

    # Final Cost and Param (line after active time)
    final_cost, final_time = None, None

    # cost and time appear after "active time: ..."
    active_time_pattern = re.compile(
        r'active time:\s*[\d.]+\s*\n([^\n]+)', re.MULTILINE)

    active_line_match = active_time_pattern.search(run_text)

    if active_line_match:
        try:
            values = [v.strip()
                      for v in active_line_match.group(1).split(",") if v.strip()]
            # Parse as float or int as needed
            if len(values) >= 2:
                try:
                    final_cost = int(float(values[0]))
                except Exception as e:
                    final_cost = int(float(values[0].split(' ')[1]))
                final_time = float(values[1])
        except Exception as e:
            print("Error parsing final cost/time:", e)
    # During reserch more parameters might be needed to make a meaningful conclusion, or formatting in the log file might change, so just update it accordingly
    return ParsedRun(
        instance = instance,
        final_cost = final_cost,
        final_time = final_time,
        enumerated_nodes = enumerated_nodes,
        lkh_find_time = final_lkh_find_time,
        lkh_final_cost = final_lkh_cost,
        global_pool_size = gp_const,
        global_pool_remaining = gp_remaining,
        percent_work_done = percent_work_done
    )

def get_median(runs: list):
    if len(runs) <= 1: return
    return ParsedRun(
        instance = match_helper(r.instance for r in runs),
        final_cost = match_helper(r.final_cost for r in runs),
        final_time = median_helper(r.final_time for r in runs),
        enumerated_nodes = median_helper(r.enumerated_nodes for r in runs),
        lkh_find_time = median_helper(r.lkh_find_time for r in runs),
        lkh_final_cost = median_helper(r.lkh_final_cost for r in runs),
        global_pool_size = median_helper(r.global_pool_size for r in runs),
        global_pool_remaining = median_helper(r.global_pool_remaining for r in runs),
        percent_work_done = median_helper(r.percent_work_done for r in runs)
    )