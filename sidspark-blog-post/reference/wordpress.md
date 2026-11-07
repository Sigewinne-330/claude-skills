# Pushing to sidspark.site through Claude in Chrome

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

