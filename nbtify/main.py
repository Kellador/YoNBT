#!/usr/bin/env python
from nbt import NBTObj
import gzip
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
import os


class ListView(Frame):
    def __init__(self, screen, nbtobj):
        super(ListView, self).__init__(screen,
                                       screen.height * 2 // 3,
                                       screen.width * 2 // 3,
                                       has_shadow=True,
                                       hover_focus=True,
                                       title="NBT")
        self._nbtobj = nbtobj
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            nbtobj.value,
            name="TAGs")
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        self.fix()


def demo(screen, scene):
    scenes = [
        Scene([ListView(screen, NBTObj(os.path.join('C:/Users/Kella/Desktop/Tidy', 'hairyt.dat')))], -1, name="Main")
    ]
    screen.play(scenes, stop_on_resize=True, start_scene=scene)


last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
