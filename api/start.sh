#!/bin/bash
set -a
source /home/ubuntu/projects/korbanmbg/api/.env
set +a
exec /home/ubuntu/projects/korbanmbg/api/korbanmbg-api
