#!/bin/bash

VPS_PUBLIC_IP=<YOUR.VPS.PUBLIC.IP>

# run preswald deploy to generate dist, immediately stop container
preswald deploy
docker ps -q --filter "publish=8501" | xargs -r docker stop

# copy dist content to vps
scp -r ./.preswald_deploy root@$VPS_PUBLIC_IP:/root

# run vps_entry
ssh -t root@$VPS_PUBLIC_IP <<EOF
cd ./.preswald_deploy
bash vps_entry.sh
EOF

exit 0