#!/usr/bin/env python3
"""Собирает из data/zhk.json: таблицу CSV, график (SVG), раздел данных в README и данные для подборщика."""
import csv, json, pathlib, statistics

ROOT = pathlib.Path(__file__).resolve().parent
D = json.loads((ROOT / 'data' / 'zhk.json').read_text(encoding='utf-8'))
rows = D['rows']
CITIES = ['Москва', 'Сочи', 'Краснодар']
COLOR = {'Москва': '#3b6fb6', 'Сочи': '#d9822b', 'Краснодар': '#3f9a5a'}


def rub(n):
    return f'{n:,}'.replace(',', ' ')


# 1. CSV (открывается в Google Таблицах и Excel)
with open(ROOT / 'data' / 'zhk.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Город', 'ЖК', 'Застройщик', 'Район', 'Класс', 'Цена от, ₽/м²', 'Срок сдачи', 'Источник (ЕРЗ)', 'Источник района', 'Примечание'])
    for r in rows:
        w.writerow([r['city'], r['name'], r['dev'], r['district'], r['class'], r['ppm'], r['deadline'], r['src'], r['district_src'], r['note']])

# 2. График: горизонтальные столбики, цвет — город
srt = sorted(rows, key=lambda r: r['ppm'])
W, LEFT, RIGHT, TOP, BAR, GAP = 1000, 300, 130, 70, 26, 10
H = TOP + len(srt) * (BAR + GAP) + 60
mx = max(r['ppm'] for r in rows)
sx = lambda v: LEFT + (W - LEFT - RIGHT) * v / mx
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
       '<text x="20" y="32" font-size="20" font-weight="700" fill="#1d2226">Цена «от» за м² в новостройках бизнес- и премиум-класса</text>',
       f'<text x="20" y="54" font-size="13" fill="#5d6670">Источник: ЕРЗ.РФ, данные на {D["date"][8:10]}.{D["date"][5:7]}.{D["date"][:4]}. Цвет — город, штриховка — премиум-класс.</text>',
       '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="6" fill="#ffffff" fill-opacity=".35"/></pattern></defs>']
for t in range(0, mx + 1, 250000):
    x = sx(t)
    svg.append(f'<line x1="{x:.1f}" y1="{TOP - 6}" x2="{x:.1f}" y2="{H - 50}" stroke="#e4e6e3"/>')
    svg.append(f'<text x="{x:.1f}" y="{H - 32}" font-size="12" fill="#5d6670" text-anchor="middle">{t // 1000} тыс.</text>')
for i, r in enumerate(srt):
    y = TOP + i * (BAR + GAP)
    x1 = sx(r['ppm'])
    svg.append(f'<text x="{LEFT - 10}" y="{y + 18}" font-size="13" fill="#1d2226" text-anchor="end">{r["name"]} · {r["city"]}</text>')
    svg.append(f'<rect x="{LEFT}" y="{y}" width="{x1 - LEFT:.1f}" height="{BAR}" rx="3" fill="{COLOR[r["city"]]}"/>')
    if r['class'] == 'премиум':
        svg.append(f'<rect x="{LEFT}" y="{y}" width="{x1 - LEFT:.1f}" height="{BAR}" rx="3" fill="url(#hatch)"/>')
    svg.append(f'<text x="{x1 + 8:.1f}" y="{y + 18}" font-size="13" fill="#1d2226">{rub(r["ppm"])} ₽</text>')
lx = LEFT
for c in CITIES:
    svg.append(f'<rect x="{lx}" y="{H - 22}" width="14" height="14" rx="2" fill="{COLOR[c]}"/><text x="{lx + 20}" y="{H - 10}" font-size="13" fill="#1d2226">{c}</text>')
    lx += 130
svg.append('</svg>')
(ROOT / 'chart.svg').write_text('\n'.join(svg), encoding='utf-8')

# 3. Сводка для выводов
summary = {}
for c in CITIES:
    cr = [r for r in rows if r['city'] == c]
    biz = [r['ppm'] for r in cr if r['class'] == 'бизнес']
    prem = [r['ppm'] for r in cr if r['class'] == 'премиум']
    summary[c] = {'median': int(statistics.median(r['ppm'] for r in cr)), 'biz_med': int(statistics.median(biz)) if biz else None,
                  'prem_med': int(statistics.median(prem)) if prem else None, 'min': min(r['ppm'] for r in cr), 'max': max(r['ppm'] for r in cr)}
(ROOT / 'data' / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding='utf-8')

# 4. Таблица в Markdown (вставляется в README между маркерами)
md = ['| Город | ЖК | Застройщик | Район | Класс | Цена от, ₽/м² | Срок сдачи | Источник |', '|---|---|---|---|---|---:|---|---|']
for r in rows:
    src = f'[ЕРЗ]({r["src"]})' + (f', [район]({r["district_src"]})' if r['district_src'] != r['src'] else '')
    name = r['name'] + (f' <sup title="{r["note"]}">*</sup>' if r['note'] else '')
    md.append(f'| {r["city"]} | {name} | {r["dev"]} | {r["district"]} | {r["class"]} | {rub(r["ppm"])} | {r["deadline"]} | {src} |')
notes = [f'- **{r["name"]}:** {r["note"]}' for r in rows if r['note']]
block = '\n'.join(md) + '\n\n<sup>*</sup> Примечания:\n' + '\n'.join(notes)
readme = ROOT / 'README.md'
if readme.exists():
    t = readme.read_text(encoding='utf-8')
    a, b = t.find('<!-- TABLE -->'), t.find('<!-- /TABLE -->')
    if a != -1 and b != -1:
        readme.write_text(t[:a] + '<!-- TABLE -->\n' + block + '\n' + t[b:], encoding='utf-8')

# 5. Данные для подборщика (веб и Python)
lite = [{k: r[k] for k in ('city', 'name', 'dev', 'district', 'class', 'ppm', 'deadline', 'src')} for r in rows]
(ROOT / 'podbor' / 'data.js').write_text('window.ZHK = ' + json.dumps(lite, ensure_ascii=False, indent=1) + ';\nwindow.ZHK_DATE = "' + D['date'] + '";\n', encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=1))
