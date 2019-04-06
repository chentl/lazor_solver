import pickle


def deepcopy(sth):
    """ A fast deepcopy. (Faster than copy.deepcopy() for usage in this project.)  """

    return pickle.loads(pickle.dumps(sth))

