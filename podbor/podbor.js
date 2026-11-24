// Подбор: считаем стоимость квартиры (цена «от» × площадь), берём ЖК, которые влезают в бюджет,
// ближе всего к бюджету — сверху. Если подходящих меньше трёх, добавляем ближайшие дороже бюджета с пометкой.
function podbor(list, city, budgetRub, area) {
  var all = list.filter(function (z) { return z.city === city; })
    .map(function (z) { return Object.assign({}, z, { cost: z.ppm * area }); });
  var fit = all.filter(function (z) { return z.cost <= budgetRub; }).sort(function (a, b) { return b.cost - a.cost; });
  var over = all.filter(function (z) { return z.cost > budgetRub; }).sort(function (a, b) { return a.cost - b.cost; })
    .map(function (z) { return Object.assign(z, { over: true }); });
  return fit.concat(over).slice(0, 3);
}

if (typeof document !== 'undefined') {
  var fmt = function (n) { return Math.round(n).toLocaleString('ru-RU'); };
  var num = function (n) { return (n / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 }); };
  var mln = function (n) { return num(n) + ' млн ₽'; };
  var $ = function (id) { return document.getElementById(id); };
  var IN = { 'Сочи': 'в Сочи', 'Москва': 'в Москве', 'Краснодар': 'в Краснодаре' };
  var WORD = function (n) { return n === 1 ? 'вариант' : (n < 5 ? 'варианта' : 'вариантов'); };
  $('d').textContent = window.ZHK_DATE.split('-').reverse().slice(0, 2).join('.');
  var form = $('f'), res = $('res');
  var getCity = function () { return form.querySelector('input[name=city]:checked').value; };
  function fill(el) { el.style.setProperty('--p', ((el.value - el.min) / (el.max - el.min) * 100) + '%'); }
  function labels() {
    $('budgetOut').textContent = parseFloat($('budget').value).toLocaleString('ru-RU') + ' млн ₽';
    $('areaOut').textContent = $('area').value + ' м²';
    fill($('budget')); fill($('area'));
  }
  function run(e) {
    if (e) e.preventDefault();
    labels();
    var city = getCity();
    if (window.setBg) window.setBg(city);
    var budget = parseFloat($('budget').value) * 1e6;
    var area = parseFloat($('area').value);
    var out = podbor(window.ZHK, city, budget, area);
    var fits = out.filter(function (z) { return !z.over; }).length;
    $('rtitle').textContent = fits ? fits + ' ' + WORD(fits) + ' ' + IN[city] : 'Ничего не входит в бюджет';
    $('rnote').textContent = fits
      ? 'Квартира ' + area + ' м² в пределах ' + mln(budget) + '. Первым — комплекс, ближе всего к вашему бюджету.'
      : 'За ' + mln(budget) + ' квартира ' + area + ' м² ' + IN[city] + ' не найдётся. Показываем ближайшие варианты.';
    res.innerHTML = out.map(function (z, i) {
      var pct = Math.min(100, Math.round(z.cost / budget * 100));
      var tag = z.over ? '<span class="tag over">Выше бюджета</span>' : (i === 0 ? '<span class="tag">Лучшее совпадение</span>' : '');
      var left = z.over ? 'Дороже на ' + mln(z.cost - budget) : 'Остаётся ' + mln(budget - z.cost);
      return '<a class="card' + (z.over ? ' over' : (i === 0 ? ' best' : '')) + '" href="' + z.src + '" target="_blank" rel="noopener" aria-label="' + z.name + ' — открыть на ЕРЗ">' +
        '<div class="rank"><b>0' + (i + 1) + '</b>' + tag + '</div>' +
        '<h3>' + z.name + '</h3>' +
        '<p class="sub">' + z.dev + ' · ' + z.district + '</p>' +
        '<div class="cost">≈ ' + num(z.cost) + ' <small>млн ₽</small></div>' +
        '<div class="meter" title="' + pct + '% бюджета"><i style="width:' + pct + '%"></i></div>' +
        '<div class="left">' + left + '</div>' +
        '<dl><dt>Класс</dt><dd>' + z.class + '</dd><dt>Сдача</dt><dd>' + z.deadline + '</dd><dt>Цена от</dt><dd>' + fmt(z.ppm) + ' ₽/м²</dd></dl>' +
        '<div class="src">Смотреть на ЕРЗ <span>→</span></div>' +
        '</a>';
    }).join('');
  }
  var q = new URLSearchParams(location.search);
  if (q.get('city')) { var r = form.querySelector('input[name=city][value="' + q.get('city') + '"]'); if (r) r.checked = true; }
  if (q.get('budget')) $('budget').value = q.get('budget');
  if (q.get('area')) $('area').value = q.get('area');
  form.addEventListener('submit', run);
  form.addEventListener('input', run);
  run();
}

if (typeof module !== 'undefined') module.exports = { podbor: podbor };
