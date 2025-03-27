#!/bin/bash

# THIS IS THE FILE WHICH WILL CONTAIN CALLS TO ALL CRON JOBS

# Source the environment variables
. /home/ec2-user/cron/.env

# Activate the virtual environment
. /home/ec2-user/cron/.venv/bin/activate

# Run the Python script and log output
python3 /home/ec2-user/cron/update_bets.py >> /home/ec2-user/cron/cron.log 2>&1