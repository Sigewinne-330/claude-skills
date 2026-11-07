---
name: "sidspark-blog-post"
description: "为用户的WordPress博客Sidspark（sidspark.site）写物理/数学文章并存成只差点发布的草稿：沿用博客英文风格、自绘SVG图、MathJax公式、REST写入并打好分类标签。用户说写博客、把题写成文章、往Sidspark发文或改博文时都用。"
---

# Sidspark 博客文章

把一个物理/数学话题变成 sidspark.site 上**一篇写完、配好图、打好标签、只差用户点"发布"的草稿**。

## 本 skill 的文件

| 文件 | 内容 | 什么时候读 |
|---|---|---|
| `scripts/build_post.py` | post.txt → Gutenberg 区块 + 分段文件与校验值 | 直接运行，不用读 |
| `scripts/svgkit.py` | 画图小工具（开头有用法示例） | 写 `make_figs.py` 前看一眼文件开头的 docstring |
| `scripts/texcheck.js` | 用 MathJax 编译每条公式，报错 | 直接运行，不用读 |
| `reference/style.md` | Sidspark 写作风格 | 第 2 步定结构前 |
| `reference/wordpress.md` | 通过 Claude in Chrome 推送与验证 | 第 7 步推送前 |

下文 `$SKILL` 指本 skill 文件夹（SKILL.md 所在目录）的绝对路径；在 shell 里先 `SKILL=<该路径>`。
脚本已在实际发文中验证过，直接调用，**不要把它们复制或改写到别处**。发现 bug 时告诉用户，以便修改仓库里的脚本。

## 流程总览

建一个任务清单，按顺序做：

1. **吃透题目，先把物理算对**（写之前验证）
2. **定结构**（`reference/style.md`）
3. **画图**（`svgkit.py`）
4. **写源稿** `post.txt`（格式见下）
5. **构建 + 检查公式**（`build_post.py`、`texcheck.js`）
6. **通读润色一遍**
7. **推送草稿并验证**（`reference/wordpress.md`）
8. **简短汇报**

工作目录建议 `~/blog/<slug>/`，内含 `figs/`、`out/`、`post.txt`、`make_figs.py`、`check.py`。所有输出都写在工作目录里，不写进 skill 文件夹。

## 1. 先把物理算对

博客读者会认真推导，一个符号错误就毁掉整篇文章，所以动笔前先算清楚：
- 自己独立推导，不照抄题目附带的或网上的解答（那份解答可能有疏漏，而且是别人的作品）。
- **写一个小数值检验**（`check.py`）：比如对完整运动方程做 RK4 积分量周期、把答案代回原题的受力方程、数值验证代数化简。公式和数值吻合再往下写。
- 检查极限情形（质量→∞/→0、无摩擦、小角度）。这既是验证，也是文章里的好素材。

## 2. 定结构

先读 `reference/style.md`。要点：英文正文、第一人称、编号 H2 小节、关键结论放引用框、展示公式带 `\tag{n}`、有"极限检验"一节、结尾用 "Closing: …"。
用户给的素材和说明要**有选择地用**——挑能支撑论证的，其余舍掉，不要原样搬进稿件，也不要把所有细节塞进一句话。题目出处（夏校、教材、网上）用自己的话转述并在正文中注明来源。
写到用户本人的经历和能力时，只写他真做过的；拿不准就问，或写得中性些。

## 3. 画图

写一个 `make_figs.py`，开头 `import sys; sys.path.insert(0, "<$SKILL 的绝对路径>/scripts"); from svgkit import *`，每张图输出一个 `figs/<name>.svg`。图要简洁：浅米色填充表示物体，深色描边，红/蓝箭头表示运动量，灰色小字做注释。
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
python3 "$SKILL/scripts/build_post.py" post.txt figs out
npm i mathjax-full@3 --silent            # 每个工作目录装一次
NODE_PATH=$PWD/node_modules node "$SKILL/scripts/texcheck.js" out/maths.json
```

`build_post.py` 输出：`out/post.json`（标题/摘要/正文）、`out/post_content.html`（区块代码）、`out/maths.json`、`out/chunkN.js` 分段文件，并打印每段的 (长度, 码点和) 校验值——推送时要用。
`texcheck.js` 必须是 `errors 0` 才能继续。

## 6. 通读润色

推送前把 `post.txt` 从头到尾读一遍：逻辑是否连贯、有无重复、句子是否自然、图号和公式编号是否按出现顺序、正文引用的 "(n)" 是否对得上。改完重新构建。

## 7. 推送与验证

先读 `reference/wordpress.md`，里面有可直接用的 JS 片段和这个站点的坑。要点：
- 先加载 Claude in Chrome 工具；这个站的页面永远到不了 document_idle，截图/读页面/上传文件都会超时，**全部用 `javascript_tool`**。
- 内容按 `chunkN.js` 分段原样贴进 `window.__parts[N]`，每段核对长度和码点和，再拼接核对总值。
- 用 REST API 建草稿（`status: 'draft'`），分类按名称找（物理类用 Physics Club），标签先按名称复用、没有再新建。
- 四项验证全部通过：存储内容与发送内容一致且公式未被 texturize 改动；编辑器内无无效区块；预览页公式数 = 构建时的数量、无 MathJax 错误、图都有宽度；最后把标签页停在文章编辑页。
- **永远不要替用户发布**；改已发布的文章前先问。

## 8. 汇报

用中文简短说明：草稿标题和 ID、分类和标签、文章结构一两句、做了哪些验证、需要用户留意的地方（比如替他写了哪些关于他本人的话）。不要复述全文。
