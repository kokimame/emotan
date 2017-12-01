# -*- coding: utf-8 -*-
# Copyright: Koki Mametani <kokimametani@gmail.com>
#
import os
from subprocess import call, check_output

from gui.utils import isWin


class BaseTalker:
    # voiceId: A unique name, pre-defined by a given TTS, that specifies a voice in the service.
    def dictate(self, script, voiceId, output=None):
        raise NotImplementedError

    def save(self, script, output, voiceId=None):
        raise NotImplementedError

    def isSupported(self):
        raise NotImplementedError


from tools.talker.say import Say
from tools.talker.espeak import Espeak

# Interfaces for various text-to-speech application
Talkers = {
    "say": Say,
    "espeak": Espeak,
}