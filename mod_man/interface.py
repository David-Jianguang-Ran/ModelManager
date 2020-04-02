import pickle
import matplotlib.pyplot as plt

from tensorflow.contrib import keras
from .models import KModel


# This interfaces here are sort of like django views
# but they are meant for a python API, not designed to be request handlers


class RecorderCallback(keras.callbacks.Callback):
    def __init__(self,db_model=None,tags=()):
        super().__init__()

        # instanciate a db model
        if not db_model:
            self.kmodel = KModel()
            self.kmodel.save()

        self.history = {}
        self.epochs = 0

        self.tags = tags

    def set_model(self, model):
        self.model = model

    def on_epoch_end(self, epoch, logs=None):
        self.epochs += 1
        logs = logs and logs or {}

        # append value for this epoch to history object
        for key, val in logs.items():
            try:
                self.history[key].append(val)
            except KeyError:
                self.history[key] = [val]

    def on_train_end(self, logs=None):
        """ save model to disk and fill in db record"""
        # save model to disk
        self.model.save(self.kmodel.default_path)

        # add fields to db records
        self.kmodel.path = self.kmodel.default_path
        self.kmodel.loss = self.history['loss'][-1]
        self.kmodel.add_tags(self.tags)

        # update # of epochs trained
        if not self.kmodel.epochs_trained:
            self.kmodel.epochs_trained = self.epochs
        else:
            self.kmodel.epochs_trained = self.epochs + self.kmodel.epochs_trained

        # record val loss, if available
        try:
            self.kmodel.loss = self.history['val_loss'][-1]
        except KeyError:
            pass

        self.kmodel.save()
