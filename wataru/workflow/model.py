import wataru.workflow.utils as wfutils


class Model:
    def __init__(self, data, material_location, name):
        self.data = data
        self.material_location = material_location
        self.name = name

    def prepare(self):
        print('prepare done.')

    def prepare_finished(self):
        print('prepare finished done.')


    def fit(self):
        print('fit done.')

    def save(self):
        print('save done.')


def _wrap_fit(fit_function):
    def _func(model):
        data = model.data
        args, kwargs = model._param.item
        return fit_function(model, data, args, kwargs)
    return _func


def model_generator(load_function = None, fit_function = None, save_function = None, name_function = None, params = [], parent_class = Model):
    wf_params = wfutils.get_converted_params(params)

    for p in wf_params:
        class_name = parent_class.__name__ + '|' + p.name
        attrs = {'param': p}
        if load_function is not None:
            attrs['load'] = _wrap_load(load_function)
        if fit_function is not None:
            attrs['fit'] = _wrap_fit(fit_function)
        if save_function is not None:
            attrs['save'] = _wrap_save(save_function)
        yield type(
            class_name,
            (parent_class,),
            attrs,
        )
