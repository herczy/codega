codega
======

What is codega?
---------------

codega is a code-generator framework for creating C/C++/Python/etc. code. The output is specified with a mixture of
Python code and templates (currently mako is supported by the extras) or just Python code.

Where can I find it?
--------------------

codega can be found at https://github.com/herczy/codega. The same page has a wiki with some help pages
on codega. For starters, consider reading the overview of codega at https://github.com/herczy/codega/wiki/Overview.

What stage is it in?
--------------------

The first public release is due after the user guide and various documentations will be ready. For now, it is in an
alpha stage: the code at this point is semi-stable: all updates to the configure format will remain backwards-compatible,
features are added often, but without significantly changing the interfaces. It doesn't do much yet beyond providing a
framework and having a few examples. You can try it out if you have the inclination:

::

    $ ./cgx make -c examples/basic/codega.xml
