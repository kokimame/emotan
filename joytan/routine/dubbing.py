# -*- coding: utf-8 -*-
# Copyright (C) 2017-Present: Kohki Mametani <kohkimametani@gmail.com>
# License: GNU GPL version 3 or later; http://www.gnu.org/licenses/gpl.html

import os
import shutil
import sys
import pydub
import tinytag
from pydub import AudioSegment as Aseg

from joytan.frozen import FROZEN_FFMPEG
if getattr(sys, 'frozen', False):
    Aseg.converter = FROZEN_FFMPEG


class DubbingWorker:
    """
    This class works in the process of making audiobook, providing an interface for pydub
    """
    def __init__(self, setting):
        self.setting = setting
        self.flowlist = []
        # List of acapella mp3file (without BGM but with SFX) for each entry
        # Every element is a set of (AudioSegment, "corresponding lyrics")
        self.acapellas = []
        self.currentTime = 0
        self.lyrics = []
        self.routers = self._get_routers()
        self.loop=self.setting['loop']
        self.bgmLoopCursor=0
        self.bgmRepeatCursor=0

    def cleanData(self):
        self.acapellas = []
        self.currentTime = 0
        self.lyrics = []
        return

    def _nextCursor(self):
        self.bgmLoopCursor+=1
        if self.bgmLoopCursor>=len(self.loop):
            self.bgmLoopCursor=0
        self.bgmRepeatCursor=0

    def _get_routers(self):
        """
        Returns a dict of function to force router of AwesomeTTS to generate audio clips
        based on given svc_id, options, path, and text.
        These functions are only compatible with offline TTS service such as
        Say on Mac, espeak on Linux.
        """
        from joytan.speaker import router
        def chikana_force_run(svc_id, options, path, text):
            opt=options.copy()
            jpopt=options['addPara']['chikanaOpt']
            if 'service' in jpopt:
                jpsvc = jpopt['service']
            elif 'svc' in jpopt:
                jpsvc = jpopt['svc']
            else:
                jpsvc = svc_id
            from joytan.routine.chikana import modi2chikana
            if 'c2c' in jpopt:
                chikana = modi2chikana(text,jpopt['c2c'])
            else:
                chikana = modi2chikana(text)

            asegs=[]
            if len(chikana) == 1:
                word=chikana[0]
                if word[0]==1:
                    router.force_run(jpsvc, jpopt, path, word[1])
                else:
                    router.force_run(svc_id, options, path, word[1])
            else:
                for word in chikana:
                    if word[0]==1:
                        router.force_run(jpsvc, jpopt, path, word[1])
                    else:
                        router.force_run(svc_id, options, path, word[1])

                    aseg=Aseg.from_mp3(path)
                    asegs.append(aseg)

                wholeWord=sum(asegs)
                wholeWord.export(path)

        def force_run(svc_id, options, path, text):
            try:
                if 'addPara' in options:
                    if 'chikana' in options['addPara'] and options['addPara']['chikana']==True:
                        chikana_force_run(svc_id, options, path, text)
                    else:
                        router.force_run(svc_id, options, path, text)
                else:
                    router.force_run(svc_id, options, path, text)
            except Exception as e:
                #Any exception is thrown to the screen as a critical message,
                #then the dubbing thread will immediately be killed.
                raise e
        routers = {}
        for key, val in self.setting['ttsmap'].items():
            routers[key] = \
                lambda path, text, svc_id=val[1], options=val[2]: force_run(svc_id=svc_id,
                                                                            options=options,
                                                                            path=path,
                                                                            text=text)

        return routers

    def setup_audio(self):
        """
        Setup SFX and BGM by converting them in AudioSegment and adjusting volume.
        """
        for fi in self.setting['flow']:
            if fi['desc'] == "MP3":
                sfx = Aseg.from_mp3(fi['path'])
                rdbfs = reduce_dbfs(sfx.dBFS, (1 - fi['volume'] / 100))
                for _ in range(fi['repeat']):
                    self.flowlist.append((sfx - rdbfs))
                    if fi['postrest'] > 0:
                        self.flowlist.append(Aseg.silent(int(fi['postrest'] * 1000)))

            elif fi['desc'] == "REST" and fi['postrest'] > 0:
                self.flowlist.append(Aseg.silent(int(fi['postrest'] * 1000)))
            else:
                # Audio segments for index and ewkeys are generated dynamically on onepass
                self.flowlist.append(fi)

    def onepass(self, ew):
        """
        In the process, the worker passes through the parts of each audio segment within
        a given EntryWidget only once, immediately creates a chunk of audio segment which
        will be a part of the actual audiobook (without BGM).
        """
        # This contains a list of set(audio object from pydub, corresponding string text)
        asegments = []
        curdir = os.path.join(self.setting['dest'], ew.str_index())
        assert os.path.exists(curdir)

        for fi in self.flowlist:
            if isinstance(fi, Aseg):
                asegments.append((fi, ''))
                continue

            if fi['desc'] == 'INDEX':
                index = "%d " % (ew.row + 1)
                idx_file = os.path.join(curdir, "index") + ".mp3"
                self.routers['atop'](path=idx_file, text=index)
                for _ in range(fi['repeat']):
                    aseg = Aseg.from_mp3(idx_file)
                    rdbfs = reduce_dbfs(aseg.dBFS, (1 - fi['volume'] / 100))
                    asegments.append((aseg - rdbfs, index))
                    if fi['postrest'] > 0:
                        asegments.append((Aseg.silent(int(fi['postrest'] * 1000)), ''))

            else:
                ewkey = fi['desc']
                path = os.path.join(curdir, ewkey) + ".mp3"
                if ew[ewkey] != '':
                    self.routers[ewkey](path=path, text=ew[ewkey])
                    for _ in range(fi['repeat']):
                        aseg = Aseg.from_mp3(path)
                        rdbfs = reduce_dbfs(aseg.dBFS, (1 - fi['volume'] / 100))
                        asegments.append((aseg - rdbfs, ew[ewkey]))
                        if fi['postrest'] > 0:
                            asegments.append((Aseg.silent(int(fi['postrest'] * 1000)), ''))

        # '>><<' represents the end of one EntryWidget.
        # This lets you know the timing to switch images on video-making
        asegments.append((Aseg.silent(0), '>><<'))

        # Concatenate all audio-segment and append it to the interim audiobook (acapellas).
        acapella = sum(item[0] for item in asegments)
        if self.setting['lrc']:
            self._add_lyrics(asegments)
        acapella.export(curdir + ".mp3")
        self.acapellas.append(acapella)

    def _add_lyrics(self, asegs):
        """
        Updates lyrics text and lyrics timer for given Entry's audio-segments
        """
        for item in asegs:
            aseg, text = item
            if text:
                self.lyrics.append((self.currentTime, text))
            else:
                self.lyrics.append((self.currentTime, ''))
            self.currentTime += len(aseg)

    def make_lyrics(self, output):
        """
        Audio dialog calls this method to complete and output LRC file 
        """
        with open(output, 'w', encoding='utf-8') as lrc:
            for item in self.lyrics:
                mmss = msec2mmss(item[0])
                lrc.write("[{time}]{line}\n".format(
                    time=mmss, line=item[1]))

    def get_bgmloop(self, audiobook_in_msec):
        """
        Generate looped BGM within given millisecond with user-selected songs.
        BGM may contain very long audio files which exceed the duration of
        the audiobook we are making. Loading such file as a whole using pydub
        is not time effective, so in these situation we call ffmpeg command to 
        copy and split the song into the size of what we need.
        """
        done = False
        bgmloop = []
        def remaining():
            return max(audiobook_in_msec - sum([len(aseg) for aseg in bgmloop]), 0)

        output = os.path.join(self.setting['dest'],
                              'last_fraction_bgm.mp3')
        output2 =os.path.join(self.setting['dest'],
                                        'remain_bgm.mp3')
        output3 = os.path.join(self.setting['dest'],
                               'replicate_bgm.mp3')
        if os.path.exists(output2):
            bgm=Aseg.from_mp3(output2)
            bgmdur=bgm.duration_seconds*1000
            if bgmdur>remaining():
                shutil.copyfile(output2,output3)
                copy_and_split(output3, output, remaining(),
                               output2)
                bgm = Aseg.from_mp3(output)
                rdbfs = reduce_dbfs(bgm.dBFS,
                                    (1 - self.loop[self.bgmLoopCursor]['volume'] / 100))
                bgmloop.append((bgm - rdbfs))
                done=True
            else:
                rdbfs = reduce_dbfs(bgm.dBFS,
                                    (1 -
                                     self.loop[self.bgmLoopCursor][
                                         'volume'] / 100))
                bgmloop.append((bgm-rdbfs))
                os.remove(output2)

        while not done:
            # Reading flowitem from audio dialog setting
            fi=self.loop[self.bgmLoopCursor]
            if fi['desc'] == "MP3":
                duration = duration_tag(fi['path'])
                if duration > remaining():
                    copy_and_split(fi['path'], output, remaining(),output2)
                    bgm = Aseg.from_mp3(output)
                    rdbfs = reduce_dbfs(bgm.dBFS, (1 - fi['volume'] / 100))
                    bgmloop.append((bgm - rdbfs))
                    done = True
                else:
                    bgm = Aseg.from_mp3(fi['path'])
                    rdbfs = reduce_dbfs(bgm.dBFS, (1 - fi['volume'] / 100))
                    # Probably it's safe to overlay BGM even if it exceeds msec with
                    # the repetition below.
                    if self.bgmRepeatCursor< fi['repeat']:
                        self.bgmRepeatCursor+=1
                        bgmloop.append((bgm - rdbfs))
                        if fi['postrest'] > 0:
                            bgmloop.append(Aseg.silent(int(fi['postrest'] * 1000)))
                    else:
                        self._nextCursor()
            elif fi['desc'] == "REST" and fi['postrest'] > 0:
                bgmloop.append(Aseg.silent(int(fi['postrest'] * 1000)))
            if done or not remaining():
                break

        return sum(bgmloop)


def copy_and_split(mp3path, output, ending, output2=""):
    """
    :param mp3path: Path to mp3 file to copy and cut
    :param output: Path to output mp3 file
    :param ending: Time to cut(split) input mp3file

    This gets called when the duration of a song at the end exceeds the 
    remaining time we need while making a looped BGM.
    This copies input mp3file and cuts it at given time then save it as 'output'. 
    """

    # Check if the user install dependencies for pydub
    if getattr(sys, 'frozen', False):
        program = FROZEN_FFMPEG
    else:
        program = pydub.utils.which("ffmpeg")

    command = [program,
               '-y',  # Say yes to override confirmation
               '-i', mp3path,
               '-acodec', 'copy',
               '-loglevel', 'panic',
               '-ss', '0',
               '-to', str(ending / 1000),
               output]

    import subprocess
    subprocess.call(command)

    if output2!="":
        command = [program,
                   '-y',  # Say yes to override confirmation
                   '-i', mp3path,
                   '-acodec', 'copy',
                   '-loglevel', 'panic',
                   '-ss', str(ending / 1000),
                   output2]
        subprocess.call(command)


def duration_tag(mp3path):
    """
    Returns the duration of given mp3 file in millisecond
    """
    Tag = tinytag.TinyTag.get(mp3path)
    return Tag.duration * 1000


def reduce_dbfs(dbfs, percent):
    """
    :param dbfs: decibel relative to full scale, 0 as upper bounds
    :param percent: The percentage of volume to reduce from the dbfs
    :return: Integer of dbfs to reduce
    
    Calculate dbfs to reduce by given percentage.
    """
    # Experimental minimum dbfs of sounds which human can hear.
    # This is intended to correspond to the 'volume 0% (mute)'.
    # However, it turns out -40 is wrong to achieve this goal;
    # even if volume slider is set to 0, you can slightly hear sounds.
    # But coming to think of the fact if you want to mute an audio just
    # delete it, and lacking the info of how to mute by reducing dbfs,
    # _MINIMUM_DBFS is set to -40 for time being.
    _MINIMUM_DBFS = -40
    diff = min(_MINIMUM_DBFS - dbfs, 0)

    return int(abs(diff) * percent)


def msec2mmss(msec):
    """
    Given a millisecond value, returns a MM:SS string.
    For a value over an hour, this returns MM:SS making MM
    over 60 (e.g, 13,800,000 msec => 230:00.00).
    The representation may break the LRC file format but
    it seems the format itself doesn't specify the workaround
    about this issue.
    """
    sec = msec / 1000
    m, s = divmod(sec, 60)
    mmss = "%02d:%02d" % (m, s) + ".%02d" % (msec % 100)
    return mmss
