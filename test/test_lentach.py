import unittest
from pylentach import lentach
from unittest.mock import Mock, patch, MagicMock
import os
import os.path

def mockMethodChain(return_val, methods):
    """
    Makes mock object with chain of given methods returning return_val

    Example:
    >>> data = mockMethodChain('abc', ['read', 'decode'])
    >>> print(data.read().decode())
    abc
    """

    def _chain(methods):
        obj = MagicMock()
        if methods:
            obj.__dict__[methods[0]] = MagicMock(return_value=_chain(methods[1:]))
        else:
            return return_val
        return obj
        
    return _chain(methods)

class PatchContextManager:

    def __init__(self, method, enter_return, exit_return=False):
        self._patched = patch(method)
        self._enter_return = enter_return
        self._exit_return = exit_return

    def __enter__(self):
        res = self._patched.__enter__()
        res.context = MagicMock()
        res.context.__enter__.return_value = self._enter_return
        res.context.__exit__.return_value = self._exit_return
        res.return_value = res.context
        return res

    def __exit__(self, type, value, tb):
        return self._patched.__exit__()


class PylentachTest(unittest.TestCase):

    def setUp(self):
        self.get_post_datas = [
            ('{"a":[{"b":{"audio":{"url":"abc"}}}]}', {'a':[{'b':{'audio':{'url':'abc'}}}]}),
        ]

    def test_get_post(self):
        for fake_data, expected in self.get_post_datas:
            mocked_chain = mockMethodChain(fake_data, ['read', 'decode'])
            with PatchContextManager('pylentach.lentach.urlopen', mocked_chain) as m_urlopen:
                posts = lentach.get_posts()
                self.assertEqual(posts, expected)
                call_url = 'https://api.vk.com/method/wall.get?domain=oldlentach&count=1&offset=0'
                m_urlopen.assert_called_with(call_url, timeout=5)

    def test_save_audio(self):
        with PatchContextManager('pylentach.lentach.urlopen', mockMethodChain(b'abc', ['read'])) \
             as m_urlopen:
            lentach.save_audio('_', 'mocked_title')
            assert os.path.isfile('mocked_title.mp3')
            os.remove('mocked_title.mp3') #tear down


    def test_find_val(self):
        pass

    def tearDown(self):
        pass
