#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规范化播放列表：补 tvg-id / tvg-logo 占位、去重、统一分组顺序、加头注释。"""
import re, sys, io

SRC = sys.argv[1]
DST = sys.argv[2]

GROUP_ORDER = ["央视", "卫视频道", "山东本地"]

text = io.open(SRC, encoding="utf-8").read().replace("\r\n", "\n").strip()
lines = [l for l in text.split("\n") if l.strip()]

entries = []          # (group, tvg_name, display, url)
seen_url = set()
seen_name = set()
i = 0
while i < len(lines):
    l = lines[i]
    if l.startswith("#EXTINF"):
        m = re.search(r'tvg-name="([^"]*)"', l)
        g = re.search(r'group-title="([^"]*)"', l)
        name = l.rsplit(",", 1)[-1].strip()
        tvg = m.group(1) if m else name
        grp = g.group(1) if g else "其他"
        url = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if url and not url.startswith("#"):
            if url not in seen_url and name not in seen_name:
                seen_url.add(url)
                seen_name.add(name)
                entries.append((grp, tvg, name, url))
        i += 2
    else:
        i += 1

# 分组排序
groups = {}
for grp, tvg, name, url in entries:
    groups.setdefault(grp, []).append((tvg, name, url))

ordered = [g for g in GROUP_ORDER if g in groups]
ordered += [g for g in groups if g not in GROUP_ORDER]

out = []
out.append("#EXTM3U")
out.append("# 直播源 · 共 %d 个频道 / %d 个分组" % (len(entries), len(ordered)))
# 注释里不要出现 URL —— 某些简陋播放器会粗暴地 grep 出所有 http 链接
out.append("# 源站：山东电信 HMS CDN（302 跳转，带时效 token）")
out.append("# 播放器需支持跟随 302 重定向；非山东/非电信网络可能不可用")
out.append("")

def natkey(s):
    """CCTV2 < CCTV10，中文保持原序"""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]

for g in ordered:
    items = sorted(groups[g], key=lambda x: natkey(x[1]))
    out.append("# ===== %s（%d） =====" % (g, len(items)))
    for tvg, name, url in items:
        out.append('#EXTINF:-1 tvg-id="%s" tvg-name="%s" group-title="%s",%s' % (tvg, tvg, g, name))
        out.append(url)
    out.append("")

io.open(DST, "w", encoding="utf-8", newline="\n").write("\n".join(out).rstrip() + "\n")
print("in=%d  out=%d  groups=%s" % (len(entries), len(entries), ordered))
