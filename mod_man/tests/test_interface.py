from django.test import TestCase

# tests for models
from mod_man.interface import RecorderCallback
from mod_man.models import *


class FakeModel:
    def __init__(self):
        self.saved = False

    def save(self,path):
        self.saved = True


class RecorderCallbackTest(TestCase):

    def setUp(self):
        tags_test = ["test_tag_1", "test_tag_2","existing_tag_1"]
        self.call_back_instance = RecorderCallback(tags=tags_test)

        dummy_model = FakeModel()
        self.call_back_instance.set_model(dummy_model)

    def test_on_epoch_end(self):

        # call the method 100 times (simulated training)
        for i in range(0,100):
            self.call_back_instance.on_epoch_end(
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

        self.assertEqual(self.call_back_instance.history,expected)

    def test_on_train_end(self):

        # call the method 100 times (simulated training)
        for i in range(0,100):
            self.call_back_instance.on_epoch_end(
                i,
                {
                    "loss":float(100 + i),
                    "acc":float(i)
                }
            )

        self.call_back_instance.on_train_end()

        self.assertTrue(KModel.objects.filter(name=self.call_back_instance.kmodel.name).exists())
        self.assertTrue(self.call_back_instance.model.saved)
