#!/bin/bash

harvester_username=harvester
harvester_password=harvester
institution=oxford
machine_ids=(machine1, machine2, machine3)

for machine_id in $machine_ids
do
  docker-compose run --rm galvanalyser_app python manage.py run_harvester \
    --harvester=$harvester_username --password=$harvester_password \
    --machine_id=$machine_id --institution=$institution
done
