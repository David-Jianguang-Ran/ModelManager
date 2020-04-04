import pickle
import pandas as pd
import matplotlib.pyplot as plt

from tensorflow.contrib import keras
from .models import KModel

from django.core.exceptions import ObjectDoesNotExist, ValidationError

# This interfaces here are sort of like django views
# but they are meant for a python API, not designed to be request handlers


def get_history(kmodel=None):
    """
    returns a python dict with key = metric_id val = [metric each epoch ]
    """
    if isinstance(kmodel,str):
        try:
            kmodel = KModel.objects.get(id=kmodel)
        except ObjectDoesNotExist:
            return None
        except ValidationError:
            return None
    elif isinstance(kmodel, KModel):
        # awesome! proceed
        pass
    else:
        raise ValueError("call get_history with etiher a str uuid for model or a db model instance")

    if kmodel.artifacts.filter(descriptor="history").exists():
        artifact_path = kmodel.artifacts.get(descriptor="history").path
        return pickle.load(open(artifact_path,"rb"))
    else:
        return None


def plot_history_many(in_models:[]=(None),lateral_compare=False,ignore_none=False):
    """
    in_models : list of any combinations of str or db kmodel instance
    return : a matplotlib figure obj
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

        def _reorganize_history(model_id,history_dict):
            for metric, values in history_dict.items():
                lateral_history[metric].update(model_id,values)

        map(_reorganize_history,history_table.items())
        history_table = lateral_history

    fig, ax = plt.subplots(len(history_table))

    # plot declaration function
    def _plot_each_metric(graph_title: str, label_history: dict, i: int):
        """
        this function is to be mapped to a history table
        this generates a subplot for each top level key,
        each metric series is labeled with second level key
        """
        for metric_label, metric_series in label_history:
            ax[i].scatter(metric_series, range(0, len(metric_series)), label=metric_label)
            # ax[i].title(graph_title)

    map(_plot_each_metric,*list(history_table.items()),range(0,len(history_table)))

    return fig


class RecorderCallback(keras.callbacks.Callback):
    """

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
