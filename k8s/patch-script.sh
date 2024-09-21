#!/bin/bash

# Get all CronJobs in the "repcal" namespace
cronjobs=$(kubectl get cronjob --no-headers | awk '{print $1}')
#cronjobs_array=($cronjobs)
# Iterate over each CronJob
for cronjob in $cronjobs; do
  # Create a Job from the CronJob
  kubectl create job ad-hoc-$cronjob --from=cronjob/$cronjob -n repcal
done