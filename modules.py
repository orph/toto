
import fnmatch
import logging
import sys

import tornado.escape
import tornado.web


class UIActionHandler(tornado.web.RequestHandler):
    '''
    A UIActionHandler receives a list of BaseModule keys on the requesting
    page in the 'page_modules' request arg.  The handler can invalidate page
    module keys using glob-like masks.  When finished, these masks are applied
    to the requesting page's module keys, any matches are re-rendered and the
    HTML returned to the client.
    '''

    def __init__(self, *args, **kwargs):
        super(UIActionHandler, self).__init__(*args, **kwargs)
        self.refresh_masks = []

    def _module_and_args_by_key(self, key):
        split = key.split('-')
        mod = getattr(sys.modules[self.__class__.__module__], split[0])(self)
        args = dict(zip(mod.args, split[1:]))
        return (mod, args)

    def finish(self, chunk=None):
        if not chunk:
            page_modules = self.get_argument('page_modules', '').split(',')
            # match refresh_masks globs to page_modules and render each
            matches = [fnmatch.filter(page_modules, mask) for mask in self.refresh_masks]
            matches = sum(matches, []) # flatten
            matches = dict().fromkeys(matches).keys() # uniquify
            logging.debug("UIActionHandler invalidating UIModules: %s", matches)
            widgets = []
            for key in matches:
                mod, args = self._module_and_args_by_key(key)
                widgets.append(mod.render(**args))
            self.write(tornado.escape.json_encode(widgets))
        super(UIActionHandler, self).finish(chunk)

    def invalidate(self, *args):
        for key in args:
            self.refresh_masks.append(key)


class BaseModule(tornado.web.UIModule):
    '''
    UIModule subclasses are identified by key, which is composed of args values
    passed to the initial render call inside templates.  key and args are used
    by UIActionHandlers for identifying/recreating modules based on key.
    '''

    args = []
    key = ''

    def render(self, *args, **kwargs):
        kwargs.update(dict(zip(self.args, args)))
        t = self.render_string(
            "modules.html", module=self.__class__.__name__, key=self.key %
            kwargs, **kwargs)
        return t

    def javascript_files(self):
        return '/static/js/modules.js'

