# claude-skills

Custom skills for Claude, kept here for safekeeping and version history.

| Skill | What it does |
|---|---|
| [`sidspark-blog-post`](sidspark-blog-post/SKILL.md) | Writes a physics/maths article for [Sidspark](https://sidspark.site) and saves it as a ready-to-publish WordPress draft: house style, SVG figures, MathJax, Gutenberg markup via the REST API, category and tags. |

Each skill is a folder: a `SKILL.md` plus the scripts (`scripts/`) and reference notes (`reference/`) it calls. Install the whole folder, not just `SKILL.md`:

- **Claude Code:** copy the folder to `~/.claude/skills/`, e.g. `cp -R sidspark-blog-post ~/.claude/skills/`.
- **Claude apps (claude.ai / desktop):** zip the folder (`zip -r sidspark-blog-post.zip sidspark-blog-post`) and upload the zip as a skill.
