from django.test import TestCase

# tests for models
from mod_man.models import *


class ModelsTest(TestCase):

    def setUp(self):
        # get some tags first
        tags_str = ["existing_tag_1","existing_tag_2"]
        tags_obj = [Tags.objects.get_or_create(title=each_str)[0] for each_str in tags_str]

        # get a kmodel to serve as dummy parent
        self.model_test = KModel.objects.create(path="records/kmodel/non-existant-file.h5")

        for each_obj in tags_obj:
            self.model_test.tags.add(each_obj)

    def tearDown(self):
        KModel.objects.all().delete()
        Tags.objects.all().delete()
        self.model_test = None

    def test_kmodel_path(self):
        # checking if path has correct format
        self.assertEqual(self.model_test.path[-3:], ".h5")
        self.assertEqual(self.model_test.path[:len(KMODEL_DIR)], KMODEL_DIR)

    def test_add_notes_empty(self):
        k_mod = KModel.objects.get(id=self.model_test.id)
        test_string = "test string"
        k_mod.add_note(test_string)

        self.assertEqual(k_mod.notes,str(datetime.datetime.now())[:-7] + "  " + test_string)

    def test_add_notes_append(self):
        k_mod = KModel.objects.get(id=self.model_test.id)
        k_mod.add_note("first string")
        k_mod.add_note("second string")

        print(k_mod.notes)
        self.assertTrue(type(k_mod.notes) == str)

    def test_add_tags(self):
        kmod = self.model_test
        kmod.add_tags(["new_tag_1","new_tag_2","existing_tag_1"])

        self.assertIn("new_tag_1",kmod.tags.values_list("title",flat=True))
        self.assertIn("new_tag_2", kmod.tags.values_list("title", flat=True))
        self.assertIn("existing_tag_1", kmod.tags.values_list("title", flat=True))

    def test_remove_tags(self):
        kmod = self.model_test
        kmod.remove_tags(["existing_tag_1","new_tag_2"])

        self.assertNotIn("existing_tag_1",kmod.tags.values_list("title",flat=True))
        self.assertNotIn("new_tag_2", kmod.tags.values_list("title", flat=True))

    def test_add_artifact_pickle(self):
        kmod = self.model_test
        test_payload = {"name":"test object", "purpose":"to test!"}
        art_mod = kmod.add_artifact(test_payload,descriptor="tester")

        # checking if relationship exists
        self.assertTrue(kmod.artifacts.filter(id=art_mod.id).exists())
        self.assertEqual(art_mod.parent.id,kmod.id)

        # checking if path has correct format
        self.assertEqual(art_mod.path[-7:],".pickle")
        self.assertEqual(art_mod.path[:16],ARTIFACT_DIR)

        # test loading payload and compare
        self.assertEqual(str(pickle.load(open(art_mod.path,"rb"))),str(test_payload))


