import json
sb = json.loads(open(r'D:\西客松\scripts\video\storyboard_v236.json', encoding='utf-8').read())
for ch in sb['chapters']:
    idx = ch['chapter_index']
    title = ch['title']
    p0 = ch['core_points'][0][:60]
    print(f'ch{idx}: {title}')
    print(f'  points[0]: {p0}')