# -*- coding: utf-8 -*-

import json
from .sql import Sql
import settings
from items import *


class GoogleprjPipeline(object):

    def process_item(self, item, spider):
        if isinstance(item,DmozItem):
            Sql.insert_brand(item)
        if isinstance(item,gurl):
            Sql.insert_gurl(item)
        if isinstance(item,burl):
            Sql.insert_burl(item)
        if isinstance(item,ukurl):
            Sql.insert_ukurl(item)
        if isinstance(item,deurl):
            Sql.insert_deurl(item)
        return item
    