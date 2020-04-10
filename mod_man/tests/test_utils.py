import pandas as pd

from django.test import TestCase


from mod_man.utils import query_set_to_df
from mod_man.models import KModel, Tags


class ModelUtilsTest(TestCase):

    def setUp(self):
        # get some tags first
        tags_str = ["existing_tag_1","existing_tag_2"]
        tags_obj = [Tags.objects.get_or_create(title=each_str)[0] for each_str in tags_str]

        # get a kmodel to serve as dummy parent
        self.model_test = KModel.objects.create(path="records/kmodel/non-existant-file.h5")
        some_other_model = KModel.objects.create(path="records/kmodel/non-existant-file-2.h5")

        for each_obj in tags_obj:
            self.model_test.tags.add(each_obj)

    def tearDown(self):
        KModel.objects.all().delete()
        Tags.objects.all().delete()
        self.model_test = None

    def test_query_set_to_df(self):

        q_set = KModel.objects.all()

        result_df = query_set_to_df(q_set)

        self.assertTrue(isinstance(result_df,pd.DataFrame))
        self.assertEqual(list(result_df.columns),["id","path","timestamp","notes","stared","epochs_trained","loss","val_loss"])
        self.assertEqual(result_df.shape,(2,8))
