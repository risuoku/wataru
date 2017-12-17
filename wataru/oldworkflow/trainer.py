class Trainer:
    def run(self):
        raise NotImplementedError()


def default_name_function(d):
    return 'Trainer__' + '_'.join(['{}{}'.format(k, v) for k, v in d.items()])


def trainer_factory_generator(iterator):
    pass
