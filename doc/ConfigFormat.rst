codega build system
===================

codega comes with a built-in build system. This system can pair different sources (like
other XML sources, custom languages, etc.) with targets.

The build system can be configured with an XML file whose structure will be explained
in detail in this wiki page. This config file should be named *codega.xml* but this is
not required, merely the default filename cgx build will look for.

Overall format
--------------

The root node of a codega XML configuration file is the **config** element. This root node
has a **version** mandatory attribute.

::

    <config version="1.1">
        <paths>
            [path list, see Path list]
        </paths>

        <external>another config</external>
        ...

        <sources>
            [source list, see Sources]
        </sources>

        <targets>
            [target list, see Targets]
        </targets>
    </config>

Version attribute
.................

The root element (config) has a mandatory attribute, **version** which denotes the
configuration version to be used. Currently two versions are supported:

* 1.0: This was the initial version.
* 1.1: The filename node in a source definition was renamed to resource.
* 1.2: The external tag was introduced.

These two versions are compatible. But not all future versions will remain so. All
incompatible config version changes will have a different major version bumped.

Sections
--------

In codega there are three basic sections in building: source- and destination paths,
sources and targets.

Path list
.........

At the beginning of the config there should be a list of paths to be searched for
files and modules (see **parser** in the `Sources`_ section and **generator** in the
`Targets`_ section).

A destination path must be specified first, followed by at least one search path. All
these paths are interpreted relative to the config files path. The search paths are
scanned in the order they are in the list.

::

    <paths>
        <target>./</target>
        <path>./</path>
        <path>/usr/share/codega</path>
    </paths>

In the above example the target path is the same where the config file is and it is
also a search path (note that the target path is not a search path). The other search
path is /usr/share/codega (don't use this, it doesn't exists by default).

If no such section is specified, then no include paths will be used and the destination
directory will be the current path.

External
........

It is possible to specify any number of other config files which should be built prior
to building any targets in the config. This is useful if you have several inter-dependent
config files.

To specify an external dependency, use the `external` node.

::

    <external>path/of/other/codega.xml</external>

Sources
.......

Sources are the data inputs to be parsed and later - using a target - turned
into source or some other text. Sources have three different important attributes:

* a **name** which identifies the source. This must be unique in the project.
* a **parser** which identifies the parser module and class. The default parser
  class is codega.source:XmlSource . Each parser module is identified like the
  previous example: <python module>:<source class>
* a **resource** which identifies the source data. It can be anything ranging from
  filenames, Python modules, etc.

Any number of sources may be defined, but at least one is required. Sources are
listed in the **sources** section:

::

    <sources>
        <source>
            <name>somesource</name>
            <parser>some.module:SomeClass</parser>
            <resource>source.file</resource>
        </source>

        ...

    </sources>

In the above example we specified the parser class. This is optional, if omitted, the
source is assumed to be an XML file.

Targets
.......

Targets describe how a source will be turned into generated code (or text, or whatever
you specify). Target generation relies on so-called **generators**. Generators are classes
derived from GeneratorBase. The process of doing this is described in a different place.

Targets have three attributes (all mandatory):

* a **source** name, which refers to a source defined in the previous section.
* a **generator**, which has the same format as the parser in the previous section.
  So a *HeaderGenerator* class defined in the *generator* module would be referred to
  as *generator:HeaderGenerator*.
* a **target** file name. This will be relative to the defined destination in the `Path list`_

A typical target definition looks like this:

::

    <targets>
        <target>
            <source>somesource</source>
            <generator>some.module:SomeOtherClass</generator>
            <target>output.file</target>
        </target>
    </targets>

A full example
--------------

As seen in the codega repository in examples/books/codega.xml

::

    <?xml version="1.0" ?>
    <config version="1.0">
        <paths>
            <target>./</target>
            <path>./</path>
        </paths>
        <source>
            <name>books</name>
            <filename>books.xml</filename>
        </source>
        <target>
            <source>books</source>
            <generator>bookgen:CBookGenerator</generator>
            <target>books.c</target>
        </target>
        <target>
            <source>books</source>
            <generator>bookgen:HtmlBookGenerator</generator>
            <target>books.html</target>
        </target>
    </config>

This generates a small C source file and an HTML file. For further explanation,
see the previous sections.
