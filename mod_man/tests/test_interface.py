from random import random
from django.test import TestCase

# tests for models
from mod_man.interface import RecorderCallback
from mod_man.models import *


class FakeModel:
    def __init__(self):
        self.saved = False

    def save(self,path):
        self.saved = True


class InterfaceTest(TestCase):

    def setUp(self):
        self.tags_test = ["test_tag_1", "test_tag_2","existing_tag_1"]

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
        model_name = str(recorder.kmodel.name)
        db_model = KModel.objects.get(name=model_name)
        self.assertTrue(isinstance(db_model,KModel))
        self.assertTrue(recorder.model.saved)

        # test if tags are saved
        self.assertEqual(["test_tag_1", "test_tag_2","existing_tag_1"],list(db_model.tags.values_list("title",flat=True)))

        # test if path is populated
        self.assertEqual(db_model.path,KMODEL_DIR + "/" + model_name + ".h5")

        # test if history is saved
        db_history = db_model.artifacts.get(descriptor="history")
        self.assertEqual(pickle.load(open(db_history.path,"rb")),recorder.history)
