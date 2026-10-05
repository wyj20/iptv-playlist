#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 playlist 的 tvg-id 重映射成老张EPG(51zmt) 的 channel id，按 display-name 匹配。

用法: python3 remap_epg.py <playlist.m3u> <e1.xml.gz> <out.m3u>
"""
import gzip, re, io, sys

pl, epgpath, out = sys.argv[1], sys.argv[2], sys.argv[3]

# 已知的命名差异 -> 51zmt display-name
ALIAS = {
    "CCTV4 大陆": "CCTV4",
    "CCTV4 欧洲": "CCTV4EUO",
    "CCTV4 美洲": "CCTV4AME",
    "海南卫视":   "海南综合",
}

# 读 EPG: display-name -> id
d = gzip.open(epgpath, 'rt', encoding='utf-8', errors='replace').read()
pairs = re.findall(r'<channel id="([^"]*)">\s*<display-name[^>]*>([^<]*)</display-name>', d)
name2id = {}
for cid, nm in pairs:
    name2id.setdefault(nm.strip(), cid)
print("EPG 频道数: %d" % len(name2id))

lines = io.open(pl, encoding='utf-8').read().split('\n')
res, hit, miss = [], 0, []
for l in lines:
    m = re.match(r'(#EXTINF:[^,]*)\s*tvg-id="([^"]*)"[^,]*,?(.*)$', l)
    if not m:
        res.append(l); continue
    prefix, tid, rest = m.group(1), m.group(2), m.group(3)
    lookup = ALIAS.get(tid, tid)
    if lookup in name2id:
        newid = name2id[lookup]
        hit += 1
    else:
        newid = tid
        miss.append(tid)
    # 重写：tvg-id 换成 EPG 的 id，tvg-name 保留原台名方便阅读
    res.append(l.replace('tvg-id="%s"' % tid, 'tvg-id="%s"' % newid))

io.open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(res))
total = hit + len(miss)
print("匹配成功: %d / %d (%.0f%%)" % (hit, total, 100.0*hit/total))
print("\n仍未匹配 (%d):" % len(miss))
for x in miss:
    print("  - %s" % x)
