"""Render terms-of-use.html and privacy-policy.html from legal-source/*.md"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "legal-source"


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    return text


def md_to_html(md: str) -> str:
    lines = md.strip().split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            out.append(render_table(table_lines))
            continue

        if stripped.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].strip().startswith("- "):
                out.append(f"<li>{inline_md(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("</ul>")
            continue

        if stripped.startswith("## "):
            out.append(f"<h2>{inline_md(stripped[3:])}</h2>")
            i += 1
            continue

        if stripped.startswith("# "):
            out.append(f"<h1>{inline_md(stripped[2:])}</h1>")
            i += 1
            if i < len(lines):
                next_line = lines[i].strip()
                if next_line.lower().startswith("**last updated") or next_line.lower().startswith(
                    "**dernière mise à jour"
                ):
                    out.append(f'<p class="last-updated">{inline_md(next_line)}</p>')
                    i += 1
            continue

        para_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() == "" or nxt.strip().startswith("#") or nxt.strip().startswith("- ") or nxt.strip().startswith("|"):
                break
            para_lines.append(nxt.rstrip())
            i += 1
        if len(para_lines) > 1:
            out.append(
                "<p>"
                + "<br>\n        ".join(inline_md(part.strip()) for part in para_lines)
                + "</p>"
            )
        else:
            out.append(f"<p>{inline_md(para_lines[0].strip())}</p>")

    return "\n    ".join(out)


def render_table(table_lines: list[str]) -> str:
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return ""
    header = rows[0]
    body = rows[2:] if re.match(r"^[\-\|: ]+$", "|".join(rows[1])) else rows[1:]
    html_parts = ['<table>', "<thead><tr>"]
    for cell in header:
        html_parts.append(f"<th>{inline_md(cell)}</th>")
    html_parts.append("</tr></thead><tbody>")
    for row in body:
        html_parts.append("<tr>")
        for cell in row:
            html_parts.append(f"<td>{inline_md(cell)}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody></table>")
    return "".join(html_parts)


def wrap_page(title: str, en_md: str, fr_md: str) -> str:
    en_html = md_to_html(en_md)
    fr_html = md_to_html(fr_md)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

  <header class="site-header">
    <div class="container">
      <a href="index.html" class="brand">Soma AI</a>
    </div>
  </header>

  <main class="container page legal-page">
    <a href="index.html" class="back-link">← Back</a>
    <p class="lang-nav"><a href="#en">English</a><span class="sep">·</span><a href="#fr">Français</a></p>

    <section id="en" lang="en">
    {en_html}
    </section>

    <section id="fr" lang="fr">
    {fr_html}
    </section>

  </main>

  <footer class="site-footer">
    <div class="container">
      <p>&copy; <span id="year">2026</span> Nathan Deleau and Mateo Goury. All rights reserved.</p>
      <p class="footer-links">
        <a href="privacy-policy.html">Privacy Policy</a>
        <span class="sep">·</span>
        <a href="terms-of-use.html">Terms of Use</a>
      </p>
    </div>
  </footer>

</body>
</html>
"""


def main() -> None:
    terms_en = (SOURCE / "terms-of-use.en.md").read_text(encoding="utf-8")
    terms_fr = (SOURCE / "terms-of-use.fr.md").read_text(encoding="utf-8")
    privacy_en = (SOURCE / "privacy-policy.en.md").read_text(encoding="utf-8")
    privacy_fr = (SOURCE / "privacy-policy.fr.md").read_text(encoding="utf-8")

    (ROOT / "terms-of-use.html").write_text(
        wrap_page("Terms of Use — Soma AI", terms_en, terms_fr),
        encoding="utf-8",
    )
    (ROOT / "privacy-policy.html").write_text(
        wrap_page("Privacy Policy — Soma AI", privacy_en, privacy_fr),
        encoding="utf-8",
    )
    print("Rendered terms-of-use.html and privacy-policy.html")


if __name__ == "__main__":
    main()
