from uuid import uuid4
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import datetime
import pickle

# note to self, there are some hardcoded settings in here
# TODO refactor settings into a settings file
# set some global vars of my own (non-django for now)
KMODEL_DIR = "records/kmodel"
ARTIFACT_DIR = "records/artifact"


class Tags(models.Model):
    """
    Text tags used only with KModel instances
    """
    title = models.CharField(max_length=64)

    # foreign key relationships
    # models => KModel class : many to many


class BaseModel(models.Model):

    class Meta:
        abstract = True
    """
    provides functionality for keeping track of local files and appending notes
    """
    # basic info
    name = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    path = models.CharField(max_length=256,null=True)

    # notes
    # TODO refactor notes into artifact i guess
    notes = models.TextField()

    # star / flag system
    stared = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    def add_notes(self,string_notes):
        """
        this method appends notes to existing notes with a time stamp <= dumb string nothing fancy
        """
        string_notes = str(datetime.datetime.now())[:-7] + "  " + string_notes

        if not self.notes:
            self.notes = string_notes
        else:
            self.notes = str(self.notes + "\n" + string_notes)

        self.save()


class KModel(BaseModel):
    """
    This class is a db representation of a tensorflow keras model
    """
    # metrics
    epochs_trained = models.IntegerField(null=True)

    loss = models.IntegerField(null=True)
    val_loss = models.IntegerField(null=True)

    # tags
    tags = models.ManyToManyField(Tags,related_name="models")

    # foreign key relationships
    # artifacts => Artifact class : one to many
    @property
    def default_path(self):
        return str(KMODEL_DIR + "/" + str(self.name) + ".h5")

    def add_artifact(self, artifact=None, descriptor="unspecified", plot=False):
        """
        dumps non image artifact obj into pickle, create db record,
        returns django model instance
        """
        # create db record
        artifact_model = Artifact(path=None, descriptor=descriptor, parent=self)

        # dump artifact into file system and save the path to django model
        if not plot:
            path = ARTIFACT_DIR + "/" + str(artifact_model.name) + ".pickle"
            pickle.dump(artifact, open(path, "wb"))
        else:
            path = ARTIFACT_DIR + "/" + str(artifact_model.name) + ".png"
            artifact.savefig(path)
        artifact_model.path = path
        artifact_model.save()

        return artifact_model

    def add_tags(self,tags_str=()):
        """
        this one finds tag obj by str title and add relation to self
        """
        if type(tags_str) == str:
            tags_str = [tags_str]

        for each_str in tags_str:
            tag_obj = Tags.objects.get_or_create(title=each_str)[0]
            self.tags.add(tag_obj)

    def remove_tags(self,tags_str=()):
        """
        removes db relationship to the tag but not the tag itself
        """
        if type(tags_str) == str:
            tags_str = [tags_str]

        for each_str in tags_str:
            try:
                self.tags.remove(self.tags.get(title=each_str))
            except ObjectDoesNotExist:
                continue


class Artifact(BaseModel):
    """
    This class stores reference to local files that are related to kmodels
    TODO implement special class for keeping pickled python objects
    """

    # a short string denote the type of data this artifact is
    descriptor = models.CharField(max_length=64)

    parent = models.ForeignKey(KModel,related_name="artifacts",on_delete=models.CASCADE)

