scluster
========
Simple tool that clusters files based on ssdeep distances. Results are output as JSON and can be grouped on disk when an output path is specified.
Suitale to be used as a standalone script or imported
Installation
============
    git clone https://github.com/0xab00d/scluster
    sudo apt-get install python-dev libfuzzy-dev
    pip install -r requirements.txt

Examples
========

help
----
    usage: scluster.py [-h] [-o [OUTPUT]] [-v] [-t [THRESHOLD]] input [input ...]

    simple file clustering using ssdeep

    positional arguments:
      input                 input path

    optional arguments:
      -h, --help            show this help message and exit
      -o [OUTPUT], --output [OUTPUT]
                            output path
      -v, --verbose         increase output verbosity
      -t [THRESHOLD], --threshold [THRESHOLD]
                            specify minimum ssdeep distance threshold in range 0
                            to 100. Default 60


