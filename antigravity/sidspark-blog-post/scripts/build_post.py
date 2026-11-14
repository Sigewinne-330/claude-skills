#!/usr/bin/env python3
"""post.txt (light markdown) -> Gutenberg block markup + chunks for browser transfer.
Usage: python3 "$SKILL/scripts/build_post.py" post.txt figs/ out/
Source format (blocks separated by blank lines):
  TITLE: ...            first line
  EXCERPT: ...          optional second line
  ## Heading / ### Sub  headings (math allowed)
  $$ ... $$             alone in a block -> centred display-math paragraph (use \\tag{n})
  > line                quote block; each > line = one paragraph inside it
  - item                list (one item per line)
  [[FIG name|Figure n. caption]]   inline SVG from figs/name.svg in a wp:html block
  <!-- wp:... -->        raw Gutenberg block passed through untouched (e.g. a wp:table)
  anything else         paragraph (single line); **bold**, *italic*, $inline$ math
"""
import re, json, sys, os
src_path, fig_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out_dir, exist_ok=True)
lines = open(src_path, encoding='utf-8').read().strip().split('\n')
meta = {}
while lines and re.match(r'^(TITLE|EXCERPT):', lines[0]):
    k, v = lines.pop(0).split(':', 1); meta[k.lower()] = v.strip()
blocks = re.split(r'\n\s*\n', '\n'.join(lines).strip())

def inline(t):
    maths = []
    def keep(m):
        maths.append(m.group(0)); return f'\x00{len(maths)-1}\x00'
    t = re.sub(r'\$\$.+?\$\$|\$[^$]+?\$', keep, t)
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: maths[int(m.group(1))].replace('&', '&amp;').replace('<', '\\lt ').replace('>', '\\gt '), t)
    if '*' in t.replace('\\ast', ''):
        sys.exit(f'Unconverted * in: {t[:80]}')
    return t

def para(t, center=False):
    if center:
        return f'<!-- wp:paragraph {{"align":"center"}} -->\n<p class="has-text-align-center">{inline(t)}</p>\n<!-- /wp:paragraph -->'
    return f'<!-- wp:paragraph -->\n<p>{inline(t)}</p>\n<!-- /wp:paragraph -->'

out = []
for b in blocks:
    b = b.strip()
    if b.startswith('<!-- wp:'):
        out.append(b)
    elif b.startswith('### '):
        out.append(f'<!-- wp:heading {{"level":3}} -->\n<h3 class="wp-block-heading">{inline(b[4:])}</h3>\n<!-- /wp:heading -->')
    elif b.startswith('## '):
        out.append(f'<!-- wp:heading -->\n<h2 class="wp-block-heading">{inline(b[3:])}</h2>\n<!-- /wp:heading -->')
    elif b.startswith('[[FIG'):
        m = re.match(r'\[\[FIG ([\w-]+)\|(.+)\]\]$', b)
        name, cap = m.group(1), m.group(2)
        svg = open(os.path.join(fig_dir, f'{name}.svg'), encoding='utf-8').read().strip()
        cm = re.match(r'(Figure \d+\.)(.*)', cap)
        caph = f'<strong>{cm.group(1)}</strong>{inline(cm.group(2))}' if cm else inline(cap)
        out.append('<!-- wp:html -->\n<figure class="sidspark-fig" style="margin:2em auto;max-width:680px;text-align:center">'
                   + svg + f'<figcaption style="font-size:0.9em;opacity:0.8;margin-top:0.6em;text-align:center">{caph}</figcaption></figure>\n<!-- /wp:html -->')
    elif b.startswith('>'):
        ls = [l[1:].strip() for l in b.split('\n') if l[1:].strip()]
        inner = '\n\n'.join(para(l) for l in ls)
        out.append(f'<!-- wp:quote -->\n<blockquote class="wp-block-quote">{inner}</blockquote>\n<!-- /wp:quote -->')
    elif b.startswith('- '):
        li = '\n'.join(f'<!-- wp:list-item -->\n<li>{inline(l[2:])}</li>\n<!-- /wp:list-item -->' for l in b.split('\n'))
        out.append(f'<!-- wp:list -->\n<ul class="wp-block-list">{li}</ul>\n<!-- /wp:list -->')
    elif b.startswith('$$') and b.endswith('$$') and b.count('$$') == 2:
        out.append(para(b, center=True))
    else:
        if '\n' in b:
            sys.exit(f'Paragraph spans several lines (join them or add a blank line): {b[:80]}')
        out.append(para(b))

content = '\n\n'.join(out)
json.dump({'title': meta.get('title', ''), 'excerpt': meta.get('excerpt', ''), 'content': content},
          open(os.path.join(out_dir, 'post.json'), 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(out_dir, 'post_content.html'), 'w', encoding='utf-8').write(content)
body = '\n'.join(lines)
maths = [a or b for a, b in re.findall(r'\$\$(.+?)\$\$|\$([^$]+?)\$', body)]
json.dump(maths, open(os.path.join(out_dir, 'maths.json'), 'w'))
# chunks (<= ~11k chars, split at block boundaries) + checksums for the browser transfer
chunks, cur = [], ''
for i, blk in enumerate(out):
    piece = ('\n\n' if i else '') + blk
    if cur and len(cur) + len(piece) > 11000:
        chunks.append(cur); cur = piece
    else:
        cur += piece
chunks.append(cur)
assert ''.join(chunks) == content
for f in os.listdir(out_dir):
    if f.startswith('chunk'): os.remove(os.path.join(out_dir, f))
for i, ch in enumerate(chunks):
    open(os.path.join(out_dir, f'chunk{i}.js'), 'w', encoding='utf-8').write(json.dumps(ch, ensure_ascii=False))
cs = lambda s: (len(s), sum(ord(c) for c in s))
print('title:', meta.get('title'))
print(f'{len(out)} blocks, {len(maths)} math snippets')
print('chunks (len, codepoint-sum):', [cs(c) for c in chunks])
print('TOTAL (len, codepoint-sum):', cs(content))
