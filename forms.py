# coding: utf-8
import re
import logging  
import urlparse
import formencode
from formencode import htmlfill, validators


class BaseForm(formencode.Schema):
    """
    by Felinx Lee 
    https://bitbucket.org/felinx/poweredsites/src/8448db5ba387/poweredsites/forms/base.py
    """
    allow_extra_fields = True
    filter_extra_fields = True

    _xsrf = validators.PlainText(not_empty=True, max=32)

    def __init__(self, handler, form_id = None):

        self._parmas = {}
        self._values = {}
        self._form_errors = {}
        self.form_id = form_id
        arguments = {}

        # re-parse qs, keep_blankvalues for formencode to validate
        # so formencode not_empty setting work.
        request = handler.request
        content_type = request.headers.get("Content-Type", "")

        if request.method == "POST":
            if content_type.startswith("application/x-www-form-urlencoded"):
                arguments = urlparse.parse_qs(request.body, keep_blank_values=1)

        for k, v in arguments.iteritems():
            if len(v) == 1:
                self._parmas[k] = v[0]
            else:
                # keep a list of values as list (or set)
                self._parmas[k] = v

        self._handler = handler
        self._result = True

    def validate(self):
        try:
            self._values = self.to_python(self._parmas)
            self._result = True
            self.__after__()
        except formencode.Invalid, error:
            self._values = error.value
            self._form_errors = error.error_dict or {}
            self._result = False

        # map values to define form propertys and decode utf8
        for k in self._values.keys():
            exec("self.%s = self._values[\"%s\"].decode('utf8')" % (k,k)) 

        return self._result

    # add custom error msg
    def add_error(self, attr, msg):
        self._result = False
        self._form_errors[attr] = msg

    def render(self, template_name, **kwargs):
        html = self._handler.render_string(template_name, **kwargs)

        if not self._result:
            html = htmlfill.render(html,
                                   defaults=self._values,
                                   errors=self._form_errors,
                                   encoding="utf8")

        self._handler.finish(html)

    # post process hook
    def __after__(self):
        pass

class LoginForm(BaseForm):
    login = validators.String(not_empty=True,strip=True)
    password = validators.String(not_empty=True)

class RegisterForm(BaseForm):
    login = validators.String(not_empty=True,strip=True,min=4,max=20)
    email = validators.Email(not_empty=True,strip=True)
    name = validators.String(not_empty=True,strip=True)
    password = validators.String(not_empty=True)
    password_confirm = validators.String(not_empty=True)
    chained_validators = [validators.FieldsMatch('password', 'password_confirm')]

