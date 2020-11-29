## Why do we restart the camera process to update configuration
Because this is hard to implement ipc (inter-process communication). Of course we could use some socket it is not that hard
but this is code to maintain, test... And of course this is error/bug-prone.

The configuration of the camera won't change frequently, so this won't impact very badly the performance of
the overall system. Of course by restarting a new process we recreate the video stream and so one, which is
kinda expensive but this won't happen frequently so this is not a problem.

The first idea was to use Thread to have memory sharing out of the box, so we could change the ROI easily,
but in Python a Thread is not executed on a different machine processor so this is not working: the camera thread
is monopolise the process, thus the system is not able to receive mqtt updates. 
