# coding: utf-8
import tornado
import tornado.web
import tornado.auth
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import session

AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        self.session = session.TornadoSession(application.session_manager, self)
        self._title = self.settings['app_name']
        self.db = self.settings['db']
        self.error_msg = None

    @property
    def flash(self):
        msg = self.get_secure_cookie('flash', None)
        self.clear_cookie('flash')
        return msg

    # flash just like Flask flash. It will appear only once after redirect to another page!
    def set_flash(self, msg):
        self.set_secure_cookie('flash', msg)

    def get_template_namespace(self):
        namespace = super(BaseHandler, self).get_template_namespace()
        namespace['flash'] = self.flash
        namespace['error_msg'] = self.error_msg
        namespace.update(self.ui)
        return namespace

    def get_current_user(self):
        return self.get_secure_cookie('username')

    def check_xsrf_cookie(self):
        header = self.request.headers
        if not ('GitHub-Hookshot' in header['User-Agent']):
            super(BaseHandler, self).check_xsrf_cookie()

    # def write(self, chunk):
    #         pickled = pickle.dumps(chunk)
    #         key = self._generate_key(self.request)
    #         if hasattr(self, "expires"):
    #             self.cache.set(self._prefix(key), pickled, self.expires)
    #         else:
    #             self.cache.set(self._prefix(key), pickled)
    #         super(CacheMixin, self).write(chunk)
