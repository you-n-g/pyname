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
        print(pn.opt(save=False)({"a": [1, 2]}))
        print(pn.opt(save=False)(b={"a": []}))

    def test_convert_basic(self):
        obj = {
            'args.args': [],
            'args.kwargs.cluster': False,
            'args.kwargs.cv': 'simple_split',
            'args.kwargs.debug': False,
            'args.kwargs.exp_suffix': None,
            'args.kwargs.extra_fea': [],
            'args.kwargs.extra_param': None,
            'args.kwargs.fold_n': 5,
            'args.kwargs.gap': 1,
            'args.kwargs.hp_ver': None,
            'args.kwargs.market_info': False,
            'args.kwargs.model_param_default': 'v01',
            'args.kwargs.model_param_update.batch_size': 512,
            'args.kwargs.model_param_update.eval_steps': -1,
            'args.kwargs.model_param_update.max_steps': None,
            'args.kwargs.model_param_update.max_epoch': 50,
            'args.kwargs.model_param_update.lr': 0.0005,
            'args.kwargs.model_param_update.shuffle_train': False,
            'args.kwargs.model_param_update.early_stop_rounds': 5,
            'args.kwargs.model_param_update.scheduler': None,
            'args.kwargs.no_shuffle': False,
            'args.kwargs.proc_ver': 'v04',
            'args.kwargs.pt_model_uri': 'infer_utils.DNNLR',
            'args.kwargs.qlib_model_default_kwargs_gen': 'utils.get_qlib_pt_model_kwargs',
            'args.kwargs.qlib_model_uri': 'infer_utils.DNNModelPytorch',
            'args.kwargs.repeat_n': 1,
            'args.kwargs.retrain': False,
            'args.kwargs.retrain_start': None,
            'args.kwargs.reweighter': None,
            'args.kwargs.run_num': 1,
            'args.kwargs.scheduler': None,
            'args.kwargs.seed': 42,
            'args.kwargs.seg_n': 120,
            'args.kwargs.simple_split_n': 1000,
            'args.kwargs.test_seg': None,
            'args.kwargs.train_start': 0
        }
        print(pn.convert2basic(obj))

        obj = {
            'args': ({
                'args': [],
                'kwargs': {
                    'cluster': False,
                    'cv': 'simple_split',
                    'debug': True,
                    'exp_suffix': None,
                    'extra_fea': [],
                    'extra_param': None,
                    'fold_n': 5,
                    'gap': 1,
                    'hp_ver': None,
                    'market_info': False,
                    'model_param_default': 'v01',
                    'model_param_update': {
                        'batch_size': 512,
                        'eval_steps': -1,
                        'max_steps': None,
                        'max_epoch': 50,
                        'lr': 0.0005,
                        'shuffle_train': False,
                        'early_stop_rounds': 5,
                        'scheduler': None
                    },
                    'no_shuffle': False,
                    'proc_ver': 'v00',
                    'p t_model_kwargs': {},
                    'pt_model_uri': 'infer_utils.DNNLR',
                    'qlib_model_default_kwargs_gen': 'utils.get_qlib_pt_model_kwargs',
                    'qlib_model_uri': 'infer_utils.DNNModelPytorch',
                    'repeat_n': 1,
                    'retrain': False,
                    'retrain_start': None,
                    'reweighter': None,
                    'run_num': 1,
                    'scheduler': None,
                    'seed': 42,
                    'seg_n': 120,
                    'simple_split_n': 1000,
                    'test_seg': None,
                    'train_start': 0
                }
            }, ),
            'kwargs': {}
        }
        print(pn.convert2basic(obj))
    # TODO:
    # def test_general_object(self):..


if __name__ == "__main__":
    unittest.main()
