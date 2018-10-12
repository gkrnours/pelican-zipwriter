from datetime import datetime
import logging
import os
import sys
from zipfile import ZipFile

from pelican import signals
from pelican.paginator import Paginator

PY2 = sys.version_info[0] == 2
logger = logging.getLogger(__name__)

def is_str(val):
    if PY2:
        return isinstance(val, basestring)
    else:
        return isinstance(val, str)


class ZipWriter(object):
    def __init__(self, output_path, settings=None):
        self.settings = settings
        output = settings.get("OUTPUT_FILE", "")
        if is_str(output):
            if not output:
                filename = datetime.now().strftime("%Y%m%d_%H%M%S.zip")
                output = os.path.join(os.getcwd(), filename)
        mode = 'w'
        self.zip = ZipFile(output, mode)
        logger.info("Created ZipFile at %s with mode %s" % (output, mode))
        signals.finalized.connect(self.finalize)

    def finalize(self, pelican_object):
        self.zip.close()
        logger.debug("Closed ZipFile")

    def write_feed(self, elements, context, path=None, feed_type="atom",
                   override_output=False, feed_title=None):
        logger.info("Writing feed (TODO(tm))")

    def write_file(self, name, template, context, relative_urls=False,
                   paginated=None, override_output=False, **kwargs):
        if not name:
            logger.debug("No name, skipping")
            return

        # make context
        if paginated:
            paginators = {key: Paginator(name, val, self.settings)
                for key, val in paginated.items()}

            for page_num in range(list(paginators.values())[0].num_pages):
                local_kwargs = self._paginate(kwargs, paginators, page_num)
                page = list(paginators.values())[0].page(page_num + 1)
                localcontext = self._make_localcontext(
                    context, page.save_as, local_kwargs)
                self._write_file(template, localcontext, page.save_as)
        else:
            localcontext = self._make_localcontext(context, name, kwargs)
            self._write_file(template, localcontext, name)

    def write_static(self):
        print("write_static")

    def _write_file(self, template, context, name):
        """Render the template and write the file"""
        output = template.render(context)
        path = os.path.join("content", name)
        self.zip.writestr(path, output)
        # signals
        logger.info('Written %s', path)
        signals.content_written.send(path, context=context)


    def _make_localcontext(self, context, name, kwargs, relative_urls=None):
        localcontext = context.copy()
        localcontext = {}
        localcontext['localsiteurl'] = localcontext.get('localsiteurl', None)
        if relative_urls:
            relative_url = path_to_url(get_relative_path(name))
            localcontext['SITEURL'] = relative_url
            localcontext['localsiteurl'] = relative_url
        localcontext['output_file'] = name
        localcontext.update(kwargs)
        return localcontext

    def _paginate(self, kwargs, paginators, page_num):
        local_kwargs = kwargs.copy()
        for key in paginators.keys():
            paginator = paginators[key]
            previous_page = (paginator.page(page_num)
                if page_num > 0 else None)
            page = paginator.page(page_num + 1)
            next_page = (paginator.page(page_num + 2)
                if page_num + 1 < paginator.num_pages else None)
            local_kwargs.update({
                '%s_paginator' % key: paginator,
                '%s_page' % key: page,
                '%s_previous_page' % key: previous_page,
                '%s_next_page' % key: next_page,
            })
        return local_kwargs
