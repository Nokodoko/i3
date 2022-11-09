#!/usr/bin/env python3

#-----------------------------------------------
# used to swallow a terminal window in i3
# USAGE
# it need you install python 3 and install i3ipc `pip3 install i3ipc`
# download this scrript and put it to your i3 config folder 
# add that script to your i3 config
# exec --no-startup-id python3 $HOME/.config/i3/i3-swallow.py
# try run `xclock`
#----------------------------------------------------

import i3ipc
import subprocess

swallowDict={}
i3 = i3ipc.Connection()

def hideSwallowParent(node,windowId,swallowId):
    if(str(node.window) == str(windowId)):
        global swallowDict
        i3.command('[con_id=%s] focus' % swallowId)
        i3.command('[con_id=%s] move to scratchpad' % node.id)
        swallowDict[str(swallowId)]=node.id
        return True
    for node in node.nodes:
        if(hideSwallowParent(node, windowId, swallowId)):
            return True
    return False

def getParentNodePid(node):
    # get parent of pid because terminal spwan shell(zsh or fish) and then spawn that child process
    output = subprocess.getoutput(
        "ps -o ppid= -p $(ps -o ppid= -p $(xprop -id %d _NET_WM_PID | cut -d' ' -f3 ))"% (node.window))
    return output

def getWindowIdfromPId(pid):
    output = subprocess.getoutput("xdotool search -pid %s" %pid)
    return output

def on_event(self, event):
    workspace = i3.get_tree().find_focused().workspace()
    # find parent node pid to map to any node in current workspace 
    parentContainerPid = getParentNodePid(event.container)
    parentContainerWid = getWindowIdfromPId(parentContainerPid)
    for item in workspace.nodes:
         hideSwallowParent(item,parentContainerWid,event.container.id)


def on_close(self,event):
    global swallowDict
    swallowId=swallowDict.get(str(event.container.id))
    if swallowId != None:
        window=i3.get_tree().find_by_id(swallowId)
        if window!=None:
            event.container.command(
                '[con_id=%s] scratchpad show; floating toggle;focus' % window.id)

# Subscribe to events
i3.on("window::new", on_event)
i3.on("window::close",on_close)
i3.main()
