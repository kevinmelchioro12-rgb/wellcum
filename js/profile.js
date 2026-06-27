/* ============================================================
   WELLCUM — Big Five / OCEAN psychometric profile
   Public-domain IPIP Big-Five Factor Markers (50 items, Goldberg 1992)
   Same framework family as IPIP-NEO and BFI-2.
   Vanilla JS, no dependencies. 100% client-side.
   ============================================================ */
(() => {
  'use strict';

  const root = document.getElementById('assessment');
  if (!root) return;

  const lang = (document.documentElement.lang || 'it').slice(0, 2);
  const STORE = 'wc_bigfive_v1';

  /* ---------- Trait order shown to the user (OCEAN) ---------- */
  const DOMAINS = ['O', 'C', 'E', 'A', 'N'];

  /* ---------- IPIP-50 item bank ----------------------------------
     d   = trait (O/C/E/A/N)
     key = +1 positively keyed · -1 reverse-scored
     t   = statement text per language
     Order follows the standard IPIP administration (E,A,C,N,O cycle).
  ---------------------------------------------------------------- */
  const ITEMS = [
    { d: 'E', key: 1,  t: { it: "Sono l'anima della festa.",                            en: 'I am the life of the party.',                           de: 'Ich bin das Leben jeder Party.' } },
    { d: 'A', key: -1, t: { it: 'Mi importa poco degli altri.',                          en: 'I feel little concern for others.',                     de: 'Die Sorgen anderer kümmern mich wenig.' } },
    { d: 'C', key: 1,  t: { it: 'Sono sempre preparato.',                                en: 'I am always prepared.',                                 de: 'Ich bin immer vorbereitet.' } },
    { d: 'N', key: 1,  t: { it: 'Mi stresso facilmente.',                                en: 'I get stressed out easily.',                            de: 'Ich gerate leicht unter Stress.' } },
    { d: 'O', key: 1,  t: { it: 'Ho un vocabolario ricco.',                              en: 'I have a rich vocabulary.',                             de: 'Ich verfüge über einen großen Wortschatz.' } },
    { d: 'E', key: -1, t: { it: 'Non parlo molto.',                                      en: "I don't talk a lot.",                                   de: 'Ich rede nicht viel.' } },
    { d: 'A', key: 1,  t: { it: 'Mi interessano le persone.',                            en: 'I am interested in people.',                            de: 'Ich interessiere mich für andere Menschen.' } },
    { d: 'C', key: -1, t: { it: 'Lascio le mie cose in giro.',                           en: 'I leave my belongings around.',                         de: 'Ich lasse meine Sachen herumliegen.' } },
    { d: 'N', key: -1, t: { it: 'Sono rilassato la maggior parte del tempo.',            en: 'I am relaxed most of the time.',                        de: 'Ich bin die meiste Zeit entspannt.' } },
    { d: 'O', key: -1, t: { it: "Faccio fatica a comprendere le idee astratte.",         en: 'I have difficulty understanding abstract ideas.',       de: 'Ich habe Schwierigkeiten, abstrakte Ideen zu verstehen.' } },
    { d: 'E', key: 1,  t: { it: 'Mi sento a mio agio tra la gente.',                     en: 'I feel comfortable around people.',                     de: 'Ich fühle mich in Gesellschaft anderer wohl.' } },
    { d: 'A', key: -1, t: { it: 'Insulto le persone.',                                   en: 'I insult people.',                                      de: 'Ich beleidige andere.' } },
    { d: 'C', key: 1,  t: { it: 'Presto attenzione ai dettagli.',                        en: 'I pay attention to details.',                           de: 'Ich achte auf Details.' } },
    { d: 'N', key: 1,  t: { it: 'Mi preoccupo delle cose.',                              en: 'I worry about things.',                                 de: 'Ich mache mir Sorgen um Dinge.' } },
    { d: 'O', key: 1,  t: { it: 'Ho una vivida immaginazione.',                          en: 'I have a vivid imagination.',                           de: 'Ich habe eine lebhafte Fantasie.' } },
    { d: 'E', key: -1, t: { it: 'Resto in disparte.',                                    en: 'I keep in the background.',                             de: 'Ich halte mich im Hintergrund.' } },
    { d: 'A', key: 1,  t: { it: 'Comprendo i sentimenti degli altri.',                   en: "I sympathize with others' feelings.",                   de: 'Ich fühle mit den Gefühlen anderer mit.' } },
    { d: 'C', key: -1, t: { it: 'Combino pasticci.',                                     en: 'I make a mess of things.',                              de: 'Ich richte oft ein Durcheinander an.' } },
    { d: 'N', key: -1, t: { it: 'Raramente mi sento giù.',                               en: 'I seldom feel blue.',                                   de: 'Ich bin selten niedergeschlagen.' } },
    { d: 'O', key: -1, t: { it: 'Non mi interessano le idee astratte.',                  en: 'I am not interested in abstract ideas.',                de: 'Abstrakte Ideen interessieren mich nicht.' } },
    { d: 'E', key: 1,  t: { it: 'Avvio le conversazioni.',                               en: 'I start conversations.',                                de: 'Ich beginne Gespräche.' } },
    { d: 'A', key: -1, t: { it: 'Non mi interessano i problemi degli altri.',            en: "I am not interested in other people's problems.",       de: 'Die Probleme anderer interessieren mich nicht.' } },
    { d: 'C', key: 1,  t: { it: 'Sbrigo subito le faccende.',                            en: 'I get chores done right away.',                         de: 'Ich erledige Aufgaben sofort.' } },
    { d: 'N', key: 1,  t: { it: 'Mi lascio turbare facilmente.',                         en: 'I am easily disturbed.',                                de: 'Ich bin leicht aus der Fassung zu bringen.' } },
    { d: 'O', key: 1,  t: { it: 'Ho ottime idee.',                                       en: 'I have excellent ideas.',                               de: 'Ich habe ausgezeichnete Ideen.' } },
    { d: 'E', key: -1, t: { it: 'Ho poco da dire.',                                      en: 'I have little to say.',                                 de: 'Ich habe wenig zu sagen.' } },
    { d: 'A', key: 1,  t: { it: 'Ho un cuore tenero.',                                   en: 'I have a soft heart.',                                  de: 'Ich habe ein weiches Herz.' } },
    { d: 'C', key: -1, t: { it: 'Dimentico spesso di rimettere le cose al loro posto.',  en: 'I often forget to put things back in their proper place.', de: 'Ich vergesse oft, Dinge an ihren Platz zurückzulegen.' } },
    { d: 'N', key: 1,  t: { it: 'Mi altero facilmente.',                                 en: 'I get upset easily.',                                   de: 'Ich rege mich leicht auf.' } },
    { d: 'O', key: -1, t: { it: 'Non ho molta immaginazione.',                           en: 'I do not have a good imagination.',                     de: 'Ich habe keine gute Fantasie.' } },
    { d: 'E', key: 1,  t: { it: 'Alle feste parlo con molte persone diverse.',           en: 'I talk to a lot of different people at parties.',       de: 'Ich rede auf Partys mit vielen verschiedenen Menschen.' } },
    { d: 'A', key: -1, t: { it: 'Non mi interessano davvero gli altri.',                 en: 'I am not really interested in others.',                 de: 'Andere interessieren mich nicht wirklich.' } },
    { d: 'C', key: 1,  t: { it: "Amo l'ordine.",                                         en: 'I like order.',                                         de: 'Ich mag Ordnung.' } },
    { d: 'N', key: 1,  t: { it: 'Cambio spesso umore.',                                  en: 'I change my mood a lot.',                               de: 'Meine Stimmung wechselt häufig.' } },
    { d: 'O', key: 1,  t: { it: 'Capisco le cose velocemente.',                          en: 'I am quick to understand things.',                      de: 'Ich begreife Dinge schnell.' } },
    { d: 'E', key: -1, t: { it: "Non amo attirare l'attenzione su di me.",               en: "I don't like to draw attention to myself.",             de: 'Ich ziehe nicht gern Aufmerksamkeit auf mich.' } },
    { d: 'A', key: 1,  t: { it: 'Mi prendo del tempo per gli altri.',                    en: 'I take time out for others.',                           de: 'Ich nehme mir Zeit für andere.' } },
    { d: 'C', key: -1, t: { it: 'Mi sottraggo ai miei doveri.',                          en: 'I shirk my duties.',                                    de: 'Ich drücke mich vor meinen Pflichten.' } },
    { d: 'N', key: 1,  t: { it: "Ho frequenti sbalzi d'umore.",                          en: 'I have frequent mood swings.',                          de: 'Ich habe häufige Stimmungsschwankungen.' } },
    { d: 'O', key: 1,  t: { it: 'Uso parole difficili.',                                 en: 'I use difficult words.',                                de: 'Ich benutze schwierige Wörter.' } },
    { d: 'E', key: 1,  t: { it: "Non mi dispiace essere al centro dell'attenzione.",     en: "I don't mind being the center of attention.",           de: 'Es macht mir nichts aus, im Mittelpunkt zu stehen.' } },
    { d: 'A', key: 1,  t: { it: 'Percepisco le emozioni degli altri.',                   en: "I feel others' emotions.",                              de: 'Ich spüre die Gefühle anderer.' } },
    { d: 'C', key: 1,  t: { it: 'Seguo un programma.',                                   en: 'I follow a schedule.',                                  de: 'Ich halte mich an einen Zeitplan.' } },
    { d: 'N', key: 1,  t: { it: 'Mi irrito facilmente.',                                 en: 'I get irritated easily.',                               de: 'Ich werde leicht gereizt.' } },
    { d: 'O', key: 1,  t: { it: 'Dedico tempo a riflettere sulle cose.',                 en: 'I spend time reflecting on things.',                    de: 'Ich denke gern über Dinge nach.' } },
    { d: 'E', key: -1, t: { it: 'Sono silenzioso con gli sconosciuti.',                  en: 'I am quiet around strangers.',                          de: 'Ich bin still, wenn ich Fremde um mich habe.' } },
    { d: 'A', key: 1,  t: { it: 'Metto le persone a proprio agio.',                      en: 'I make people feel at ease.',                           de: 'Ich gebe anderen ein Gefühl von Geborgenheit.' } },
    { d: 'C', key: 1,  t: { it: 'Sono meticoloso nel mio lavoro.',                       en: 'I am exacting in my work.',                             de: 'Ich bin in meiner Arbeit sehr genau.' } },
    { d: 'N', key: 1,  t: { it: 'Spesso mi sento giù di morale.',                        en: 'I often feel blue.',                                    de: 'Ich fühle mich oft niedergeschlagen.' } },
    { d: 'O', key: 1,  t: { it: 'Sono pieno di idee.',                                   en: 'I am full of ideas.',                                   de: 'Ich stecke voller Ideen.' } }
  ];

  /* ---------- Localised strings ---------- */
  const STR = {
    it: {
      scale: ['Del tutto in disaccordo', 'In disaccordo', 'Neutrale', "D'accordo", "Del tutto d'accordo"],
      bands: ['Molto basso', 'Basso', 'Nella media', 'Alto', 'Molto alto'],
      progress: (n, t) => `${n} / ${t} completate`,
      compute: 'Rivela il mio profilo',
      validate: (n) => `Rispondi a tutte le 50 affermazioni — ne ${n === 1 ? 'manca ancora 1' : 'mancano ancora ' + n}.`,
      resultsKicker: 'Risultato',
      resultsTitle: 'Il tuo profilo Big Five',
      resultsLead: 'I punteggi indicano dove ti collochi su ciascun tratto rispetto al punto medio della scala (50 = equilibrio). Descrivono tendenze, non un verdetto.',
      radarTitle: 'Sintesi OCEAN',
      copy: 'Copia il riepilogo',
      copied: 'Copiato negli appunti',
      redo: 'Rifai il test',
      scoreUnit: '/100',
      savedNote: 'Le tue risposte sono salvate solo in questo browser.',
      summaryHead: 'Profilo Big Five / OCEAN — Wellcum',
      domains: {
        O: { name: 'Apertura mentale', facets: 'Immaginazione · Curiosità · Estetica',
          high: 'Sei curioso, fantasioso e attratto da nuove idee, arte ed esperienze non convenzionali.',
          mid:  'Unisci curiosità e pragmatismo: aperto al nuovo ma con i piedi per terra.',
          low:  'Preferisci il concreto, il familiare e il collaudato rispetto all’astratto o sperimentale.' },
        C: { name: 'Coscienziosità', facets: 'Ordine · Disciplina · Affidabilità',
          high: 'Sei organizzato, affidabile e orientato agli obiettivi: pianifichi e porti a termine ciò che inizi.',
          mid:  'Sei abbastanza organizzato: sai essere disciplinato quando conta e flessibile per il resto.',
          low:  'Sei spontaneo e flessibile: preferisci improvvisare piuttosto che pianificare e strutturare.' },
        E: { name: 'Estroversione', facets: 'Socievolezza · Energia · Assertività',
          high: 'Sei socievole, energico e a tuo agio con gli altri: trai energia dal contatto sociale.',
          mid:  'Ami la compagnia ma apprezzi anche i tuoi spazi: socievole senza bisogno di stare al centro.',
          low:  'Sei riservato e riflessivo: preferisci ambienti tranquilli e cerchie ristrette.' },
        A: { name: 'Amicalità', facets: 'Empatia · Fiducia · Cooperazione',
          high: 'Sei caloroso, empatico e collaborativo, attento ai bisogni e ai sentimenti degli altri.',
          mid:  'Bilanci il calore verso gli altri con un sano riguardo per i tuoi interessi.',
          low:  'Sei diretto, competitivo e scettico: metti al primo posto franchezza e interesse personale.' },
        N: { name: 'Neuroticismo', facets: 'Ansia · Umore · Reattività allo stress',
          high: 'Vivi le emozioni con intensità e sei più sensibile a stress, preoccupazioni e sbalzi d’umore.',
          mid:  'Sei generalmente stabile: a volte senti lo stress ma ritrovi il tuo equilibrio.',
          low:  'Sei calmo, resiliente ed emotivamente stabile: difficilmente ti lasci scuotere.' }
      }
    },
    en: {
      scale: ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'],
      bands: ['Very low', 'Low', 'Average', 'High', 'Very high'],
      progress: (n, t) => `${n} / ${t} answered`,
      compute: 'Reveal my profile',
      validate: (n) => `Please answer all 50 statements — ${n === 1 ? '1 is' : n + ' are'} still missing.`,
      resultsKicker: 'Result',
      resultsTitle: 'Your Big Five profile',
      resultsLead: 'Scores show where you fall on each trait relative to the scale midpoint (50 = balanced). They describe tendencies, not a verdict.',
      radarTitle: 'OCEAN snapshot',
      copy: 'Copy summary',
      copied: 'Copied to clipboard',
      redo: 'Retake the test',
      scoreUnit: '/100',
      savedNote: 'Your answers are saved only in this browser.',
      summaryHead: 'Big Five / OCEAN profile — Wellcum',
      domains: {
        O: { name: 'Openness to Experience', facets: 'Imagination · Curiosity · Aesthetics',
          high: 'You are curious, imaginative and drawn to new ideas, art and unconventional experiences.',
          mid:  'You balance curiosity with pragmatism — open to the new but grounded in the familiar.',
          low:  'You prefer the concrete, familiar and proven over the abstract or experimental.' },
        C: { name: 'Conscientiousness', facets: 'Order · Discipline · Reliability',
          high: 'You are organised, dependable and goal-directed, planning ahead and following through.',
          mid:  'You are reasonably organised — disciplined when it matters, flexible otherwise.',
          low:  'You are spontaneous and flexible, preferring to improvise rather than plan and structure.' },
        E: { name: 'Extraversion', facets: 'Sociability · Energy · Assertiveness',
          high: 'You are outgoing, energetic and at ease with people, gaining energy from social contact.',
          mid:  'You enjoy company but also value time alone — sociable without needing the spotlight.',
          low:  'You are reserved and reflective, preferring calm settings and smaller, closer circles.' },
        A: { name: 'Agreeableness', facets: 'Compassion · Trust · Cooperation',
          high: "You are warm, empathetic and cooperative, attentive to others' needs and feelings.",
          mid:  'You balance warmth toward others with a healthy regard for your own interests.',
          low:  'You are direct, competitive and sceptical, putting candour and self-interest first.' },
        N: { name: 'Neuroticism', facets: 'Anxiety · Mood · Stress reactivity',
          high: 'You feel emotions intensely and are more sensitive to stress, worry and mood shifts.',
          mid:  'You are generally steady — you feel stress at times but recover your balance.',
          low:  'You are calm, resilient and emotionally stable, rarely rattled under pressure.' }
      }
    },
    de: {
      scale: ['Trifft gar nicht zu', 'Trifft eher nicht zu', 'Neutral', 'Trifft eher zu', 'Trifft voll zu'],
      bands: ['Sehr niedrig', 'Niedrig', 'Durchschnittlich', 'Hoch', 'Sehr hoch'],
      progress: (n, t) => `${n} / ${t} beantwortet`,
      compute: 'Mein Profil anzeigen',
      validate: (n) => `Bitte beantworte alle 50 Aussagen — es ${n === 1 ? 'fehlt noch 1' : 'fehlen noch ' + n}.`,
      resultsKicker: 'Ergebnis',
      resultsTitle: 'Dein Big-Five-Profil',
      resultsLead: 'Die Werte zeigen, wo du bei jedem Merkmal im Verhältnis zur Skalenmitte (50 = ausgeglichen) liegst. Sie beschreiben Tendenzen, kein Urteil.',
      radarTitle: 'OCEAN-Überblick',
      copy: 'Zusammenfassung kopieren',
      copied: 'In die Zwischenablage kopiert',
      redo: 'Test wiederholen',
      scoreUnit: '/100',
      savedNote: 'Deine Antworten werden nur in diesem Browser gespeichert.',
      summaryHead: 'Big-Five- / OCEAN-Profil — Wellcum',
      domains: {
        O: { name: 'Offenheit für Erfahrungen', facets: 'Fantasie · Neugier · Ästhetik',
          high: 'Du bist neugierig, fantasievoll und offen für neue Ideen, Kunst und unkonventionelle Erfahrungen.',
          mid:  'Du verbindest Neugier mit Pragmatismus – offen für Neues, aber mit Bodenhaftung.',
          low:  'Du bevorzugst das Konkrete, Vertraute und Bewährte gegenüber dem Abstrakten oder Experimentellen.' },
        C: { name: 'Gewissenhaftigkeit', facets: 'Ordnung · Disziplin · Verlässlichkeit',
          high: 'Du bist organisiert, verlässlich und zielstrebig: Du planst voraus und ziehst Dinge durch.',
          mid:  'Du bist recht organisiert – diszipliniert, wenn es darauf ankommt, und sonst flexibel.',
          low:  'Du bist spontan und flexibel und improvisierst lieber, als zu planen und zu strukturieren.' },
        E: { name: 'Extraversion', facets: 'Geselligkeit · Energie · Durchsetzung',
          high: 'Du bist kontaktfreudig, energiegeladen und im Umgang mit Menschen entspannt – sozialer Kontakt gibt dir Kraft.',
          mid:  'Du genießt Gesellschaft, schätzt aber auch Zeit für dich – gesellig, ohne im Mittelpunkt stehen zu müssen.',
          low:  'Du bist zurückhaltend und nachdenklich und bevorzugst ruhige Umgebungen und kleinere Kreise.' },
        A: { name: 'Verträglichkeit', facets: 'Mitgefühl · Vertrauen · Kooperation',
          high: 'Du bist warmherzig, einfühlsam und kooperativ und achtest auf die Bedürfnisse und Gefühle anderer.',
          mid:  'Du bringst Wärme gegenüber anderen mit einem gesunden Eigeninteresse in Einklang.',
          low:  'Du bist direkt, wettbewerbsorientiert und skeptisch und stellst Offenheit und Eigeninteresse voran.' },
        N: { name: 'Neurotizismus', facets: 'Ängstlichkeit · Stimmung · Stressreaktion',
          high: 'Du erlebst Gefühle intensiv und reagierst empfindlicher auf Stress, Sorgen und Stimmungsschwankungen.',
          mid:  'Du bist im Allgemeinen ausgeglichen: Stress spürst du zuweilen, findest aber dein Gleichgewicht wieder.',
          low:  'Du bist ruhig, belastbar und emotional stabil und lässt dich unter Druck kaum aus der Ruhe bringen.' }
      }
    }
  };

  const L = STR[lang] || STR.it;

  /* ---------- Elements ---------- */
  const quiz        = document.getElementById('quiz');
  const legendBox   = document.getElementById('scaleLegend');
  const controls    = document.getElementById('quizControls');
  const results     = document.getElementById('results');
  const progFill    = document.getElementById('qprogressFill');
  const progNum     = document.getElementById('qprogressNum');
  const total       = ITEMS.length;

  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  /* ---------- Scale legend ---------- */
  legendBox.className = 'scale-legend';
  legendBox.innerHTML = L.scale
    .map((s, i) => `<span><b>${i + 1}</b> ${esc(s)}</span>`)
    .join('');

  /* ---------- Build questions ---------- */
  quiz.innerHTML = ITEMS.map((it, i) => {
    const opts = L.scale.map((label, j) => {
      const v = j + 1;
      return `<label class="qopt" title="${esc(label)}">
        <input type="radio" name="q${i}" value="${v}" aria-label="${esc(label)}">
        <span><b>${v}</b><i>${esc(label)}</i></span>
      </label>`;
    }).join('');
    return `<div class="qcard" id="qc${i}" data-i="${i}">
      <div class="qcard__head">
        <span class="qcard__n">${String(i + 1).padStart(2, '0')}</span>
        <span class="qcard__text">${esc(it.t[lang] || it.t.it)}</span>
      </div>
      <div class="qopts">${opts}</div>
    </div>`;
  }).join('');

  /* ---------- Controls ---------- */
  controls.innerHTML =
    `<button type="button" class="btn btn--gold" id="computeBtn" data-magnetic>${esc(L.compute)}</button>
     <span class="assess__feedback" id="quizFeedback" role="status" aria-live="polite"></span>`;
  const computeBtn = document.getElementById('computeBtn');
  const feedback   = document.getElementById('quizFeedback');

  /* ---------- State + persistence ---------- */
  const answers = new Array(total).fill(null);

  function answeredCount() {
    return answers.reduce((n, v) => n + (v ? 1 : 0), 0);
  }
  function updateProgress() {
    const n = answeredCount();
    progNum.textContent = L.progress(n, total);
    progFill.style.width = (n / total) * 100 + '%';
  }
  function save(done) {
    try { localStorage.setItem(STORE, JSON.stringify({ a: answers, done: !!done, lang })); } catch (e) {}
  }
  function restore() {
    let data;
    try { data = JSON.parse(localStorage.getItem(STORE) || 'null'); } catch (e) { data = null; }
    if (!data || !Array.isArray(data.a)) return false;
    data.a.forEach((v, i) => {
      if (!v || i >= total) return;
      const input = quiz.querySelector(`input[name="q${i}"][value="${v}"]`);
      if (input) { input.checked = true; answers[i] = v; }
    });
    updateProgress();
    return !!data.done && answeredCount() === total;
  }

  quiz.addEventListener('change', (e) => {
    const input = e.target.closest('input[type="radio"]');
    if (!input) return;
    const i = +input.name.slice(1);
    answers[i] = +input.value;
    document.getElementById('qc' + i)?.classList.remove('is-missing');
    feedback.textContent = '';
    updateProgress();
    save(false);
  });

  /* ---------- Scoring ---------- */
  function score() {
    const sum = { O: 0, C: 0, E: 0, A: 0, N: 0 };
    ITEMS.forEach((it, i) => {
      const raw = answers[i];
      sum[it.d] += it.key === -1 ? (6 - raw) : raw;
    });
    const out = {};
    DOMAINS.forEach((d) => {
      const mean = sum[d] / 10;            // 10 items per trait, mean 1..5
      const pct = Math.round((mean - 1) / 4 * 100);
      const band = pct < 20 ? 0 : pct < 40 ? 1 : pct < 60 ? 2 : pct < 80 ? 3 : 4;
      out[d] = { pct, band };
    });
    return out;
  }
  function descFor(d, band) {
    const dm = L.domains[d];
    return band >= 3 ? dm.high : band <= 1 ? dm.low : dm.mid;
  }

  /* ---------- OCEAN radar (inline SVG) ---------- */
  function radarSVG(s) {
    const cs = getComputedStyle(document.body);
    const gold  = (cs.getPropertyValue('--gold')  || '#e40078').trim();
    const gold2 = (cs.getPropertyValue('--gold-2') || '#ff4da6').trim();
    const grid  = (cs.getPropertyValue('--line')  || 'rgba(228,0,120,.2)').trim();
    const ink   = (cs.getPropertyValue('--ink-mute') || '#9b8492').trim();
    const cx = 180, cy = 180, R = 120;
    const ax = DOMAINS.map((d, i) => ({ d, a: (-90 + i * 72) * Math.PI / 180 }));
    const pt = (r, a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    const poly = (r) => ax.map((o) => pt(r, o.a).map((n) => n.toFixed(1)).join(',')).join(' ');

    let svg = `<svg class="radar" viewBox="0 0 360 360" role="img" aria-label="${esc(L.radarTitle)}">`;
    [0.25, 0.5, 0.75, 1].forEach((f) => {
      svg += `<polygon points="${poly(R * f)}" fill="none" stroke="${grid}" stroke-width="1"/>`;
    });
    ax.forEach((o) => {
      const [x, y] = pt(R, o.a);
      svg += `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="${grid}" stroke-width="1"/>`;
    });
    const dpts = ax.map((o) => pt(R * s[o.d].pct / 100, o.a).map((n) => n.toFixed(1)).join(',')).join(' ');
    svg += `<polygon points="${dpts}" fill="${gold}" fill-opacity="0.20" stroke="${gold2}" stroke-width="2" stroke-linejoin="round"/>`;
    ax.forEach((o) => {
      const [x, y] = pt(R * s[o.d].pct / 100, o.a);
      svg += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.6" fill="${gold2}"/>`;
    });
    ax.forEach((o) => {
      const [lx, ly] = pt(R + 26, o.a);
      svg += `<text x="${lx.toFixed(1)}" y="${(ly - 5).toFixed(1)}" fill="${gold}" font-family="Jost,sans-serif" font-size="15" font-weight="600" text-anchor="middle">${o.d}</text>`;
      svg += `<text x="${lx.toFixed(1)}" y="${(ly + 11).toFixed(1)}" fill="${ink}" font-family="Jost,sans-serif" font-size="11" text-anchor="middle">${s[o.d].pct}</text>`;
    });
    return svg + '</svg>';
  }

  /* ---------- Render results ---------- */
  function showResults(s) {
    const rows = DOMAINS.map((d) => {
      const r = s[d];
      const dm = L.domains[d];
      return `<div class="domain">
        <div class="domain__top">
          <div class="domain__name">${esc(dm.name)} <small>${esc(d)} · ${esc(dm.facets)}</small></div>
          <div class="domain__score">${r.pct}<small>${esc(L.scoreUnit)}</small></div>
        </div>
        <div class="domain__bar"><div class="domain__fill" data-pct="${r.pct}"></div></div>
        <div class="domain__band">${esc(L.bands[r.band])}</div>
        <div class="domain__desc">${esc(descFor(d, r.band))}</div>
      </div>`;
    }).join('');

    results.innerHTML =
      `<div class="results__head">
        <p class="eyebrow">${esc(L.resultsKicker)}</p>
        <h3 class="results__title">${esc(L.resultsTitle)}</h3>
        <p class="results__lead">${esc(L.resultsLead)}</p>
      </div>
      <div class="result-grid">
        <div class="radar-wrap">${radarSVG(s)}<p class="radar-cap">${esc(L.radarTitle)}</p></div>
        <div class="result-domains">${rows}</div>
      </div>
      <div class="results__actions">
        <button type="button" class="btn btn--gold" id="copyBtn" data-magnetic>${esc(L.copy)}</button>
        <button type="button" class="btn btn--ghost" id="redoBtn" data-magnetic>${esc(L.redo)}</button>
      </div>`;

    results.classList.add('is-on');
    requestAnimationFrame(() => {
      results.querySelectorAll('.domain__fill').forEach((f) => { f.style.width = f.dataset.pct + '%'; });
    });

    document.getElementById('copyBtn').addEventListener('click', (e) => copySummary(s, e.currentTarget));
    document.getElementById('redoBtn').addEventListener('click', redo);
  }

  function copySummary(s, btn) {
    const lines = [L.summaryHead, ''];
    DOMAINS.forEach((d) => {
      const r = s[d];
      lines.push(`${d} · ${L.domains[d].name}: ${r.pct}${L.scoreUnit} (${L.bands[r.band]})`);
    });
    const text = lines.join('\n');
    const done = () => { const old = btn.textContent; btn.textContent = L.copied; setTimeout(() => { btn.textContent = old; }, 1800); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(() => fallbackCopy(text, done));
    } else { fallbackCopy(text, done); }
  }
  function fallbackCopy(text, done) {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); done(); } catch (e) {}
    document.body.removeChild(ta);
  }

  function redo() {
    answers.fill(null);
    quiz.querySelectorAll('input[type="radio"]:checked').forEach((i) => { i.checked = false; });
    quiz.querySelectorAll('.is-missing').forEach((q) => q.classList.remove('is-missing'));
    results.classList.remove('is-on');
    results.innerHTML = '';
    feedback.textContent = '';
    try { localStorage.removeItem(STORE); } catch (e) {}
    updateProgress();
    document.getElementById('assessment').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ---------- Compute ---------- */
  computeBtn.addEventListener('click', () => {
    const missing = [];
    answers.forEach((v, i) => { if (!v) missing.push(i); });
    if (missing.length) {
      quiz.querySelectorAll('.is-missing').forEach((q) => q.classList.remove('is-missing'));
      missing.forEach((i) => document.getElementById('qc' + i)?.classList.add('is-missing'));
      feedback.textContent = L.validate(missing.length);
      document.getElementById('qc' + missing[0])?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    feedback.textContent = '';
    const s = score();
    save(true);
    showResults(s);
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  /* ---------- Init ---------- */
  updateProgress();
  if (restore()) {
    showResults(score());
  }
})();
