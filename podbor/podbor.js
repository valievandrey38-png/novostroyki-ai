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
  var mln = function (n) { return (n / 1e6).toLocaleString('ru-RU', { maximumFractionDigits: 1 }) + ' млн ₽'; };
  document.getElementById('d').textContent = window.ZHK_DATE.split('-').reverse().join('.');
  var form = document.getElementById('f'), res = document.getElementById('res');
  function run(e) {
    if (e) e.preventDefault();
    var city = document.getElementById('city').value;
    var budget = parseFloat(document.getElementById('budget').value) * 1e6;
    var area = parseFloat(document.getElementById('area').value);
    if (!(budget > 0) || !(area > 0)) { res.innerHTML = '<p class="msg">Введите бюджет и площадь.</p>'; return; }
    var out = podbor(window.ZHK, city, budget, area);
    var fits = out.filter(function (z) { return !z.over; }).length;
    var head = fits === 0
      ? '<p class="msg">В бюджет ' + mln(budget) + ' за ' + area + ' м² в г. ' + city + ' ничего не входит. Ближайшие варианты:</p>'
      : '<p class="msg">Подходит ' + fits + ' из ' + out.length + '. Сверху — самые близкие к бюджету.</p>';
    res.innerHTML = head + out.map(function (z) {
      return '<article class="item' + (z.over ? ' over' : '') + '">' +
        (z.over ? '<span class="tag">Дороже бюджета на ' + mln(z.cost - budget) + '</span>' : '') +
        '<h2>' + z.name + '</h2>' +
        '<div class="price">≈ ' + mln(z.cost) + '</div>' +
        '<div class="row"><span>' + z.class + '</span><span>' + z.dev + '</span><span>' + z.district + '</span><span>сдача: ' + z.deadline + '</span></div>' +
        '<div class="row"><span>от ' + fmt(z.ppm) + ' ₽/м²</span><a href="' + z.src + '" target="_blank" rel="noopener">источник</a></div>' +
        '</article>';
    }).join('');
  }
  var q = new URLSearchParams(location.search);
  if (q.get('city')) document.getElementById('city').value = q.get('city');
  if (q.get('budget')) document.getElementById('budget').value = q.get('budget');
  if (q.get('area')) document.getElementById('area').value = q.get('area');
  form.addEventListener('submit', run);
  run();
}

if (typeof module !== 'undefined') module.exports = { podbor: podbor };
