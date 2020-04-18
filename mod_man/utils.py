import pandas as pd

from django.db.models.query import QuerySet


def query_set_to_df(q_set : QuerySet):
    """
    this function returns a pandas DataFrame with data from given django queryset
    """
    return pd.DataFrame(q_set.values())


def query_set_to_html(q_set : QuerySet):
    """
    This function returns a simple html table from the query_set obj
    note: this is a temporary solution, in future version the same functionality
    will be carried out via django templates
    TODO : rebuild this via django templates
    """
    data = q_set.values()
    frame = pd.DataFrame(data)
    return frame.to_html(notebook=True), list(frame['id'])