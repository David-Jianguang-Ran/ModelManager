import pickle
import pandas as pd
import matplotlib.pyplot as plt

from tensorflow import keras
from .models import KModel

from django.core.exceptions import ObjectDoesNotExist, ValidationError
# This interfaces here are sort of like django views
# but they are meant for a python API, not designed to be request handlers


def get_history(kmodel=None):
    """
    returns a python dict with key = metric_id val = [metric each epoch ]
    """
    # get kmodel object from input str if the input is a string
    if isinstance(kmodel,str):
        try:
            kmodel = KModel.objects.get(id=kmodel)
        except ObjectDoesNotExist:
            # object with name doesn't exist
            return None
        except ValidationError:
            # input string isn't a valid uuid
            return None
    elif isinstance(kmodel, KModel):
        # awesome! proceed
        pass
    else:
        raise ValueError("call get_history with etiher a str uuid for model or a db model instance")

    # get the history object and load history
    if kmodel.artifacts.filter(descriptor="history").exists():
        artifact_path = kmodel.artifacts.get(descriptor="history").path
        return pickle.load(open(artifact_path,"rb"))
    else:
        return None


def plot_history_many(in_models:[]=(None),lateral_compare=False,ignore_none=False):
    """
    in_models : list of any combinations of str or db kmodel instance
    return : a matplotlib figure obj, data dict
    """
    # iterate through in models and collect history
    history_table = {}
    for each_item in in_models:
        each_history = get_history(each_item)
        if each_history or not ignore_none:
            history_table[str(each_item)] = each_history

    # lateral as in show a plot of a single metric over time across many histories
    if lateral_compare:
        # define a function and map it across all model histories
        # all data is collected in lateral history
        # then assigned as the new history_table
        lateral_history = {}
        # TODO refactor this maybe? this is a lot of nested for loops
        for model_id, history_dict in history_table.items():
            for metric, values in history_dict.items():
                try:
                    lateral_history[metric][model_id] = values
                except KeyError:
                    lateral_history[metric] = {model_id : values}

        history_table = lateral_history

    fig, ax = plt.subplots(len(history_table),figsize=(10,8))

    # plot a graph (axe) for each item in the history table
    i = 0
    for graph_title, graph_content in history_table.items():
        ax[i].set_title(graph_title)
        for series_name, series_content in graph_content.items():
            ax[i].scatter(series_content, range(0, len(series_content)), label=series_name)
            ax[i].legend()
        i += 1

    return fig, history_table


class RecorderCallback(keras.callbacks.Callback):
    """
    this call back saves history data and keras model to disk
    and saves record to database
    note, the django model object can be accessed by callbackinstance.kmodel
    """
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
        """ record logs for each epoch"""
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

        # record history to db
        db_hist = self.kmodel.add_artifact(self.history,"history")

        self.kmodel.save()
