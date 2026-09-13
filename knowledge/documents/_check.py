import os, re, glob

os.chdir(os.path.dirname(os.path.abspath(__file__)))

for d in ['jobs','skills','companies','interview','projects','roadmap','resume','market','competition','policies']:
    files = glob.glob(os.path.join(d, '*.md'))
    no_fm, no_ref, small = [], [], []
    for f in files:
        content = open(f, encoding='utf-8').read()
        if not content.startswith('---'):
            no_fm.append(os.path.basename(f))
        if not re.search(r'^#+.*Reference|参考来源|参考资料|数据来源', content, re.I | re.M):
            no_ref.append(os.path.basename(f))
        if len(content) < 1500:
            small.append((os.path.basename(f), len(content)))
    print(f'{d}: {len(files)}p | noFM:{len(no_fm)} | noRef:{len(no_ref)} | small:{len(small)}')
    if no_fm: print('   noFM:', ', '.join(no_fm[:10]))
    if no_ref: print('   noRef:', ', '.join(no_ref[:10]))
    if small: print('   small:', ', '.join(n + '(' + str(c) + ')' for n, c in small[:10]))
