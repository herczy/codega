from codega.generator import *
from codega.visitor import find_method
from codega.ordereddict import OrderedDict

from codega.cgextra.makowrapper import inline
from codega.cgextra.dicttools import *
from codega.cgextra.indent import *
from codega.cgextra import matcher

def checknone(

class InfoVisitor(XmlVisitor):
    def visit_project(self, node, info):
        info['project'] = node.text

    def visit_color(self, node, info):
        map(lambda n: self.visit(n, colors)

class Pagen(ObjectGenerator):
    @inline(matcher = matcher.tag('pagen')
    @autobindict
    def generate_main(self, source, context, bindings):
        '''
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset='utf-8'>

          <title>herczy/codega @ GitHub</title>

          <style type="text/css">
            body {
              margin-top: 1.0em;
              background-color: #13a4ea;
              font-family: Helvetica, Arial, FreeSans, san-serif;
              color: #000000;
            }
            #container {
              margin: 0 auto;
              width: 700px;
            }
            h1 { font-size: 3.8em; color: #ec5b15; margin-bottom: 3px; }
            h1 .small { font-size: 0.4em; }
            h1 a { text-decoration: none }
            h2 { font-size: 1.5em; color: #ec5b15; }
            h3 { text-align: center; color: #ec5b15; }
            a { color: #ec5b15; }
            .description { font-size: 1.2em; margin-bottom: 30px; margin-top: 30px; font-style: italic;}
            .download { float: right; }
            pre { background: #000; color: #fff; padding: 15px;}
            hr { border: 0; width: 80%; border-bottom: 1px solid #aaa}
            .footer { text-align:center; padding-top:30px; font-style: italic; }
          </style>
        </head>

        <body>
          <a href="http://github.com/herczy/codega"><img style="position: absolute; top: 0; right: 0; border: 0;" src="http://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png" alt="Fork me on GitHub" /></a>

          <div id="container">

            <div class="download">
              <a href="http://github.com/herczy/codega/zipball/master">
                <img border="0" width="90" src="http://github.com/images/modules/download/zip.png"></a>
              <a href="http://github.com/herczy/codega/tarball/master">
                <img border="0" width="90" src="http://github.com/images/modules/download/tar.png"></a>
            </div>

            <h1><a href="http://github.com/herczy/codega">codega</a>
              <span class="small">by <a href="http://github.com/herczy">herczy</a></span></h1>

            <div class="description">
              Code generation suite
            </div>

            <p>codega aims to create a simple-to-use code generation suite in Python, but not only for Python. It is in a pre-beta stage, the first usable release (with a few working generators) will be done around December, 2011.</p><h2>Dependencies</h2>
        <p>mako (if you plan to use the codega.cgextra helpers)
        lxml</p>
        <h2>Install</h2>
        <p>Check out github.com/herczy/codega (or download one of the snapshots) and install it.</p>
        <h2>License</h2>
        <p>BSD</p>
        <h2>Authors</h2>
        <p>Hercinger Viktor (hercinger.viktor@gmail.com)<br/><br/>      </p>
        <h2>Contact</h2>
        <p>Hercinger Viktor (hercinger.viktor@gmail.com)<br/>      </p>


            <h2>Download</h2>
            <p>
              You can download this project in either
              <a href="http://github.com/herczy/codega/zipball/master">zip</a> or
              <a href="http://github.com/herczy/codega/tarball/master">tar</a> formats.
            </p>
            <p>You can also clone the project with <a href="http://git-scm.com">Git</a>
              by running:
              <pre>$ git clone git://github.com/herczy/codega</pre>
            </p>

            <div class="footer">
              get the source code on GitHub : <a href="http://github.com/herczy/codega">herczy/codega</a>
            </div>

          </div>

          
        </body>
        </html>
        '''
