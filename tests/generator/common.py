from codega.generator.base import GeneratorBase

from tests.common import MockMaker

SimpleGeneratorFactory = MockMaker(bases=(GeneratorBase,), name='SimpleGenerator')
SimpleGeneratorFactory.add_function('validate')
SimpleGeneratorFactory.add_function('generate')
SimpleGenerator = SimpleGeneratorFactory.create_mock_class()
