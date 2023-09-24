# audio_timer

example launch script

```
#!/bin/bash
set -euxo pipefail
cd /home/$USER/audio_timer
source /home/$USER/anaconda3/etc/profile.d/conda.sh 

conda activate torch

python web_server.py & python zero_shot_audio_rtsp.py

```
