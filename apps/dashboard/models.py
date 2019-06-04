#coding=utf-8

from django.utils import timezone
from django.db.models import Q, F
from django.conf import settings
from django.db import models

from apps.account.models import User

from collections import OrderedDict
import datetime
