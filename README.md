# pager
# Assumptions:
    1. service name is of the format: xxx-[a-zA-Z]+
    2. service instance-id is of format [a-zA-Z0-9]+
    3. Text in the log is utf-8 encoded
    4. Log file to be processed ends in ".txt"

# How to Execute
    1. Script can be executed using following command OR
        ``` python3 process_log.py
    2. A docker container can be started using following command:
        ``` docker run -d sandeepsingh2103/pager:0.1
        # image is available as public image on docker hub
        https://cloud.docker.com/repository/docker/sandeepsingh2103/pager/general 

# How to check output
    It prints the required output for each processed file on stdout.
    
# How it works
This python3 script processes log file based on following requirement: https://gist.github.com/cilindrox/c2da38fe4daddbc9d2a509fc1625714a.
At the start up containers creates a directory called "input" and "output" under $HOME directory if it doesn't exist. Thereafter it continues to monitor the input directory for any .txt files and puts them to $HOME/output/ after processing them until the container/process is stopped or killed.
    
# Concurrency and File Size
This script utliizes Python's ProcessPoolExecutor module to spawn multiple worker processes which processes multiples file concurrently.By  default it spawns 5 processes and goes to read the input directory every time after finishing. In order to minimize the memory footrpint this script uses a memory mapped file.
     
# Not covered
    RESTful api is not created.
