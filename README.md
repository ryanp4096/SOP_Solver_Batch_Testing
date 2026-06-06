# SOP_Solver Batch Testing
A Python module to run batch tests for [SOP_Solver](https://github.com/jacobnormington/SOP_Solver).

Generates shell scripts to automatically runs a batch of tests, then parse the log files into a data table.

## Usage
- Create the file `main.py` and add the following:
  ```py
  from batch import Batch, Config

  batch = Batch("/path/to/sop_solver/directory")

  # Set the global configuration for all instances
  batch.config.set(time_limit=3600, end_lkh=20)

  # Add specific instances to run. Each instance can have own configuration settings to override global configuration
  batch.add('ft70.4', end_lkh=10)
  batch.add('prob.42', end_lklh=5, time_limit=100)

  batch.create()

  ```
- Then, run the program using `python3 main.py` to generate a shell script.
- Copy and paste the path to the shell script into the command line to run the tests.