# -*- coding: utf-8 -*-
import unittest
import phpserialize


class PhpSerializeTestCase(unittest.TestCase):

    def test_dumps_int(self):
        self.assertEqual(phpserialize.dumps(5), b'i:5;')

    def test_dumps_float(self):
        self.assertEqual(phpserialize.dumps(5.6), b'd:5.6;')

    def test_dumps_str(self):
        self.assertEqual(phpserialize.dumps('Hello world'),
                         b's:11:"Hello world";')

    def test_dumps_unicode(self):
        self.assertEqual(phpserialize.dumps('Björk Guðmundsdóttir'),
                         b's:23:"Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir";')

    def test_dumps_binary(self):
        self.assertEqual(phpserialize.dumps(b'\001\002\003'),
                         b's:3:"\x01\x02\x03";')

    def test_dumps_list(self):
        self.assertEqual(phpserialize.dumps([7, 8, 9]),
                         b'a:3:{i:0;i:7;i:1;i:8;i:2;i:9;}')

    def test_dumps_tuple(self):
        self.assertEqual(phpserialize.dumps((7, 8, 9)),
                         b'a:3:{i:0;i:7;i:1;i:8;i:2;i:9;}')

    def test_dumps_dict(self):
        self.assertEqual(phpserialize.dumps({'a': 1, 'b': 2, 'c': 3}),
                         b'a:3:{s:1:"a";i:1;s:1:"c";i:3;s:1:"b";i:2;}')

    def test_loads_dict(self):
        self.assertEqual(phpserialize.loads(b'a:3:{s:1:"a";i:1;s:1:"c";i:3;s:1:"b";i:2;}',
                         decode_strings=True), {'a': 1, 'b': 2, 'c': 3})

    def test_loads_unicode(self):
        self.assertEqual(phpserialize.loads(b's:23:"Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir";',
                         decode_strings=True), b'Bj\xc3\xb6rk Gu\xc3\xb0mundsd\xc3\xb3ttir'.decode('utf-8'))

    def test_loads_binary(self):
        self.assertEqual(phpserialize.loads(b's:3:"\001\002\003";', decode_strings=False),
                         b'\001\002\003')

    def test_dumps_and_loads_dict(self):
        self.assertEqual(phpserialize.loads(phpserialize.dumps({'a': 1, 'b': 2, 'c': 3}),
                         decode_strings=True), {'a': 1, 'b': 2, 'c': 3})

    def test_list_roundtrips(self):
        x = phpserialize.loads(phpserialize.dumps(list(range(2))))
        self.assertEqual(x, {0: 0, 1: 1})
        y = phpserialize.dict_to_list(x)
        self.assertEqual(y, [0, 1])

    def test_tuple_roundtrips(self):
        x = phpserialize.loads(phpserialize.dumps(list(range(2))))
        self.assertEqual(x, {0: 0, 1: 1})
        y = phpserialize.dict_to_tuple(x)
        self.assertEqual(y, (0, 1))

    def test_fileio_support_with_chaining_and_all(self):
        f = phpserialize.BytesIO()
        phpserialize.dump([1, 2], f)
        phpserialize.dump(42, f)
        f = phpserialize.BytesIO(f.getvalue())
        self.assertEqual(phpserialize.load(f), {0: 1, 1: 2})
        self.assertEqual(phpserialize.load(f), 42)

    def test_array_object(self):
        self.assertEqual(phpserialize.loads(b"""a:1:{s:16:"525f70091c4bd_ja";C:11:"ArrayObject":896:{x:i:2;a:16:{s:10:"unit_count";i:3;s:7:"credits";d:0.14999999999999999;s:3:"eta";i:25236;s:8:"currency";s:3:"USD";s:4:"type";s:4:"text";s:15:"lc_src_detected";b:0;s:11:"custom_data";s:13:"525f70091c4bd";s:6:"lc_tgt";s:2:"ja";s:6:"lc_src";s:2:"en";s:5:"title";s:10:"sa dsa dsa";s:8:"body_src";s:10:"sa dsa dsa";s:10:"word_count";i:3;s:5:"force";i:1;s:7:"comment";s:0:"";s:12:"preview_html";s:463:"&lt;div class='item type_text' id='cart_item_525f70091c4bd'&gt;
    &lt;a href='javascript:;' class='remove_item'&gt;x&lt;/a&gt;
    &lt;span class='word_count'&gt;&lt;/span&gt;
            &lt;p class='title'&gt;&lt;strong&gt;sa dsa dsa&lt;/strong&gt;&lt;/p&gt;
        &lt;p class='body'&gt;sa dsa dsa&lt;/p&gt;
        &lt;p class='item_tools'&gt;&lt;a href='javascript:;' class='edit_text'&gt;Edit Text / Add Instructions&lt;/a&gt;&lt;/p&gt;
    &lt;/div&gt;
";s:4:"tier";s:8:"standard";};m:a:0:{}}}""", object_hook=phpserialize.phpobject), {'525f70091c4bd_ja': None})

    def test_object_hook(self):
        class User(object):
            def __init__(self, username):
                self.username = username

        def load_object_hook(name, d):
            return {'WP_User': User}[name](**d)

        def dump_object_hook(obj):
            if isinstance(obj, User):
                return phpserialize.phpobject('WP_User', {'username': obj.username})
            raise LookupError('unknown object')

        user = User('test')
        x = phpserialize.dumps(user, object_hook=dump_object_hook)
        y = phpserialize.loads(x, object_hook=load_object_hook,
                               decode_strings=True)
        self.assert_(b'WP_User' in x)
        self.assertEqual(type(y), type(user))
        self.assertEqual(y.username, user.username)

    def test_basic_object_hook(self):
        data = b'O:7:"WP_User":1:{s:8:"username";s:5:"admin";}'
        user = phpserialize.loads(data, object_hook=phpserialize.phpobject,
                                  decode_strings=True)
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.__name__, 'WP_User')


if __name__ == '__main__':
    unittest.main()
