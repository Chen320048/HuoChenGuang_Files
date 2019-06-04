from django.utils.deconstruct import deconstructible
from django.utils import timezone
from django.conf import settings

import os

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

        full_path = "%s/%s" % (settings.MEDIA_ROOT, sub_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    def __call__(self, instance, filename):
        # set filename as random string
        ext = filename.split('.')[-1]
        t = timezone.now().strftime('%Y%m%d%H%M%S%f')
        # get filename

        if instance.pk:
            filename = '{}-{}.{}'.format(instance.pk, t, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(t, ext)
        # return the whole path to the file
        return os.path.join(self.path , filename)
