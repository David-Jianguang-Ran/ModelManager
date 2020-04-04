from random import random
from django.test import TestCase

# tests for models
from mod_man.interface import *
from mod_man.models import *


class FakeModel:
    def __init__(self):
        self.saved = False

    def save(self,path):
        self.saved = True


class RecorderMixin:
    """
    this class provides functionality for building recorder callbacks
    and do simulated training on it
    """
    @staticmethod
    def get_recorder(tags):
        recorder_callback = RecorderCallback(tags=tags)
        dummy_model = FakeModel()
        recorder_callback.set_model(dummy_model)
        return recorder_callback

    @staticmethod
    def simulate_training(recorder_callback):
        # its just like training if you squint (-)_(-)
        data_slope = random()
        for i in range(0,100):
            recorder_callback.on_epoch_end(
                i,
                {
                    "loss":data_slope *(100 - i),
                    "acc":data_slope * (i)
                }
            )
        return recorder_callback


class InterfaceTest(TestCase, RecorderMixin):
    
    def setUp(self) -> None:
        # make some dummy db records, collect id in self.model_ids
        self.model_ids = []
        tags = ["existing_tag_1"]
        for i in range(0,10):
            rec = self.get_recorder(tags)
            rec = self.simulate_training(rec)
            rec.on_train_end()
            self.model_ids.append(str(rec.kmodel.id))
        
    def test_get_history_str(self):
        # for a valid model id, dict object should be returned
        result_1 = get_history(self.model_ids[0])
        self.assertTrue(isinstance(result_1,dict))
        self.assertEqual(["loss","acc"],list(result_1.keys()))
        
        # for a non valid model id, nothing should be returned
        result_2 = get_history("invalid model id")
        self.assertIsNone(result_2)

        # for a uuid that isn't a valid model id, nothing should be returned either
        result_3 = get_history(str(uuid4()))
        self.assertIsNone(result_3)

    def test_get_history_obj(self):
        # get our kmodel instance from id
        kmodel_1 = KModel.objects.get(id=self.model_ids[-1])

        # for a model with history artifact, a dict should be returned
        result_1 = get_history(kmodel_1)
        self.assertTrue(isinstance(result_1,dict))
        self.assertEqual(["loss","acc"],list(result_1.keys()))

        # for a model without history artifact, return none

        kmodel_2 = KModel()
        kmodel_2.save()

        result_2 = get_history(kmodel_2)
        self.assertIsNone(result_2)

    def test_plot_history_many_mixed(self):
        # replace some str model ids with model obj
        some_replaced = [(random() >= 0.5) and id or KModel.objects.get(id=id) for id in self.model_ids]

        result = plot_history_many(some_replaced[0:2])

        self.assertTrue(isinstance(result, plt.Figure))
        result.show()


class RecorderTest(TestCase, RecorderMixin):

    def setUp(self):
        self.tags_test = ["test_tag_1", "test_tag_2","existing_tag_1"]

    def test_on_epoch_end(self):

        recorder = self.get_recorder(self.tags_test)

        # call the method 100 times (simulated training)
        for i in range(0,100):
            recorder.on_epoch_end(
                i,
                {
                    "loss":float(100 + i),
                    "acc":float(i)
                }
            )

        expected = {
            "loss" : [float(100 + i) for i in range(0,100)],
            "acc": [float(i) for i in range(0, 100)]
        }

        self.assertEqual(recorder.history,expected)

    def test_on_train_end(self):

        recorder = self.get_recorder(self.tags_test)
        recorder = self.simulate_training(recorder)
        recorder.on_train_end()

        # test if db record and keras model are saved
        model_id = str(recorder.kmodel.id)
        db_model = KModel.objects.get(id=model_id)
        self.assertTrue(isinstance(db_model,KModel))
        self.assertTrue(recorder.model.saved)

        # test if tags are saved
        self.assertEqual(["test_tag_1", "test_tag_2","existing_tag_1"],list(db_model.tags.values_list("title",flat=True)))

        # test if path is populated
        self.assertEqual(db_model.path,KMODEL_DIR + "/" + model_id + ".h5")

        # test if history is saved
        db_history = db_model.artifacts.get(descriptor="history")
        self.assertEqual(pickle.load(open(db_history.path,"rb")),recorder.history)
