What is codega?
===============

codega is a code and (generally speaking) text generation framework. The purpose is not to
have a template engine (cheetah and mako do it better, and in fact, the `cgextra` module
contains a mako template binding) but to have a way to break up the generation process, have
separate template definitions and pre- or post-processing code, a simple build system, etc.)

Why are stand-alone templates not enough?
-----------------------------------------

The classic problem with generating code with a template is that the template code and the
'real' code can be hard to keep separate. So you have some mako code to generate a structure:

::

    <def name="structure(node)">
    typedef struct _${node.name}
    {
    % for field in ${map(render, node.children)}:
    ${field}
    % endfor
    } ${node.name};
    </def>

If all you want is this, no problem. But chances are you'd like to do other things not closely
related to the generation, like collect type information. You'd have to add a global type
dictionary or something like that. This is still easy to add to the above example.

But as more and more information needs to be gathered, the templates get more and more unreadable.
Too much code gets integrated into the template definition, the template needs to do more and more
tasks and it soon gets out of control. If you forgive the personal tone, I had to find out this
the hard way.

What does codega provide?
-------------------------

codega, on itself does nothing really. It is a framework or rather a collection of tools.
You need some source to use for the generation and a generator.

The following are provided to acomplish this:

* Generator classes. The generators convert the source into the desired output. These
  classes provide some common generator functions.
* Source classes. These provide the XML parser (default) and some base classes for
  custom source classes.
* A very simple builder for building the specified sources into the targets given.
* Configuration classes for creating codega-specific build scripts.
* Extras, like mako template wrappings, dictionary tools to use with some generators, etc.
  These are the classes and functions that could not be easily fit into the core, but had
  to go somewhere. In the future they'll be separated.

How to install?
---------------

codega supports installation but strictly speaking it's not required. First you need to download
the current [[tarball|https://github.com/herczy/codega/tarball/current]],
[[zip file|https://github.com/herczy/codega/zipball/current]], or you can check out the current version
of the git repository:

::

    git clone git://github.com/herczy/codega.git

After you have the source you can either run the provided setup.py script or you can create a
self-contained script. This script contains the full module and if it does not find the codega
module, it extracts it in the current directory.

To create the self-contained script, run

::

    ./cgx pack <self-contained script>

You can copy the self-contained script where you'd like to use it. This script has the exact
same functionality as the installed version.

Are there any docs?
-------------------

Yes, the following (this will be expanded):

* [[Overview of codega|Overview]] - you should start here
* [[Description of the configuration format|ConfigFormat]]
* [[API documentation|http://herczy.github.com/codega/doc/index.html]]

License
-------

codega is released under the BSD license. Basically you can use it for whatever you'd like
provided that you respect the few small requirements in the LICENSE file (provided with
the codega source).

Author
------

Viktor Hercinger <hercinger.viktor@gmail.com>

If you have trouble with codega or you want a question, ask me, I'll gladly help.

NOTE
====

This documentation is somewhat outdated, but will be updated around July. Most of the information
is still valid.
