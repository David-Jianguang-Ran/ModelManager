import pandas as pd

from django.db.models.query import QuerySet


def query_set_to_df(q_set : QuerySet):
    """
    this function returns a pandas DataFrame with data from given django queryset
    """
    return pd.DataFrame(q_set.values())

