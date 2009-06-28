#!/usr/bin/env python
# Copyright (C) 2009
#    Martin Heistermann, <mh at sponc dot de>
#
# mediaSchubser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mediaSchubser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mediaSchubser.  If not, see <http://www.gnu.org/licenses/>.

from libavg import avg, Point2D, Grabbable
from libavg import AVGApp
from libavg.mathutil import getScaledDim
from libavg.AVGAppUtil import getMediaDir

import os
import random
import math

g_player = avg.Player.get()

class Image(object):
    def __init__(self, parentNode, type_, href):
        assert type_ in ('image', 'video')
        self._divNode = g_player.createNode('div', {})
        self._borderNode = g_player.createNode('image', {'href': 'whitepix.png'})
        self._divNode.appendChild(self._borderNode)
        self.type_ = type_
        if (type_=='video'):
            self._mediaNode = g_player.createNode('video', {
                'href': href,
                'threaded': True,
                'loop': True,
                'mipmap': True,
                })
            self._mediaNode.play()
        else:
            self._mediaNode = g_player.createNode('image', {'href': href, 'mipmap': True})
        self._mediaNode.pos = Point2D(5,5)
        self._divNode.appendChild(self._mediaNode)
        parentNode.appendChild(self._divNode)
        self._parentNode = parentNode
        self._mediaNode.active = False

    def start(self):
        mediasize = Point2D(self._mediaNode.getMediaSize())
        self._divNode.size = getScaledDim(mediasize, max = Point2D(200,200))
        self._divNode.pivot = self._divNode.size/2
        self._divNode.angle = random.uniform(-0.4 * math.pi, 0.4 * math.pi)
        borderDist = 50
        mid = self._divNode.getParent().size/2
        x = random.uniform(mid.x - 300, mid.x + 300)
        y = random.uniform(mid.y - 200, mid.y + 200)
        self._divNode.pos = Point2D(x,y)
        self.__adaptSize()

        self.grabbable = Grabbable(
                node = self._divNode,
                maxSize = mediasize,
                minSize = Point2D(100, 100),
                onAction = self.__adaptSize,
                )
        self._mediaNode.active = True
        if self.type_ == 'video':
            self._mediaNode.play()

    def __adaptSize(self):
        """adapt medianode and bordernode to divnode size"""
        size = self._divNode.size
        self._borderNode.size = size
        self._mediaNode.size = size - 2 * self._mediaNode.pos

    def stop(self):
        self.grabbable.delete()
        del self.grabbable
        self._mediaNode.active = False
        if self.type_ == 'video':
            self._mediaNode.stop()

    def isAlive(self):
        midPos = self._divNode.getAbsPos(self._divNode.size/2)
        if midPos.x < -10 or midPos.x > self._divNode.getParent().width + 10:
            return False
        if midPos.y < -10 or midPos.y > self._divNode.getParent().height + 10:
            return False
        return True


def getFilesInDir(dirName):
    hrefs = []
    def handleEntry(maindir, dirname, fname):
        if maindir == dirname: # only top-level
            hrefs.extend([name for name in fname if name[0] != '.'])
        while len(fname):
            del fname[0]

    os.path.walk(dirName, handleEntry, dirName)
    return hrefs

class Schubser(AVGApp):
    multitouch = True
    def __init__(self, parentDir):
        print "Schubser: moving media to ramdisk"
        self.contentDir = os.path.join(getMediaDir(__file__), "content")
        ret = os.system("rsync -av %s/ /dev/shm/mediaschubser_content" % self.contentDir)
        if ret==0:
            print "rsync success!"
            self.contentDir = '/dev/shm/mediaschubser_content'
        super(Schubser, self).__init__(parentDir)

    def loadImages(self):
        for type_, dirName in (('video', 'videos'), ('image','images')):
            path = os.path.join(self.contentDir, dirName)
            for href in os.listdir(path):
                if href[0]!='.':
                    self.images.append(Image(self._parentNode, type_, os.path.join(path,href)))

    def init(self):
        self._parentNode.mediadir = getMediaDir(__file__)
        bgNode = g_player.createNode('image', {'href': 'background.jpg'})
        self._parentNode.appendChild(bgNode)
        self.images = []

        self.loadImages()

    def _enter(self):
        g_player.volume = 0
        for image in self.images:
            image.start()
        self.__amIDeadYet = g_player.setInterval(1000, self.__checkDeath)

    def _leave(self):
        g_player.volume = 1
        for image in self.images:
            image.stop()
        g_player.clearInterval(self.__amIDeadYet)

    def __checkDeath(self):
        for image in self.images:
            if image.isAlive():
                return
        self.leave()

if __name__ == '__main__':
    Schubser.start(resolution = (1280,720))


