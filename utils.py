from tornado.database import Connection
from tornado.template import Loader, Template
from tornado.web import RequestHandler

from oz.handler import DjangoErrorMixin

import myhaml


class ConnectionPing(Connection):
    def __init__(self, *args, **kwargs):
        Connection.__init__(self, *args, **kwargs)
        # MySQL connection will go away if no any queries within 8 hours by default
        PeriodicCallback(self._ping_db, 4 * 3600 * 1000).start()

    def _ping_db(self):
        # Any query is ok, eg. show variables.
        self.db.query("show variables")


class BaseHandler(DjangoErrorMixin, RequestHandler):
    pass


class HAMLLoader(Loader):
    def load(self, name, parent_path=None):
        name = self.resolve_path(name, parent_path=parent_path)
        if name not in self.templates:
            path = os.path.join(self.root, name)
            f = open(path, "r")
            contents = f.read()
            contents = myhaml.convert_text(contents) # Preprocess with myhaml
            self.templates[name] = Template(contents, name=name, loader=self)
            f.close()
        return self.templates[name]



