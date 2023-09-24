from transformers import pipeline
import subprocess as sp
import time
import os
import glob

candidate_labels = ["piano", "singing", "noise", "silence"]

pipe = pipeline(
    task="zero-shot-audio-classification",
    model="laion/clap-htsat-unfused",  # , device=0
)


def classify_audio_0(filepath):
    try:
        start = time.time()
        preds = pipe(filepath, candidate_labels=candidate_labels)
        print("time:", time.time() - start)
    except ValueError as e:
        print(f"An error occurred: {e}")
        return {"noise": 1}
    outputs = {}
    for p in preds:
        outputs[p["label"]] = p["score"]
    return outputs


tmdir = "/dev/shm/audio/"
if not os.path.exists(tmdir):
    os.makedirs(tmdir)

command = [
    "ffmpeg",
    "-loglevel",
    "error",
    "-i",
    "rtsp://admin:password@10.0.0.53:554/subaddress",
    "-acodec",
    "pcm_s32le",
    "-f",
    "segment",
    # "-ar",    # "44100",  # ouput will have 44100 Hz
    "-segment_time",
    "10",
    "-segment_format",
    "wav",
    "-strftime",
    "1",
    tmdir + "%m%dT%H%M%S.wav",
    # "-ac",    "1",  # stereo (set to '1' for mono)
    # "-",
]
print(" ".join(command))

sub_p = sp.Popen(
    command,
    stdout=sp.PIPE,
    bufsize=10**8,
)

import shutil
from pathlib import Path


is_piano = False
counter = {}
for label in candidate_labels:
    counter[label] = 0


def UpdateCounter(result):
    counter[result] += 10
    print(counter)
    print("\t", score)
    f = open(tmdir + "counter", "w")
    for key, value in counter.items():
        if value > 0:
            m, s = divmod(value, 60)
            f.write(key + " : " + str(m) + " min " + str(s) + " sec\n")
    f.close()


while True:
    wav_files = glob.glob(os.path.join(tmdir, "*.wav"))
    if len(wav_files) <= 1:
        time.sleep(1)
        continue
    input = min(wav_files)
    score = classify_audio_0(input)
    result = max(score, key=score.get)
    if is_piano != (result == "piano") or counter[result] == 0:
        is_piano = result == "piano"
        shutil.move(input, "done/" + Path(input).stem + "_" + result + ".wav")
    else:
        os.remove(input)
    UpdateCounter(result)
