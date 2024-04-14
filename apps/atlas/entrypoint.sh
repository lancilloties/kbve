#!/bin/bash

# Ensure the X11 and VNC related files are cleaned up properly
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 $XAUTHORITY
touch $XAUTHORITY
xauth generate $DISPLAY . trusted 2>/dev/null

# Start Virtual Frame Buffer in the background
# Added `-ac` to disable access control, i.e., allow connections from any host
# You might need to be careful with security implications of -ac in a production environment
Xvfb $DISPLAY -screen 0 1280x800x24 -ac &  

# Wait a bit to make sure Xvfb starts
sleep 5

# Set up a password for VNC connection
mkdir -p ~/.vnc
x11vnc -storepasswd 12345 ~/.vnc/passwd

# Start the VNC server
# Added `-noxdamage` to avoid issues with compositing window managers that might cause the black screen
# Added `-verbose` for more detailed logs which might help in diagnosing issues
x11vnc -display $DISPLAY -auth $XAUTHORITY -forever -usepw -create -noxdamage -verbose &

# Start the noVNC server
websockify -D --web=/usr/share/novnc/ 6080 localhost:5900 &

# Execute the command passed to the docker run
exec "$@"