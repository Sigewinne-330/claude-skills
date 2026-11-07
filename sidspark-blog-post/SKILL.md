---
name: "sidspark-blog-post"
description: "为用户的WordPress博客Sidspark（sidspark.site）写物理/数学文章并存成只差点发布的草稿：沿用博客英文风格、自绘SVG图、MathJax公式、REST写入并打好分类标签。用户说写博客、把题写成文章、往Sidspark发文或改博文时都用。"
---

# Sidspark 博客文章

把一个物理/数学话题变成 sidspark.site 上**一篇写完、配好图、打好标签、只差用户点"发布"的草稿**。
所需的三个脚本、写作风格和 WordPress 操作细节都在本文末尾的附录里。

## 流程总览

建一个任务清单，按顺序做：

0. **准备工具**：若 `~/blog/tools/` 下没有 `build_post.py`、`svgkit.py`、`texcheck.js`，用 Write 把附录 C 的三个文件原样写进去
1. **吃透题目，先把物理算对**（写之前验证）
2. **定结构**（附录 A）
3. **画图**（`svgkit.py`）
4. **写源稿** `post.txt`（格式见下）
5. **构建 + 检查公式**（`build_post.py`、`texcheck.js`）
6. **通读润色一遍**
7. **推送草稿并验证**（附录 B）
8. **简短汇报**

工作目录建议 `~/blog/<slug>/`，内含 `figs/`、`out/`、`post.txt`、`make_figs.py`、`check.py`。

## 1. 先把物理算对

博客读者会认真推导，一个符号错误就毁掉整篇文章，所以动笔前先算清楚：
- 自己独立推导，不照抄题目附带的或网上的解答（那份解答可能有疏漏，而且是别人的作品）。
- **写一个小数值检验**（`check.py`）：比如对完整运动方程做 RK4 积分量周期、把答案代回原题的受力方程、数值验证代数化简。公式和数值吻合再往下写。
- 检查极限情形（质量→∞/→0、无摩擦、小角度）。这既是验证，也是文章里的好素材。

## 2. 定结构

按附录 A 的风格：英文正文、第一人称、编号 H2 小节、关键结论放引用框、展示公式带 `\tag{n}`、有"极限检验"一节、结尾用 "Closing: …"。
用户给的素材和说明要**有选择地用**——挑能支撑论证的，其余舍掉，不要原样搬进稿件，也不要把所有细节塞进一句话。题目出处（夏校、教材、网上）用自己的话转述并在正文中注明来源。
写到用户本人的经历和能力时，只写他真做过的；拿不准就问，或写得中性些。

## 3. 画图

用 `~/blog/tools/svgkit.py`（文件开头有用法示例）写一个 `make_figs.py`，每张图输出一个 `figs/<name>.svg`。图要简洁：浅米色填充表示物体，深色描边，红/蓝箭头表示运动量，灰色小字做注释。
每张图都用 `rsvg-convert -w 1000 -b white figs/x.svg -o figs/x.png` 渲染出来，**用 Read 看一眼**，把文字压线、标签出界之类的问题改掉——这一步每次都能发现问题。
svgkit 内置的规则（不要绕开）：不用 `<style>`；marker id 按图加前缀以免全页冲突；SVG 文字里不能出现 `$`。

## 4. 源稿格式（post.txt）

```
TITLE: Reduced Mass: A Ball in a Sliding Bowl, ...
EXCERPT: One or two sentences, no maths.

Intro paragraph, one line per paragraph, with $inline$ maths, **bold** and *italic*.

[[FIG setup|Figure 1. Caption sentence or two.]]

## 1. Numbered section heading

$$K=\tfrac12\mu\dot r^2 \tag{3}$$

> **Claim.** A statement in a quote block.
> $$ display maths inside the quote $$

- list item
- list item

### 5.1 Sub-heading

<!-- wp:table -->
<figure class="wp-block-table"><table>…</table></figure>
<!-- /wp:table -->
```

区块之间空一行；一段正文必须写在一行里（脚本发现多行段落会报错停止）。以 `<!-- wp:` 开头的区块原样保留，表格就这样写。

**WordPress 的 wptexturize 会改写正文里的某些字符，所以公式里避开：**撇号 prime（用 `^{\prime}`）、`--`、`...`（用 `\dots`）、"数字x数字"（如 `2x3`）、双引号。`<` `>` 由脚本自动转成 `\lt` `\gt`。

## 5. 构建与公式检查

```bash
python3 ~/blog/tools/build_post.py post.txt figs out
npm i mathjax-full@3 --silent            # 每个工作目录装一次
NODE_PATH=$PWD/node_modules node ~/blog/tools/texcheck.js out/maths.json
```

`build_post.py` 输出：`out/post.json`（标题/摘要/正文）、`out/post_content.html`（区块代码）、`out/maths.json`、`out/chunkN.js` 分段文件，并打印每段的 (长度, 码点和) 校验值——推送时要用。
`texcheck.js` 必须是 `errors 0` 才能继续。

## 6. 通读润色

推送前把 `post.txt` 从头到尾读一遍：逻辑是否连贯、有无重复、句子是否自然、图号和公式编号是否按出现顺序、正文引用的 "(n)" 是否对得上。改完重新构建。

## 7. 推送与验证

先读附录 B，里面有可直接用的 JS 片段和这个站点的坑。要点：
- 先加载 Claude in Chrome 工具；这个站的页面永远到不了 document_idle，截图/读页面/上传文件都会超时，**全部用 `javascript_tool`**。
- 内容按 `chunkN.js` 分段原样贴进 `window.__parts[N]`，每段核对长度和码点和，再拼接核对总值。
- 用 REST API 建草稿（`status: 'draft'`），分类按名称找（物理类用 Physics Club），标签先按名称复用、没有再新建。
- 四项验证全部通过：存储内容与发送内容一致且公式未被 texturize 改动；编辑器内无无效区块；预览页公式数 = 构建时的数量、无 MathJax 错误、图都有宽度；最后把标签页停在文章编辑页。
- **永远不要替用户发布**；改已发布的文章前先问。

## 8. 汇报

用中文简短说明：草稿标题和 ID、分类和标签、文章结构一两句、做了哪些验证、需要用户留意的地方（比如替他写了哪些关于他本人的话）。不要复述全文。

---

## 附录 A：Sidspark 写作风格

Distilled from the physics posts on sidspark.site (pole/vibration isolation, Bertrand's theorem,
shell theorem, Playing Pool with Pi series, reduced mass). Refresh it by skimming one or two recent
posts (Appendix B, "Reading existing posts") if the blog may have drifted.

### Voice
- Body in **English**, first person ("I"), conversational but precise. Dry humour is welcome
  ("it has been living in my head ever since", "a caveat I refuse to bury").
- Honest about limits. The author is an IB student who self-studies physics; do not claim
  mastery he does not have (e.g. Lagrangian mechanics is new to him: say "I am still fairly new to
  Lagrangians, so I'll go slowly"). Only state things he actually did (experiments, checks, where he met
  a problem). If unsure whether he did something, ask or phrase it neutrally.
- Explain *why* each step is allowed, not just what it is ("Why one degree of freedom is allowed.").
- Short paragraphs; one idea each. Don't cram every detail of the brief into one sentence:
  pick what serves the argument and drop the rest.

### Structure
- Title: punchy, often "Topic: Hook" or a series form
  ("How Differential Equations Describe the Physics World – Why …", "Playing Pool with Pi – Part 3 – …").
- Intro with no heading: a concrete hook (problem, folk claim, story), the question, and what the post
  will show. Usually 3–6 paragraphs and the first figure.
- Numbered H2 sections "1. …", "2. …" (a "0." section is fine for definitions). H3 "5.1 …" for sub-cases.
- A limit/sanity-check section is a signature move ("Breaking the answer on purpose": M→∞, M→0,
  frictionless case, dimension check).
- If the problem asks "can method X do it?", answer it explicitly in its own section.
- Final section unnumbered: "Closing: …" or "Closing, with …" — what the trick needs / where it fails,
  plus one surprising connection to something bigger. No summary of every section.
- Typical length 3,000–4,500 words; 10–15 numbered display equations; 2–5 figures.

### Formatting conventions
- Display maths: own centred paragraph, `$$ … \tag{n} $$`; refer to it as "(n)" in text.
  Un-numbered displays for intermediate steps are fine.
- Inline maths `$…$`. Vectors `\mathbf r`. Fractions in inline maths: `\tfrac`.
- Bold lead-ins start paragraphs that make one specific point: `**Heavy track, $M\to\infty$.** …`
- Key statements (Claim / The rule / Theorem 1) go in a quote block with a bold label.
- Proofs end with `\qquad\blacksquare` inside the last display.
- Tables only for numeric results. Write them in post.txt as a raw block (no blank lines inside):
  `<!-- wp:table -->` / `<figure class="wp-block-table"><table><thead>…</thead><tbody>…</tbody></table></figure>` / `<!-- /wp:table -->`.
- Figures: "Figure n." caption in bold followed by one or two sentences; numbered in order of
  appearance.

### Sources and other people's material
- Paraphrase problems from textbooks, summer schools or the web in your own words and credit the
  source in prose ("the problem from HKU summer school, in my own words"). Do not paste their text
  or reproduce someone else's worked solution; derive it yourself.
- Never use someone else's figures; redraw everything as SVG.

### Taxonomy
- Category for physics/maths posts: **Physics Club** (id 13 at time of writing; confirm by name).
  Other categories exist (Creative Writing Club, Feelings) for non-physics writing.
- Tags: 4–7 topical tags in Title Case (e.g. Classical Mechanics, Reduced Mass, Simple Harmonic
  Motion, Lagrangian Mechanics). Reuse existing tags by exact name before creating new ones.
- Excerpt: one or two sentences, no maths.

---

## 附录 B：通过 Claude in Chrome 推送到 sidspark.site

### Contents
1. Browser quirks on this site (read first)
2. Reading existing posts
3. Transferring the content (chunks + checksums)
4. Creating the draft
5. Verification
6. Updating an existing post

### 1. Browser quirks on this site

- Pages on sidspark.site (front end *and* wp-admin) never reach `document_idle`, so
  `computer screenshot`, `get_page_text`, `find`, `read_page` and `file_upload` time out.
  **`javascript_tool` works** — do everything with it. `navigate` works too.
- `javascript_tool` output is truncated at roughly 1,000 characters, and a result containing
  URL query strings or cookie-like data is replaced by `[BLOCKED: Cookie/query string data]`.
  Return only short summaries (counts, ids, lengths, booleans); when reading text, strip
  `& = ?` first and slice ≤ 900 characters.
- `browser_batch` cannot act on a page after navigating in the same batch; navigate on its own.
- The admin session is already logged in. On any wp-admin page, `wpApiSettings.nonce` is the REST
  nonce (`X-WP-Nonce` header). The user is an administrator with `unfiltered_html`, so inline SVG
  in Custom HTML blocks is saved untouched.
- Start with `tabs_context_mcp`, then open a new tab (`tabs_create_mcp`) unless the user points to an
  existing one. Leave the final tab on the post's edit page so the user can press Publish.

### 2. Reading existing posts

Public REST works from any sidspark.site page:

```js
const posts = await (await fetch('/wp-json/wp/v2/posts?per_page=10&_fields=id,title,date,categories,tags')).json();
posts.map(p => p.id + ' | ' + p.date.slice(0,10) + ' | ' + p.title.rendered).join('\n')
```

Tags/categories: `/wp-json/wp/v2/tags?per_page=100&_fields=id,name,count` (same for `categories`).
For a post's text: fetch `/wp-json/wp/v2/posts/<id>?_fields=content`, put it in a `div`,
take `innerText.replace(/[&=?]/g,' ')`, and read it in ≤ 900-character slices.
Raw block markup (context=edit) needs the nonce, so do that from a wp-admin page.

### 3. Transferring the content

There is no way to send a file into the page, so the content goes in as JS string literals.
`build_post.py` writes `out/chunk0.js`, `chunk1.js`, … (each a JSON string ≤ ~11k chars) and prints
`(length, codepoint-sum)` for each chunk and for the total.

For each chunk N, `cat out/chunkN.js` and paste its contents **verbatim** as the right-hand side:

```js
window.__parts = window.__parts || [];
window.__parts[N] = <contents of chunkN.js>;
const p = window.__parts[N]; let s = 0; for (const ch of p) s += ch.codePointAt(0); p.length + ' ' + s
```

The printed pair must equal the build output for that chunk; if not, resend that chunk.
After the last chunk:

```js
window.__content = window.__parts.join(''); let s = 0; for (const ch of window.__content) s += ch.codePointAt(0);
window.__content.length + ' ' + s
```

must equal the TOTAL line. (`window.__parts` lives only until the tab navigates, so do the transfer
and the REST call on the same page without navigating in between.)

### 4. Creating the draft

Run on a wp-admin page (e.g. `https://sidspark.site/wp-admin/edit.php`). Fill in title, excerpt,
tag names and the category name.

```js
const H = {'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type': 'application/json'};
const tagNames = ['Classical Mechanics', 'Reduced Mass'];          // edit
const catName = 'Physics Club';                                     // edit
const cats = await (await fetch('/wp-json/wp/v2/categories?per_page=100&_fields=id,name', {headers: H})).json();
const cat = cats.find(c => c.name === catName);
const tagIds = [];
for (const n of tagNames) {
  const ex = await (await fetch('/wp-json/wp/v2/tags?search=' + encodeURIComponent(n) + '&_fields=id,name', {headers: H})).json();
  const hit = ex.find(t => t.name.toLowerCase() === n.toLowerCase());
  tagIds.push(hit ? hit.id : (await (await fetch('/wp-json/wp/v2/tags', {method: 'POST', headers: H, body: JSON.stringify({name: n})})).json()).id);
}
const post = await (await fetch('/wp-json/wp/v2/posts', {method: 'POST', headers: H, body: JSON.stringify({
  title: 'TITLE', excerpt: 'EXCERPT', content: window.__content,
  status: 'draft', categories: [cat.id], tags: tagIds
})})).json();
JSON.stringify({id: post.id, status: post.status, tags: post.tags, cats: post.categories, err: post.message})
```

Always `status: 'draft'`. Publishing is the user's click, never ours.

### 5. Verification (all four, every time)

a) Stored content is byte-identical, and wptexturize did not touch any maths:

```js
const p = await (await fetch('/wp-json/wp/v2/posts/ID?context=edit&_fields=content', {headers: {'X-WP-Nonce': wpApiSettings.nonce}})).json();
const strip = s => s.replace(/<svg[\s\S]*?<\/svg>/g, '');
const re = /\$\$[\s\S]+?\$\$|\$[^$]+?\$/g;
const a = strip(p.content.raw).match(re) || [], b = strip(p.content.rendered).match(re) || [];
const d = a.filter((x, i) => x !== b[i]);
[p.content.raw === window.__content, a.length, b.length, 'diffs:' + d.length, d.slice(0, 2).join(' || ')].join(' | ')
```

b) Block validity in the editor — navigate to `https://sidspark.site/wp-admin/post.php?post=ID&action=edit`, then:

```js
await new Promise(r => setTimeout(r, 4000));
const flat = []; const walk = bs => bs.forEach(b => { flat.push(b); walk(b.innerBlocks); });
walk(wp.data.select('core/block-editor').getBlocks());
const ed = wp.data.select('core/editor');
JSON.stringify({blocks: flat.length, invalid: flat.filter(b => !b.isValid).map(b => b.name),
  status: ed.getEditedPostAttribute('status'), tags: ed.getEditedPostAttribute('tags'), dirty: ed.isEditedPostDirty()})
```

c) Front-end preview — navigate to `https://sidspark.site/?p=ID&preview=true`, then:

```js
await new Promise(r => setTimeout(r, 6000));
JSON.stringify({mj: document.querySelectorAll('mjx-container').length,
  errs: document.querySelectorAll('mjx-merror,[data-mjx-error]').length,
  figs: [...document.querySelectorAll('figure.sidspark-fig svg')].map(s => Math.round(s.getBoundingClientRect().width)),
  leftover: (document.querySelector('.entry-content,article') || document.body).innerText.match(/\$[^$]{1,40}\$/g)})
```

`mj` must equal the number of maths snippets from the build, `errs` 0, `leftover` null, every
figure width > 0.

d) Navigate back to the edit page and leave the tab there.

### 6. Updating an existing post

Same transfer, then `POST /wp-json/wp/v2/posts/<id>` with only the fields that change. If the
post is already published, say so and ask before overwriting it — a live post changes instantly.

---

## 附录 C：工具脚本（原样写入 `~/blog/tools/`）

这三个文件已在实际发文中验证过，照原样写出，不要改写逻辑；发现 bug 时再修，并告诉用户以便更新这个 skill。

### C1. `build_post.py`

```python
#!/usr/bin/env python3
"""post.txt (light markdown) -> Gutenberg block markup + chunks for browser transfer.
Usage: python3 ~/blog/tools/build_post.py post.txt figs/ out/
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
```

### C2. `svgkit.py`

```python
"""Tiny helper kit for Sidspark blog figures (inline SVG inside a WordPress Custom HTML block).

Usage in a per-post figure script:

    import os, sys; sys.path.insert(0, os.path.expanduser("~/blog/tools"))
    from svgkit import *
    def fig_setup():
        b = [defs(marker("s1r", RED))]          # marker ids MUST be unique across the whole post
        b.append(floor(40, 600, 300))
        b.append(arrow(104, 205, 58, 205, RED, "s1r"))
        b.append(text(80, 192, "recoils", 13, RED, italic=False, family=SANS))
        b.append(text(170, 268, sub("m", "1"), 18))   # italic m with upright subscript 1
        return svg(640, 330, "".join(b), "Alt text describing the figure")
    save("figs/setup.svg", fig_setup())

Then render to check:  rsvg-convert -w 1000 -b white figs/setup.svg -o figs/setup.png  (and Read the PNG).

Rules baked in (why they matter):
- No <style> element: inline SVG CSS would leak into the whole blog page.
- Marker ids are page-global once inlined: prefix them per figure (s1r, s2b, ...).
- Never put "$" or "\\(" in <text>: Simple MathJax would try to typeset it.
- Fonts are set per <text> (Georgia italic for symbols, Helvetica for annotations), and
  subscripts use dy shifts rather than baseline-shift so every renderer agrees.
"""
import math

INK, BLUE, RED, GREY, FILL, WHITE = "#1f2328", "#2563a8", "#c2410c", "#8a8f98", "#efe9dc", "#ffffff"
SERIF = "Georgia, serif"
SANS = "Helvetica, Arial, sans-serif"


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def marker(mid, color):
    """Arrowhead; use with marker-end / marker-start (auto-start-reverse flips it for the start)."""
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="{color}"/></marker>')


def line(x1, y1, x2, y2, color=INK, w=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"{d}/>'


def arrow(x1, y1, x2, y2, color, mid, w=2.2, dash=None, both=False):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s = f' marker-start="url(#{mid})"' if both else ''
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
            f'stroke-width="{w}"{d}{s} marker-end="url(#{mid})"/>')


def circle(cx, cy, r, fill=WHITE, stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'


def dot(cx, cy, r=3, color=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}"/>'


def path(d, fill="none", stroke=INK, w=2, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{ds}/>'


def rect_rot(cx, cy, w, h, deg, fill=WHITE, stroke=INK, sw=2):
    """Rectangle centred at (cx, cy) rotated by deg (e.g. a block on an incline)."""
    return (f'<rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" transform="rotate({deg:.2f} {cx:.1f} {cy:.1f})"/>')


def text(x, y, s, size=17, color=INK, italic=True, anchor="middle", family=SERIF, weight="normal"):
    st = ' font-style="italic"' if italic else ''
    wt = f' font-weight="{weight}"' if weight != "normal" else ''
    an = '' if anchor == "middle" else f' text-anchor="{anchor}"'
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{family}" font-size="{size}" fill="{color}"'
            f'{st}{wt}{an}>{s}</text>')


def sub(main, s, size=12):
    """main followed by an upright subscript (dy shift, then restore)."""
    return f'{main}<tspan dy="4" font-size="{size}" font-style="normal">{s}</tspan><tspan dy="-4"></tspan>'


def bold(s):
    """Bold glyph inside a text() string, e.g. vectors: text(x, y, sub(bold('r'), '1'))."""
    return f'<tspan font-weight="bold">{s}</tspan>'


def angle_arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=1.3):
    """Arc of radius r around (cx, cy) from screen angle a0 to a1 (degrees, y axis pointing DOWN,
    0 = +x, 90 = straight down). Sweep goes in the direction of increasing angle."""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    return f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'


def floor(x0, x1, y, step=18):
    """Ground line with hatching below (one compact <path> instead of dozens of lines)."""
    d = "".join(f"M{x:g},{y:g}l-11,12" for x in range(int(x0) + 10, int(x1) + 1, step))
    return line(x0, y, x1, y, INK, 1.8) + f'<path d="{d}" stroke="{GREY}" stroke-width="1.2"/>'


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}" '
            f'style="max-width:100%;height:auto;display:block;margin:0 auto" text-anchor="middle">{body}</svg>')


def save(fname, content):
    assert "<style" not in content, "no <style> in inline SVG"
    assert "$" not in content, "no $ in SVG text (MathJax would grab it)"
    with open(fname, "w", encoding="utf-8") as fh:
        fh.write(content)
```

### C3. `texcheck.js`

```js
// Compile every LaTeX snippet with MathJax 3 and report errors (undefined macros, missing braces...).
// Setup once in the working dir:  npm i mathjax-full@3 --silent
// Run:  NODE_PATH=$PWD/node_modules node ~/blog/tools/texcheck.js out/maths.json
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
```