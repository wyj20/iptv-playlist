#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""比对 playlist 的 tvg-id 与 EPG 源的 channel id，报告匹配率。"""
import re, sys, io, collections

playlist = sys.argv[1]
epgfiles = sys.argv[2:]

# 1) 读播放列表的 tvg-id
ids = []
for line in io.open(playlist, encoding="utf-8"):
    m = re.search(r'tvg-id="([^"]*)"', line)
    if m:
        ids.append(m.group(1))

print("播放列表 tvg-id 数: %d" % len(ids))
print()

# 2) 合并所有 EPG 源的 id 集合
src_ids = {}
for f in epgfiles:
    txt = io.open(f, encoding="utf-8", errors="replace").read()
    s = set(re.findall(r'<channel id="([^"]*)"', txt))
    name = f.split("/")[-1]
    src_ids[name] = s
    print("EPG %-16s 频道数 %d" % (name, len(s)))
print()

union = set()
for s in src_ids.values():
    union |= s
print("合并可用 id 总数: %d" % len(union))
print()

hit = [i for i in ids if i in union]
miss = [i for i in ids if i not in union]
print("=" * 50)
print("匹配: %d / %d  (%.0f%%)" % (len(hit), len(ids), 100.0 * len(hit) / len(ids)))
print("=" * 50)

if miss:
    print("\n未匹配的 %d 个频道:" % len(miss))
    for m in miss:
        print("  - %s" % m)
    print("\n各源命中情况:")
    for name, s in src_ids.items():
        n = sum(1 for i in ids if i in s)
        print("  %-16s %d/%d" % (name, n, len(ids)))
