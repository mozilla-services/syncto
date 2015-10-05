try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import webtest
from cliquet.tests import support as cliquet_support
from syncto import main as testapp


ENCRYPTED_CREDENTIALS = (
    'ada7bf44ae1f88bdb08a0ad4d8702419f77912f5ee4a7a06948a88993cd05d77b8'
    'e1cc01212db4b007102e7eaf2379afecc043324cc565337bba48c278052be99190'
    'a47b4040bf7cfa594414637ba50de16342cad902c8c249b9ae2af93e6675b52d55'
    '8ae157f98ff168deb719054917a44de115e43609c0bb2ce9a92a4cf1c2477ddddd'
    '38c625b92a0b5e9bd9a53247955479fbaa7a0a1bc3077f5ff71ef3b1c0decaac88'
)


class BaseWebTest(object):

    def __init__(self, *args, **kwargs):
        super(BaseWebTest, self).__init__(*args, **kwargs)
        self.app = self._get_test_app()
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _get_test_app(self, settings=None):
        app = webtest.TestApp(testapp({}, **self.get_app_settings(settings)))
        app.RequestClass = cliquet_support.get_request_class(prefix="v1")
        return app

    def get_app_settings(self, additional_settings=None):
        settings = cliquet_support.DEFAULT_SETTINGS.copy()
        settings['cliquet.cache_backend'] = 'cliquet.cache.memory'
        settings['cliquet.storage_backend'] = 'cliquet.storage.memory'
        settings['cliquet.permission_backend'] = 'cliquet.permission.memory'
        settings['cliquet.userid_hmac_secret'] = "this is not a secret"
        settings['syncto.cache_hmac_secret'] = 'This is not a secret'

        if additional_settings is not None:
            settings.update(additional_settings)
        return settings
