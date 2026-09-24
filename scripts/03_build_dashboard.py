"""
Builds the self-contained interactive HTML dashboard from the cleaned data.
Run after 01_clean_data.py has produced ../data/superstore_clean.csv.
"""
import json
import pandas as pd

df = pd.read_csv("../data/superstore_clean.csv", parse_dates=["Order Date", "Ship Date"])

def agg(g):
    out = g.agg(revenue=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
    out["margin"] = (out["profit"] / out["revenue"] * 100).round(2)
    out["revenue"] = out["revenue"].round(2)
    out["profit"] = out["profit"].round(2)
    return out.reset_index()

kpis = dict(
    revenue=round(df["Sales"].sum(), 2),
    profit=round(df["Profit"].sum(), 2),
    margin=round(df["Profit"].sum() / df["Sales"].sum() * 100, 2),
    orders=int(df["Order ID"].nunique()),
    customers=int(df["Customer ID"].nunique()),
    aov=round(df["Sales"].sum() / df["Order ID"].nunique(), 2),
    date_min=str(df["Order Date"].min().date()),
    date_max=str(df["Order Date"].max().date()),
)

monthly = agg(df.groupby("Order Year-Month"))
yearly = agg(df.groupby("Order Year"))
region = agg(df.groupby("Region")).sort_values("revenue", ascending=False)
category = agg(df.groupby("Category")).sort_values("revenue", ascending=False)
subcat = agg(df.groupby(["Category", "Sub-Category"])).sort_values("profit")
segment = agg(df.groupby("Segment")).sort_values("revenue", ascending=False)

disc_bins = [-0.01, 0, 0.2, 0.4, 0.6, 1.0]
disc_labels = ["0% (none)", "1-20%", "21-40%", "41-60%", "60%+"]
df["discount_band"] = pd.cut(df["Discount"], bins=disc_bins, labels=disc_labels)
discount = agg(df.groupby("discount_band", observed=True))

shipmode = (
    df.groupby("Ship Mode")
    .agg(avg_days=("Days to Ship", "mean"), orders=("Order ID", "nunique"), revenue=("Sales", "sum"))
    .round(2)
    .reset_index()
)

top_customers = (
    df.groupby(["Customer Name", "Segment"])
    .agg(revenue=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
    .round(2).reset_index().sort_values("revenue", ascending=False).head(10)
)

top_products = (
    df.groupby(["Product Name", "Category"])
    .agg(revenue=("Sales", "sum"), profit=("Profit", "sum"))
    .round(2).reset_index().sort_values("profit", ascending=False).head(10)
)
bottom_products = (
    df.groupby(["Product Name", "Category"])
    .agg(revenue=("Sales", "sum"), profit=("Profit", "sum"))
    .round(2).reset_index().sort_values("profit").head(10)
)

state = (
    df.groupby("State/Province")
    .agg(revenue=("Sales", "sum"), profit=("Profit", "sum"))
    .round(2).reset_index().sort_values("revenue", ascending=False)
)

returns_summary = (
    df.groupby("Is Returned")
    .agg(revenue=("Sales", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
    .round(2).reset_index()
)

DATA = dict(
    kpis=kpis,
    monthly=monthly.to_dict("records"),
    yearly=yearly.to_dict("records"),
    region=region.to_dict("records"),
    category=category.to_dict("records"),
    subcat=subcat.to_dict("records"),
    segment=segment.to_dict("records"),
    discount=discount.to_dict("records"),
    shipmode=shipmode.to_dict("records"),
    top_customers=top_customers.to_dict("records"),
    top_products=top_products.to_dict("records"),
    bottom_products=bottom_products.to_dict("records"),
    state=state.to_dict("records"),
    returns=returns_summary.to_dict("records"),
)

DATA_JSON = json.dumps(DATA)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Superstore Sales Performance & Revenue Analytics</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script>
  // Try cdnjs first; if that fails to load (network/CSP block specific to
  // that host), automatically fall back to jsdelivr before giving up.
  (function loadChartJs() {
    var CDNS = [
      'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js',
      'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js'
    ];
    function tryLoad(i) {
      if (i >= CDNS.length) { window.__chartLoadFailed = true; return; }
      var s = document.createElement('script');
      s.src = CDNS[i];
      s.onload = function(){ window.__chartLoaded = true; };
      s.onerror = function(){ tryLoad(i + 1); };
      document.head.appendChild(s);
    }
    tryLoad(0);
  })();
</script>
<style>
:root{
  --ink:#16202b; --paper:#f7f5f0; --panel:#ffffff; --line:#dcd6c9;
  --muted:#6b7280; --accent:#2f6f4f; --accent-soft:#e4efe6;
  --loss:#b5432f; --loss-soft:#f7e6e1;
  --gold:#b08b2a;
  --radius:2px;
  box-sizing:border-box;
  padding-top: env(safe-area-inset-top, 0px);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ink:#e9e6de; --paper:#14181a; --panel:#1b2023; --line:#31363a;
    --muted:#9aa1a6; --accent:#6fbd93; --accent-soft:#1e2b23;
    --loss:#e08669; --loss-soft:#2b1c18; --gold:#d8b85a;
  }
}
:root[data-theme="dark"]{
  --ink:#e9e6de; --paper:#14181a; --panel:#1b2023; --line:#31363a;
  --muted:#9aa1a6; --accent:#6fbd93; --accent-soft:#1e2b23;
  --loss:#e08669; --loss-soft:#2b1c18; --gold:#d8b85a;
}
*{box-sizing:border-box;}
html{scroll-padding-top: env(safe-area-inset-top, 0px);}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:'Inter',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
}
.mono{font-family:'IBM Plex Mono',monospace;}
header{
  padding:2.2rem 2rem 1.4rem; border-bottom:1px solid var(--line);
  display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:1rem;
}
.title-block h1{
  font-family:'Fraunces',serif; font-weight:600; font-size:2rem; margin:0 0 .3rem;
  letter-spacing:-.01em;
}
.title-block p{margin:0; color:var(--muted); font-size:.92rem; max-width:46ch;}
.range{font-size:.78rem; color:var(--muted); text-align:right;}
nav{
  display:flex; gap:0; border-bottom:1px solid var(--line); overflow-x:auto;
  padding:0 2rem; background:var(--paper); position:sticky; top:0; z-index:5;
}
nav button{
  font-family:'Inter',sans-serif; font-size:.86rem; font-weight:500; color:var(--muted);
  background:none; border:none; padding:.9rem 1rem; cursor:pointer; white-space:nowrap;
  border-bottom:2px solid transparent; transition:color .15s, border-color .15s;
}
nav button.active{color:var(--ink); border-bottom-color:var(--accent);}
nav button:hover{color:var(--ink);}
main{padding:1.8rem 2rem 4rem; max-width:1180px; margin:0 auto;}
.view{display:none;}
.view.active{display:block;}
.kpis{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px;
  background:var(--line); border:1px solid var(--line); margin-bottom:1.6rem;
}
.kpi{background:var(--panel); padding:1rem 1.1rem;}
.kpi .label{font-size:.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:.04em;}
.kpi .value{font-family:'Fraunces',serif; font-size:1.5rem; font-weight:600; margin-top:.2rem;}
.kpi .value.pos{color:var(--accent);}
.kpi .value.neg{color:var(--loss);}
.grid2{display:grid; grid-template-columns:1.4fr 1fr; gap:1.4rem; margin-bottom:1.4rem;}
.grid3{display:grid; grid-template-columns:repeat(3,1fr); gap:1.4rem; margin-bottom:1.4rem;}
@media (max-width:820px){.grid2,.grid3{grid-template-columns:1fr;}}
.panel{
  background:var(--panel); border:1px solid var(--line); padding:1.2rem 1.3rem;
}
.panel h3{
  font-family:'Fraunces',serif; font-size:1rem; font-weight:600; margin:0 0 .2rem;
}
.panel .sub{font-size:.78rem; color:var(--muted); margin-bottom:.9rem;}
.chart-wrap{position:relative; height:280px;}
.chart-wrap.tall{height:340px;}
table{width:100%; border-collapse:collapse; font-size:.84rem;}
th{
  text-align:left; font-size:.7rem; text-transform:uppercase; letter-spacing:.04em;
  color:var(--muted); font-weight:600; padding:.5rem .5rem; border-bottom:1px solid var(--line);
}
td{padding:.5rem .5rem; border-bottom:1px solid var(--line);}
td.num, th.num{text-align:right; font-family:'IBM Plex Mono',monospace; font-variant-numeric:tabular-nums;}
tr:last-child td{border-bottom:none;}
.pos-text{color:var(--accent);}
.neg-text{color:var(--loss);}
.bar-cell{position:relative;}
.bar-track{height:6px; background:var(--line); width:100%; margin-top:4px; overflow:hidden;}
.bar-fill{height:100%; background:var(--accent);}
.bar-fill.neg{background:var(--loss);}
.table-scroll{overflow-x:auto;}
.note{
  font-size:.78rem; color:var(--muted); border-left:2px solid var(--gold); padding:.5rem .9rem;
  background:var(--accent-soft); margin-top:1rem;
}
.insight{
  border-left:2px solid var(--accent); padding:.6rem 1rem; margin:.9rem 0; font-size:.86rem;
  background:var(--panel);
}
.insight.warn{border-left-color:var(--loss);}
footer{padding:2rem; text-align:center; color:var(--muted); font-size:.75rem; border-top:1px solid var(--line);}
</style>
</head>
<body>

<header>
  <div class="title-block">
    <h1>Superstore Sales Performance</h1>
    <p>Revenue, profitability, and customer analytics across __ORDERS__ orders and __CUSTOMERS__ customers.</p>
  </div>
  <div class="range mono">__DATE_MIN__ &ndash; __DATE_MAX__<br>US &amp; Canada retail orders</div>
</header>

<nav>
  <button data-view="overview" class="active">Overview</button>
  <button data-view="profitability">Profitability</button>
  <button data-view="customers">Customers &amp; Products</button>
  <button data-view="geography">Geography</button>
</nav>

<main>

  <div class="kpis" id="kpiStrip"></div>

  <!-- OVERVIEW -->
  <section class="view active" id="view-overview">
    <div class="panel" style="margin-bottom:1.4rem;">
      <h3>Monthly revenue &amp; profit</h3>
      <div class="sub">Jan 2023 &ndash; Dec 2026, order month</div>
      <div class="chart-wrap tall"><canvas id="chartMonthly"></canvas></div>
    </div>
    <div class="grid2">
      <div class="panel">
        <h3>Revenue by region</h3>
        <div class="sub">Bar length = revenue, label = margin</div>
        <div class="chart-wrap"><canvas id="chartRegion"></canvas></div>
      </div>
      <div class="panel">
        <h3>Revenue by category</h3>
        <div class="chart-wrap"><canvas id="chartCategory"></canvas></div>
      </div>
    </div>
    <div class="insight">Revenue has grown every year since 2023, and __YOY__ from 2025 to 2026 &mdash; but margin has stayed roughly flat near 13%, so growth is not yet translating into proportionally higher profit.</div>
  </section>

  <!-- PROFITABILITY -->
  <section class="view" id="view-profitability">
    <div class="grid2">
      <div class="panel">
        <h3>Margin by discount band</h3>
        <div class="sub">Every line item, grouped by discount applied</div>
        <div class="chart-wrap"><canvas id="chartDiscount"></canvas></div>
      </div>
      <div class="panel">
        <h3>Ship mode</h3>
        <div class="sub">Avg. days to ship vs. order volume</div>
        <div class="chart-wrap"><canvas id="chartShip"></canvas></div>
      </div>
    </div>
    <div class="insight warn">Margin turns negative once discounts exceed ~20%. Line items discounted 60%+ lost money overall &mdash; discounting past ~20% is destroying more profit than it recovers in volume.</div>
    <div class="panel">
      <h3>Category &amp; sub-category profitability</h3>
      <div class="sub">Sorted by profit, worst first</div>
      <div class="table-scroll"><table id="tblSubcat">
        <thead><tr><th>Category</th><th>Sub-Category</th><th class="num">Revenue</th><th class="num">Profit</th><th class="num">Margin</th></tr></thead>
        <tbody></tbody>
      </table></div>
    </div>
  </section>

  <!-- CUSTOMERS & PRODUCTS -->
  <section class="view" id="view-customers">
    <div class="grid2">
      <div class="panel">
        <h3>Top 10 customers by revenue</h3>
        <div class="table-scroll"><table id="tblCustomers">
          <thead><tr><th>Customer</th><th>Segment</th><th class="num">Revenue</th><th class="num">Profit</th><th class="num">Orders</th></tr></thead>
          <tbody></tbody>
        </table></div>
      </div>
      <div class="panel">
        <h3>Segment mix</h3>
        <div class="chart-wrap"><canvas id="chartSegment"></canvas></div>
      </div>
    </div>
    <div class="grid2">
      <div class="panel">
        <h3>Top 10 products by profit</h3>
        <div class="table-scroll"><table id="tblTopProducts">
          <thead><tr><th>Product</th><th class="num">Revenue</th><th class="num">Profit</th></tr></thead>
          <tbody></tbody>
        </table></div>
      </div>
      <div class="panel">
        <h3>10 biggest loss-makers</h3>
        <div class="table-scroll"><table id="tblBottomProducts">
          <thead><tr><th>Product</th><th class="num">Revenue</th><th class="num">Profit</th></tr></thead>
          <tbody></tbody>
        </table></div>
      </div>
    </div>
  </section>

  <!-- GEOGRAPHY -->
  <section class="view" id="view-geography">
    <div class="panel">
      <h3>Top 10 states by revenue</h3>
      <div class="sub">Profit shown alongside &mdash; note the states with strong revenue but negative profit</div>
      <div class="table-scroll"><table id="tblState">
        <thead><tr><th>State</th><th class="num">Revenue</th><th class="num">Profit</th></tr></thead>
        <tbody></tbody>
      </table></div>
      <div class="note">Texas, Pennsylvania, Illinois and Ohio each generate six-figure revenue but post a net loss &mdash; a strong signal to review regional discount policy and freight-heavy categories (Furniture, Machines) in those states.</div>
    </div>
  </section>

</main>

<footer>Built from the Sample Superstore dataset &middot; cleaned with pandas, analyzed with SQL &middot; __ORDERS__ orders, __ITEMS__ line items</footer>

<script>
const DATA = __DATA_JSON__;
const fmt$ = n => '$' + Number(n).toLocaleString('en-US', {maximumFractionDigits:0});
const fmtPct = n => Number(n).toFixed(1) + '%';

// ---- KPI strip (renders regardless of chart library) ----
const k = DATA.kpis;
const kpiHtml = [
  ['Total Revenue', fmt$(k.revenue), null],
  ['Total Profit', fmt$(k.profit), k.profit>=0?'pos':'neg'],
  ['Overall Margin', fmtPct(k.margin), k.margin>=0?'pos':'neg'],
  ['Orders', k.orders.toLocaleString(), null],
  ['Customers', k.customers.toLocaleString(), null],
  ['Avg. Order Value', fmt$(k.aov), null],
].map(([label,val,cls])=>`<div class="kpi"><div class="label">${label}</div><div class="value ${cls||''}">${val}</div></div>`).join('');
document.getElementById('kpiStrip').innerHTML = kpiHtml;

document.title = "Superstore Sales Performance & Revenue Analytics";

// fill header placeholders
document.querySelectorAll('.title-block p').forEach(el=>{
  el.innerHTML = el.innerHTML.replace('__ORDERS__', k.orders.toLocaleString()).replace('__CUSTOMERS__', k.customers.toLocaleString());
});
document.querySelector('.range').innerHTML = document.querySelector('.range').innerHTML
  .replace('__DATE_MIN__', k.date_min).replace('__DATE_MAX__', k.date_max);
document.querySelector('footer').innerHTML = document.querySelector('footer').innerHTML
  .replace('__ORDERS__', k.orders.toLocaleString());

// YoY figure
const y = DATA.yearly;
const last = y[y.length-1], prev = y[y.length-2];
const yoy = prev ? (((last.revenue-prev.revenue)/prev.revenue)*100).toFixed(1)+'%' : '';
document.querySelectorAll('.insight').forEach(el=>{ el.innerHTML = el.innerHTML.replace('__YOY__', 'grew ' + yoy); });

// ---- Nav ----
document.querySelectorAll('nav button').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('nav button').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('view-'+btn.dataset.view).classList.add('active');
  });
});

// ---- Charts: wait for the charting library, don't assume script execution order ----
function initCharts() {
  const CSS = getComputedStyle(document.documentElement);
  const cVar = n => CSS.getPropertyValue(n).trim();
  Chart.defaults.font.family = "Inter, sans-serif";
  Chart.defaults.color = cVar('--muted');
  Chart.defaults.borderColor = cVar('--line');
  const accent = cVar('--accent'), loss = cVar('--loss'), gold = cVar('--gold'), line = cVar('--line'), ink = cVar('--ink');

  new Chart(document.getElementById('chartMonthly'), {
    type:'line',
    data:{ labels: DATA.monthly.map(d=>d['Order Year-Month']),
      datasets:[
        {label:'Revenue', data: DATA.monthly.map(d=>d.revenue), borderColor: ink, backgroundColor: 'transparent', tension:.25, borderWidth:2, pointRadius:0},
        {label:'Profit', data: DATA.monthly.map(d=>d.profit), borderColor: accent, backgroundColor: 'transparent', tension:.25, borderWidth:2, pointRadius:0}
      ]},
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{legend:{position:'top', align:'end', labels:{boxWidth:10}}},
      scales:{ x:{ticks:{maxTicksLimit:12}, grid:{display:false}}, y:{ticks:{callback:v=>fmt$(v)}} } }
  });

  new Chart(document.getElementById('chartRegion'), {
    type:'bar',
    data:{ labels: DATA.region.map(d=>d.Region),
      datasets:[{label:'Revenue', data: DATA.region.map(d=>d.revenue), backgroundColor: accent, borderRadius:2}]},
    options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{ x:{ticks:{callback:v=>fmt$(v)}}, y:{grid:{display:false}} } }
  });

  new Chart(document.getElementById('chartCategory'), {
    type:'doughnut',
    data:{ labels: DATA.category.map(d=>d.Category),
      datasets:[{data: DATA.category.map(d=>d.revenue), backgroundColor:[ink, accent, gold]}]},
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom', labels:{boxWidth:10}}} }
  });

  new Chart(document.getElementById('chartDiscount'), {
    type:'bar',
    data:{ labels: DATA.discount.map(d=>d.discount_band),
      datasets:[{label:'Margin %', data: DATA.discount.map(d=>d.margin),
        backgroundColor: DATA.discount.map(d=>d.margin>=0?accent:loss), borderRadius:2}]},
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{ y:{ticks:{callback:v=>v+'%'}}, x:{grid:{display:false}} } }
  });

  new Chart(document.getElementById('chartShip'), {
    type:'bar',
    data:{ labels: DATA.shipmode.map(d=>d['Ship Mode']),
      datasets:[
        {label:'Avg days to ship', data: DATA.shipmode.map(d=>d.avg_days), backgroundColor: gold, yAxisID:'y', borderRadius:2},
      ]},
    options:{ responsive:true, maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{ y:{title:{display:true,text:'Days'}}, x:{grid:{display:false}} } }
  });

  new Chart(document.getElementById('chartSegment'), {
    type:'pie',
    data:{ labels: DATA.segment.map(d=>d.Segment),
      datasets:[{data: DATA.segment.map(d=>d.revenue), backgroundColor:[accent, ink, gold]}]},
    options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom', labels:{boxWidth:10}}} }
  });
}

function showChartFallback() {
  document.querySelectorAll('.chart-wrap').forEach(el=>{
    el.innerHTML = '<p style="color:var(--muted); font-size:.8rem; padding-top:1rem;">Charts couldn\\'t load (the charting library didn\\'t come through from the CDN). The KPIs and tables on this page are unaffected. Try reloading, or disabling any script/content blockers for this page.</p>';
  });
}

// Poll for the library rather than assuming <script> execution order.
// Handles the case where the browser doesn't block on external scripts
// the way a plain HTML page normally would.
(function waitForChart(attemptsLeft) {
  if (typeof Chart !== 'undefined') { initCharts(); return; }
  if (window.__chartLoadFailed) { showChartFallback(); return; }
  if (attemptsLeft <= 0) { showChartFallback(); return; }
  setTimeout(() => waitForChart(attemptsLeft - 1), 150);
})(40); // ~6 seconds total

// ---- Tables ----
function rows(sel, data, mapper){
  document.querySelector(sel+' tbody').innerHTML = data.map(mapper).join('');
}

rows('#tblSubcat', DATA.subcat, d=>`<tr>
  <td>${d.Category}</td><td>${d['Sub-Category']}</td>
  <td class="num">${fmt$(d.revenue)}</td>
  <td class="num ${d.profit>=0?'pos-text':'neg-text'}">${fmt$(d.profit)}</td>
  <td class="num ${d.margin>=0?'pos-text':'neg-text'}">${fmtPct(d.margin)}</td>
</tr>`);

rows('#tblCustomers', DATA.top_customers, d=>`<tr>
  <td>${d['Customer Name']}</td><td>${d.Segment}</td>
  <td class="num">${fmt$(d.revenue)}</td>
  <td class="num ${d.profit>=0?'pos-text':'neg-text'}">${fmt$(d.profit)}</td>
  <td class="num">${d.orders}</td>
</tr>`);

rows('#tblTopProducts', DATA.top_products, d=>`<tr>
  <td>${d['Product Name']}</td>
  <td class="num">${fmt$(d.revenue)}</td>
  <td class="num pos-text">${fmt$(d.profit)}</td>
</tr>`);

rows('#tblBottomProducts', DATA.bottom_products, d=>`<tr>
  <td>${d['Product Name']}</td>
  <td class="num">${fmt$(d.revenue)}</td>
  <td class="num neg-text">${fmt$(d.profit)}</td>
</tr>`);

rows('#tblState', DATA.state, d=>`<tr>
  <td>${d['State/Province']}</td>
  <td class="num">${fmt$(d.revenue)}</td>
  <td class="num ${d.profit>=0?'pos-text':'neg-text'}">${fmt$(d.profit)}</td>
</tr>`);
</script>
</body>
</html>
"""

html = HTML.replace("__DATA_JSON__", DATA_JSON)
html = html.replace("__ORDERS__", str(DATA["kpis"]["orders"]))
html = html.replace("__CUSTOMERS__", str(DATA["kpis"]["customers"]))
html = html.replace("__DATE_MIN__", DATA["kpis"]["date_min"])
html = html.replace("__DATE_MAX__", DATA["kpis"]["date_max"])
html = html.replace("__ITEMS__", "10,194")

with open("../dashboard/superstore_dashboard.html", "w") as f:
    f.write(html)

print("Dashboard written:", len(html), "bytes")
