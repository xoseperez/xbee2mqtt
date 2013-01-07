class FilterFactory(object):

    filters = []

    @staticmethod
    def register(filter):
        FilterFactory.filters.append(filter)

    def __new__(self, type):
        for filter in self.filters:
            if filter.name == type:
                return filter()
        return None

class Filter(object):

    name = ''

    parameters = None

    required = []

    def configure(self, parameters):
        self.parameters = parameters

    def validate(self):
        for key in self.required:
            if key not in self.parameters:
                return False
        return True

    def process(self, value):
        return value

class LinearFilter(Filter):
    name = 'linear'
    required = ['slope', 'offset']
    def process(self, value):
        return int(self.parameters['slope'] * value + self.parameters['offset'])
FilterFactory.register(LinearFilter)

class BooleanFilter(Filter):
    name = 'boolean'
    required = []
    def process(self, value):
        return 0 if value == 0 else 1
FilterFactory.register(BooleanFilter)

class NotFilter(Filter):
    name = 'not'
    required = []
    def process(self, value):
        return 1 if value == 0 else 0
FilterFactory.register(NotFilter)

class EnumFilter(Filter):
    name = 'enum'
    required = []
    def process(self, value):
        for from_value, to_value in self.parameters.iteritems():
            if value == from_value:
                return to_value
        return to_value
FilterFactory.register(EnumFilter)

class StepFilter(Filter):
    name = 'step'
    required = []
    def process(self, value):
        for threshold, to_value in self.parameters.iteritems():
            if value <= threshold:
                return to_value
        return to_value
FilterFactory.register(StepFilter)

