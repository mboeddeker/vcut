#!/usr/bin/env python


#yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" https://www.youtube.com/watch\?v\=kDCkgdRK5I8

import sys
import subprocess
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio

input_path = sys.argv[1]
out_path = sys.argv[2]
threshold = sys.argv[3] #-25
duration = sys.argv[4] #0.3 oder 1

try:
    ease = float(sys.argv[5])
except IndexError:
    ease = 0.2

minimum_duration = 1.0

def generate_timestamps(path, threshold, duration):
    command = "./detect_silence.sh {} {} {}".format(path, threshold, duration)
    output = subprocess.run(command, shell=True, capture_output=True, text=True)
    return output.stdout.split('\n')[:-1]


def main():
    count = 0
    last = 0
    timestamps = generate_timestamps(input_path, threshold, duration)
    # print("Timestamps: {}".format(timestamps))
    video = VideoFileClip(input_path)
    full_duration = video.duration
    clips = []
    
    for times in timestamps:
        # print("Times: {}".format(times))
        if times == "":
            continue

        if "silence" in times:
            continue


        end,dur = times.strip().split()
        #print("End: {}, Duration: {}".format(end, dur))

        to = float(end) - float(dur) + ease

        start = float(last)
        clip_duration = float(to) - start
        # Clips less than one seconds don't seem to work
        print("Clip Duration: {} seconds".format(clip_duration))

        if clip_duration < minimum_duration:
            continue

        if full_duration - to < minimum_duration:
            continue


        #print("Clip {} (Start: {}, End: {})".format(count, start, to))
        clip = video.subclip(start, to)
        clips.append(clip)
        last = end
        count += 1

    if not clips:
        print("No silence detected, exiting...")
        return


    if full_duration - float(last) > minimum_duration:
        #print("Clip {} (Start: {}, End: {})".format(count, last, 'EOF'))
        clips.append(video.subclip(last))
    rate = clips[0].fps
    print(rate)
    processed_video = concatenate_videoclips(clips, method="chain")

    processed_video.write_videofile(
        out_path,
        fps=rate,
        preset='ultrafast',
        codec='h264_videotoolbox',
        audio_codec='aac',
        threads=32,
        bitrate="4000k"
   )

    video.close()


main()
