# agent-skills

Custom skills for AI coding agents (Claude and Antigravity), kept here for safekeeping and version history.

| Skill | Platform | What it does |
|---|---|---|
| [`claude/sidspark-blog-post`](claude/sidspark-blog-post/SKILL.md) | Claude (Claude in Chrome) | Writes a physics/maths article for [Sidspark](https://sidspark.site) and saves it as a ready-to-publish WordPress draft using Claude in Chrome (`javascript_tool`), house style, SVG figures, MathJax, and REST API. |
| [`antigravity/sidspark-blog-post`](antigravity/sidspark-blog-post/SKILL.md) | Antigravity (`chrome-devtools` MCP) | Adapted version for Antigravity using `chrome-devtools` MCP (`evaluate_script`, `navigate_page`, `list_pages`), supporting local fallback checks and optional private (`status: 'private'`) test publishing. |

Each skill is a folder: a `SKILL.md` plus the scripts (`scripts/`) and reference notes (`reference/`) it calls. Install the whole `sidspark-blog-post` folder, not just `SKILL.md`:

- **Claude Code:** copy the Claude folder to `~/.claude/skills/`, e.g. `cp -R claude/sidspark-blog-post ~/.claude/skills/`.
- **Claude apps (claude.ai / desktop):** zip the folder (`cd claude && zip -r sidspark-blog-post.zip sidspark-blog-post`) and upload the zip as a skill.
- **Antigravity:** copy the Antigravity folder to `~/.gemini/config/skills/`, e.g. `cp -R antigravity/sidspark-blog-post ~/.gemini/config/skills/`.
