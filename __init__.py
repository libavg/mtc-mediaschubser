import os
from libavg.utils import getMediaDir, createImagePreviewNode
from . import schubser

__all__ = [ 'apps', ]

def createPreviewNode(maxSize):
    filename = os.path.join(getMediaDir(__file__), 'preview.png')
    return createImagePreviewNode(maxSize, absHref = filename)

apps = (
        {'class': schubser.Schubser,
            'createPreviewNode': createPreviewNode},
        )
