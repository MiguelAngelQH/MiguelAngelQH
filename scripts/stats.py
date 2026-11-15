"""Genera las tarjetas de estadisticas (stats, lenguajes y actividad) con estilo lofi.

Uso: GITHUB_TOKEN=... python scripts/stats.py <usuario> <carpeta_salida>
"""
import json
import os
import sys
import urllib.request
from datetime import date

USER = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

BG1, BG2, LINE = "#111a2e", "#1a2744", "#2a3b60"
PURPLE, LAV, PINK, ROSE = "#4f78d1", "#a8c8f5", "#f2a7c3", "#e68aa8"
AMBER, CREAM, MUTED = "#f6c177", "#f4e6d8", "#8399c2"
FONT = "'JetBrains Mono','Cascadia Code','SF Mono',Menlo,Consolas,'Courier New',monospace"
PALETTE = [PINK, AMBER, LAV, ROSE, PURPLE, CREAM, "#9ccfd8", "#eb6f92"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes { stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}"""


def gql():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


ICONS = {
    "commit": '<circle cx="12" cy="12" r="4"/><line x1="1.05" y1="12" x2="7" y2="12"/><line x1="17.01" y1="12" x2="22.96" y2="12"/>',
    "pr": '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><line x1="6" y1="9" x2="6" y2="21"/>',
    "issue": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "repo": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
}


def icon(name, x, y, size, color):
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def frame(w, h, title, body, extra_css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">
<defs>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 0.92  0 0 0 0 0.86  0 0 0 0.12 0"/></filter>
<radialGradient id="gl" cx="1" cy="0" r="1"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".3"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<linearGradient id="pg" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>
<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PINK}" stop-opacity=".45"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath>
</defs>
<style>text{{font-family:{FONT}}}
.in{{opacity:0;animation:in .8s ease-out forwards}}@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
{extra_css}</style>
<g clip-path="url(#c)">
<rect width="{w}" height="{h}" fill="{BG1}"/><rect width="{w}" height="{h}" fill="url(#gl)"/>
<text x="24" y="38" fill="{PINK}" font-size="16" font-weight="700">{title}</text>
{body}
<rect width="{w}" height="{h}" filter="url(#grain)"/>
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="none" stroke="{LINE}" stroke-width="1.5"/>
</svg>"""


def main():
    u = gql()
    cc = u["contributionsCollection"]
    repos = u["repositories"]
    stars = sum(r["stargazerCount"] for r in repos["nodes"])

    # -------- stats
    items = [
        ("commit", "commits (último año)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("pr", "pull requests", cc["totalPullRequestContributions"]),
        ("issue", "issues", cc["totalIssueContributions"]),
        ("repo", "repos públicos", repos["totalCount"]),
        ("star", "estrellas", stars),
        ("users", "seguidores", u["followers"]["totalCount"]),
    ]
    body = []
    for i, (ic, label, val) in enumerate(items):
        y = 70 + i * 30
        body.append(f'<g class="in" style="animation-delay:{i * .15:.2f}s">{icon(ic, 24, y - 15, 18, AMBER)}'
                    f'<text x="54" y="{y}" fill="{LAV}" font-size="14">{label}</text>'
                    f'<text x="400" y="{y}" fill="{CREAM}" font-size="15" font-weight="700" text-anchor="end">{val}</text></g>')
    total = cc["contributionCalendar"]["totalContributions"]
    body.append(f'<text x="24" y="{70 + 6 * 30 + 4}" fill="{MUTED}" font-size="12">{total} contribuciones en el último año</text>')
    with open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(frame(424, 270, "stats de github", "\n".join(body)))

    # -------- lenguajes
    sizes = {}
    for r in repos["nodes"]:
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:6]
    tot = sum(v for _, v in top) or 1
    body, css = [], []
    x = 24
    for i, (name, v) in enumerate(top):
        wpx = 376 * v / tot
        body.append(f'<rect class="seg" x="{x:.1f}" y="58" width="{max(wpx - 2, 1):.1f}" height="10" rx="3" fill="{PALETTE[i]}" '
                    f'style="animation-delay:{i * .12:.2f}s"/>')
        x += wpx
    for i, (name, v) in enumerate(top):
        col, row = i % 2, i // 2
        bx, by = 24 + col * 196, 104 + row * 34
        body.append(f'<g class="in" style="animation-delay:{.5 + i * .12:.2f}s"><circle cx="{bx + 6}" cy="{by - 5}" r="6" fill="{PALETTE[i]}"/>'
                    f'<text x="{bx + 20}" y="{by}" fill="{LAV}" font-size="14">{name}</text>'
                    f'<text x="{bx + 182}" y="{by}" fill="{MUTED}" font-size="13" text-anchor="end">{100 * v / tot:.1f}%</text></g>')
    css = (".seg{transform-box:fill-box;transform-origin:left;animation:grow 1s ease-out both}"
           "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}")
    with open(os.path.join(OUT, "langs.svg"), "w", encoding="utf-8") as f:
        f.write(frame(424, 270, "lenguajes más usados", "\n".join(body), css))

    # -------- actividad (últimos 60 días)
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]][-60:]
    w, h = 900, 300
    x0, x1, y0, y1 = 50, 870, 250, 70
    mx = max([d["contributionCount"] for d in days] + [4])
    pts = []
    for i, d in enumerate(days):
        px = x0 + (x1 - x0) * i / (len(days) - 1)
        py = y0 - (y0 - y1) * d["contributionCount"] / mx
        pts.append((px, py))
    line = " ".join(f"{'M' if i == 0 else 'L'}{px:.1f} {py:.1f}" for i, (px, py) in enumerate(pts))
    area = line + f" L{x1} {y0} L{x0} {y0} Z"
    grid = "".join(f'<line x1="{x0}" x2="{x1}" y1="{y0 - (y0 - y1) * k / 4:.0f}" y2="{y0 - (y0 - y1) * k / 4:.0f}" stroke="{LINE}" stroke-dasharray="3 6"/>'
                   f'<text x="{x0 - 10}" y="{y0 - (y0 - y1) * k / 4 + 4:.0f}" fill="{MUTED}" font-size="11" text-anchor="end">{round(mx * k / 4)}</text>'
                   for k in range(5))
    pts_svg = "".join(f'<circle class="pt" cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{AMBER}" style="animation-delay:{1.5 + i * .02:.2f}s"/>'
                      for i, (px, py) in enumerate(pts) if days[i]["contributionCount"] > 0)
    first = date.fromisoformat(days[0]["date"]).strftime("%d/%m")
    last = date.fromisoformat(days[-1]["date"]).strftime("%d/%m")
    body = (f'{grid}<path d="{area}" fill="url(#ar)" class="ar"/>'
            f'<path d="{line}" fill="none" stroke="url(#pg)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" class="ln" pathLength="1"/>'
            f'{pts_svg}<text x="{x0}" y="{y0 + 26}" fill="{MUTED}" font-size="12">{first}</text>'
            f'<text x="{x1}" y="{y0 + 26}" fill="{MUTED}" font-size="12" text-anchor="end">{last}</text>'
            f'<text x="{w - 24}" y="38" fill="{MUTED}" font-size="12" text-anchor="end">últimos 60 días</text>')
    css = (".ln{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.4s ease-out forwards}"
           "@keyframes draw{to{stroke-dashoffset:0}}"
           ".ar{opacity:0;animation:fa 1.5s ease-out 1s forwards}@keyframes fa{to{opacity:1}}"
           ".pt{opacity:0;animation:fa .4s ease-out forwards}")
    with open(os.path.join(OUT, "activity.svg"), "w", encoding="utf-8") as f:
        f.write(frame(w, h, "contribuciones", body, css))
    print("tarjetas generadas en", OUT)


if __name__ == "__main__":
    main()
