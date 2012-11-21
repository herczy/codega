import os

from codega.decorators import abstract
from codega.generator.base import GeneratorBase
from codega.variant import use_variant, get_variant
from codega.generator.priority import PriorityGenerator, PRI_FALLBACK, PRI_BASE
from codega.matcher import matcher, all, true
from codega.generator.template import TemplateGenerator
from codega.config import structures
from codega.source import SourceBase
from codega.alp.inline import build
import types


def walk_settings(base, keystub=()):
    for key, value in base.items():
        if isinstance(value, structures.Settings.RecursiveContainer):
            for res in walk_settings(value, keystub + (key,)):
                yield res

            continue

        yield '.'.join(keystub + (key,)), value


class AutoGenerator(PriorityGenerator):
    def __init__(self, templates):
        self._template_set = templates

        self.register_subgenerators()

    @abstract
    def register_subgenerators(self):
        pass

    def _get_bindings(self, source, context, variant=None):
        return dict(source=source, generate=lambda item: self.__generate_with_variant(item, context, variant=variant))

    def __generate_with_variant(self, source, context, variant=None):
        if variant is None:
            return self.generate(source, context)

        with use_variant(context, variant):
            return self.generate(source, context)


class AlpAutoGenerator(AutoGenerator):
    def __init__(self, templates, mapping):
        super(AlpAutoGenerator, self).__init__(templates)

        self.__mapping = mapping

    def register_subgenerators(self):
        for matcher, priority, tplname in self.__mapping.items():
            tpl = self.__template_set.get_template(tplname)
            gen = TemplateGenerator(tpl, self._get_bindings)

            self.register(gen, priority=priority, matcher=matcher)


class ModuleBase(object):
    def __init__(self, locator, module_config):
        self.__locator = locator
        self.__module_config = module_config
        self.__module = module_config.reference.load(locator)

    @property
    def locator(self):
        return self.__locator

    @property
    def module_config(self):
        return self.__module_config

    @property
    def module(self):
        return self.__module

    @property
    def config(self):
        return self.__module_config.root

    @abstract
    def get_parser(self, source):
        pass

    @abstract
    def get_generator(self, target):
        pass

    @abstract
    def get_config(self):
        pass


class AlpCache(object):
    def __init__(self, sources, cachedir):
        self.__sources = sources
        self.__cachedir = cachedir

    def get_module(self, source):
        dest = self.__get_dest_name(source)
        if not os.path.isfile(dest):
            self.__build(source)

        retmod = types.ModuleType(os.path.splitext(source)[0])
        execfile(dest, retmod.__dict__)

        return retmod

    def __build(self, source):
        filename = self.__get_source_name(source)
        dest = self.__get_dest_name(source)

        with open(filename) as src:
            code = build(src, source)

        with open(dest, 'w') as out:
            out.write(code)

        return filename

    def __get_source_name(self, source):
        return os.path.join(self.__sources, source)

    def __get_dest_name(self, source):
        return os.path.join(self.__cachedir, os.path.splitext(source)[0] + '.py')


class AlpSource(SourceBase):
    def __init__(self, alp_module):
        self.__alp = alp_module

    def load(self, resource, resource_locator=None):
        if resource_locator is not None:
            resource = resource_locator.find(resource)

        return self.__alp.parse_file(resource)


class AlpModuleBase(ModuleBase):
    #sources = ()
    #targets = ()
    #copy = ()

    def __init__(self, locator, module_config):
        super(ModuleBase, self).__init__(locator, module_config)

        basedir = os.path.dirname(self.module.__file__)
        sources = os.path.join(basedir, 'alp')
        cachedir = os.path.join(os.getenv('HOME'), '.alpcache')
        if not os.path.isdir(cachedir):
            os.mkdir(cachedir)

        self.__alp_cache = AlpCache(sources, cachedir)

    def get_config(self):
        builder = structures.StructureBuilder()
        builder.paths.destination = self.config.paths.destination
        builder.paths.paths.extend(self.config.paths)

        scandir = self.module_config.settings.safe_get('scandir', '.')
        files = self.module_config.settings.safe_get

    '''
        for source, alp, transform in self.sources:
            builder.add_source(source, source, alp, transform=transform)

        for target, source, variant in self.targets:
            builder.add_target(source, target, variant, settings=walk_settings(self.config.settings))

        for source, dest in self.copy:
            builder.add_copy(source, dest)
    '''

    def get_parser(self, source):
        alpmod = self.__alp_cache.get_module(source.resource)
        return AlpSource(alpmod)

    def get_generator(self, target):
        #gen = 
