#!/usr/bin/env python3
"""Подборщик ЖК в терминале.

    python3 podbor/podbor.py                  # спросит город, бюджет и площадь
    python3 podbor/podbor.py Сочи 25 60       # бюджет в млн ₽, площадь в м²

Стоимость = цена «от» за м² × площадь (нижняя граница). Берём ЖК, которые влезают в бюджет,
ближе всего к нему; если их меньше трёх — добавляем ближайшие дороже бюджета с пометкой.
"""
import json, pathlib, sys

DATA = json.loads((pathlib.Path(__file__).resolve().parent.parent / 'data' / 'zhk.json').read_text(encoding='utf-8'))


def podbor(rows, city, budget_rub, area):
    allz = [dict(r, cost=r['ppm'] * area) for r in rows if r['city'].lower() == city.lower()]
    fit = sorted((z for z in allz if z['cost'] <= budget_rub), key=lambda z: -z['cost'])
    over = sorted((dict(z, over=True) for z in allz if z['cost'] > budget_rub), key=lambda z: z['cost'])
    return (fit + over)[:3]


def mln(n):
    return f'{n / 1e6:.1f} млн ₽'.replace('.', ',')


def main():
    if len(sys.argv) == 4:
        city, budget, area = sys.argv[1], float(sys.argv[2].replace(',', '.')), float(sys.argv[3].replace(',', '.'))
    else:
        city = input('Город (Сочи / Москва / Краснодар): ').strip()
        budget = float(input('Бюджет, млн ₽: ').replace(',', '.'))
        area = float(input('Площадь, м²: ').replace(',', '.'))
    cities = {r['city'] for r in DATA['rows']}
    if city.capitalize() not in cities:
        sys.exit(f'Нет данных по городу «{city}». Есть: {", ".join(sorted(cities))}')
    res = podbor(DATA['rows'], city, budget * 1e6, area)
    print(f'\n{city}, бюджет {mln(budget * 1e6)}, площадь {area:g} м²\n')
    for i, z in enumerate(res, 1):
        flag = f'  ⚠ дороже бюджета на {mln(z["cost"] - budget * 1e6)}' if z.get('over') else ''
        print(f'{i}. {z["name"]} ({z["class"]}, {z["dev"]}) — ≈ {mln(z["cost"])}{flag}')
        print(f'   {z["district"]} · сдача {z["deadline"]} · от {z["ppm"]:,} ₽/м²'.replace(',', ' '))
        print(f'   {z["src"]}')
    print(f'\nДанные: ЕРЗ.РФ на {DATA["date"]}. Цена «от» — нижняя граница.')


if __name__ == '__main__':
    main()
