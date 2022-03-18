import unittest

import pyname as pn


class NameIt(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def to_str(self, obj):
        return "".join(str(obj).split())

    def test_name(self):
        pn.clear_prev_obj_l()
        print(pn("test"))
        print(pn(xixi="hah"))

        # FIXME: It fails to create name without ambiguity for `good` and `good2`
        # My idea is to remove all the shared name at first
        print(pn("test", "jjj", "repeat",  good2="xxx", good="xixi"))
        print(pn("test", "xx", "repeat", good2="xxx", good="xixi"))

    def test_get_long_name(self):
        pn.clear_prev_obj_l()
        info = {i: i for i in range(1000)}
        print(pn(info))

        info[20] = "a"

        print(pn(info))
        print(pn(info))

    def test_shorten_list(self):
        print(pn({"a": [1, 2]}))

if __name__ == "__main__":
    unittest.main()
