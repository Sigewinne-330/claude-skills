// Compile every LaTeX snippet with MathJax 3 and report errors (undefined macros, missing braces...).
// Setup once in the working dir:  npm i mathjax-full@3 --silent
// Run:  NODE_PATH=$PWD/node_modules node "$SKILL/scripts/texcheck.js" out/maths.json
const path = require('path');
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {TeX} = require('mathjax-full/js/input/tex.js');
const {AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js');
const {SVG} = require('mathjax-full/js/output/svg.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
const a = liteAdaptor(); RegisterHTMLHandler(a);
const doc = mathjax.document('', {InputJax: new TeX({packages: AllPackages}), OutputJax: new SVG()});
const ms = require(path.resolve(process.argv[2]));
let bad = 0;
ms.forEach((m, i) => {
  const h = a.outerHTML(doc.convert(m, {display: true}));
  if (/merror|fill="red"|color="red"/.test(h)) {
    bad++; console.log('ERR', i, m, (h.match(/data-mjx-error="([^"]*)"/) || [])[1] || 'undefined macro');
  }
});
console.log('checked', ms.length, 'errors', bad);
process.exit(bad ? 1 : 0);
