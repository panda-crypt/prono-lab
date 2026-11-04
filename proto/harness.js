// Usage: node harness.js <html> <out.json>
// Pour chaque match européen joué (même règle que backtest() : au moins 30 matchs européens antérieurs),
// renvoie la prédiction du modèle européen actuel et les variables nécessaires aux nouveaux modèles,
// calculées uniquement avec les matchs antérieurs au jour du match.
const { chromium } = require('playwright');
(async () => {
  const [file, out] = process.argv.slice(2);
  const b = await chromium.launch(); const ctx = await b.newContext({ timezoneId: 'Europe/Paris' });
  const p = await ctx.newPage(); await p.clock.install({ time: new Date('2026-11-04T09:00:00+01:00') });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  const res = await p.evaluate(() => {
    const euroK = Object.keys(DATA.leagues).filter(k => DATA.leagues[k].type === 'euro');
    const all = euroK.flatMap(lg => DATA.leagues[lg].matches.map(m => ({ lg, m })));
    const clubs = {}; euroK.forEach(lg => DATA.leagues[lg].teams.forEach(t => clubs[t.id] = t));
    const coef = DATA.uefaCountry;
    const days = [...new Set(all.filter(x => x.m.s || x.m.d < '2026-11-06').map(x => x.m.d.slice(0,10)))].sort();
    const recs = [];
    const domFeat = (t, before, cache) => {
      if (!t.dom || !DATA.leagues[t.dom.lg]) return null;
      const lg = t.dom.lg;
      cache[lg] = cache[lg] || computeLeague(DATA.leagues[lg], { before, useXg:false });
      const C = cache[lg], T = C.T[t.dom.id]; if (!T) return null;
      const g = T.games || [];
      const last = g.slice(-5);
      return { lg, att: Math.log(T.att), def: Math.log(T.def), mu: C.muAll, p: T.p != null ? T.p : g.length,
               form: last.length ? last.reduce((s,x)=>s+(x.gf>x.ga?3:x.gf===x.ga?1:0),0)/last.length : null,
               formGd: last.length ? last.reduce((s,x)=>s+x.gf-x.ga,0)/last.length : null };
    };
    days.forEach(day => {
      const before = day + 'T00:00';
      const ev0 = all.filter(x => x.m.s && x.m.d < before).length >= 30;
      const E = euroFit(before), cache = {};
      all.filter(x => (x.m.s || x.m.d < '2026-11-06') && x.m.d.slice(0,10) === day).forEach(({ lg, m }) => {
        const [lh, la] = euroLambdas(E, m.h, m.a, false), r = scoreMatrix(lh, la);
        const f = id => { const t = clubs[id]; return { id, country: t.country, coef: coef[t.country], dom: domFeat(t, before, cache) }; };
        recs.push({ ev: ev0 && !!m.s, up: !m.s, lg, d: m.d, h: m.h, a: m.a, s: m.s, cur: [r.pH, r.pD, r.pA], curO25: r.o25, lh, la, H: f(m.h), A: f(m.a) });
      });
    });
    // tous les matchs européens (pour l'apprentissage chronologique côté Python)
    const train = all.filter(x => x.m.s).map(({lg, m}) => ({ lg, d: m.d, h: m.h, a: m.a, s: m.s }));
    return { recs, train, clubs: Object.fromEntries(Object.entries(clubs).map(([k,t]) => [k, { country: t.country, dom: t.dom }])), coef };
  });
  require('fs').writeFileSync(out, JSON.stringify(res));
  console.log('matchs évalués', res.recs.length, '· matchs européens joués', res.train.length);
  await b.close();
})();
