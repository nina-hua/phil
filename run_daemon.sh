#!/bin/bash
source activate /home/ec2-user/.conda/envs/phil
cd /home/ec2-user/product-analytics-group-project-phil-minus-phil/code/
gunicorn --bind 0.0.0.0:8080 run_app -D
