#!/bin/bash

# ... (Parameter Mapping is the same) ...
DEVICE="/dev/video4"
WIDTH=1280
HEIGHT=720
PIX_FMT=MJPG
FPS=10

BRIGHTNESS=0
CONTRAST=24              # <--- Critical Color Control
SATURATION=64            # <--- Critical Color Control
GAIN=0
WHITE_BALANCE_TEMP=4624
SHARPNESS=3
AUTO_EXPOSURE=1
EXPOSURE_TIME=150
FOCUS_ABSOLUTE=250
FOCUS_AUTO_CONTINUOUS=0
WHITE_BALANCE_AUTO=0


# 1. Set the Format, Frame Rate, and Less-Volatile Manual Controls
#    We keep the color format (MJPG) here, and sharpenss/white balance.
v4l2-ctl -d "$DEVICE" \
    --set-parm=1/"$FPS" \
    --set-fmt-video=width="$WIDTH",height="$HEIGHT",pixelformat="$PIX_FMT" \
    --set-ctrl=sharpness="$SHARPNESS" \
    --set-ctrl=white_balance_automatic="$WHITE_BALANCE_AUTO" \
    --set-ctrl=white_balance_temperature="$WHITE_BALANCE_TEMP"

# 2. Add a short delay to allow the camera to process the format change
echo "Waiting for camera to stabilize settings..."
sleep 0.5

# 3. Re-Lock CRITICAL and VOLATILE Controls (Focus, Exposure, and COLOR)
#    Adding color controls here ensures they are set immediately before capture.
v4l2-ctl -d "$DEVICE" \
    --set-ctrl=brightness="$BRIGHTNESS" \
    --set-ctrl=contrast="$CONTRAST" \
    --set-ctrl=saturation="$SATURATION" \
    --set-ctrl=gain="$GAIN" \
    --set-ctrl=auto_exposure="$AUTO_EXPOSURE" \
    --set-ctrl=exposure_time_absolute="$EXPOSURE_TIME" \
    --set-ctrl=focus_automatic_continuous="$FOCUS_AUTO_CONTINUOUS" \
    --set-ctrl=focus_absolute="$FOCUS_ABSOLUTE"

# 4. Capture the single frame
echo "Capturing image..."
v4l2-ctl -d "$DEVICE" \
    --stream-mmap --stream-count=1 --stream-to=./.images/test.jpg