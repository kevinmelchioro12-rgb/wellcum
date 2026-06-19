/* ============================================================
   WELLCUM — interactions & visual effects
   Vanilla JS, no dependencies.
   ============================================================ */
(() => {
  'use strict';
  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine   = matchMedia('(hover:hover) and (pointer:fine)').matches;

  /* ---------- Footer year ---------- */
  const yEl = $('#year'); if (yEl) yEl.textContent = new Date().getFullYear();

  /* ---------- Hero video (keep opening videos; pick mobile source) ---------- */
  const hv = $('#heroVideo');
  if (hv) {
    if (innerWidth < 760 && hv.dataset.mobile) {
      const s = hv.querySelector('source');
      if (s) { s.src = hv.dataset.mobile; hv.load(); }
    }
    const tryPlay = () => hv.play().catch(() => {});
    hv.addEventListener('loadeddata', tryPlay); tryPlay();
  }

  /* ---------- Age gate ---------- */
  const gate = $('#agegate');
  if (gate) {
    if (sessionStorage.getItem('wc_age_ok') === '1') {
      gate.classList.add('is-hidden');
    } else {
      document.body.style.overflow = 'hidden';
    }
    $('#age-yes')?.addEventListener('click', () => {
      sessionStorage.setItem('wc_age_ok', '1');
      gate.classList.add('is-hidden');
      document.body.style.overflow = '';
      startHero();
    });
  }

  /* ---------- Preloader ---------- */
  window.addEventListener('load', () => {
    const pre = $('#preloader');
    setTimeout(() => {
      pre?.classList.add('is-done');
      if (!gate || sessionStorage.getItem('wc_age_ok') === '1') startHero();
    }, 650);
  });

  let heroStarted = false;
  function startHero() {
    if (heroStarted) return; heroStarted = true;
    $$('.hero__title .line').forEach((l, i) => {
      setTimeout(() => l.classList.add('is-in'), 120 + i * 140);
    });
  }

  /* ---------- Custom cursor ---------- */
  if (fine) {
    const ring = $('.cursor'), dot = $('.cursor-dot');
    let rx = innerWidth / 2, ry = innerHeight / 2, dx = rx, dy = ry;
    addEventListener('mousemove', e => {
      dx = e.clientX; dy = e.clientY;
      dot.style.transform = `translate(${dx}px,${dy}px) translate(-50%,-50%)`;
    });
    const loop = () => {
      rx += (dx - rx) * 0.18; ry += (dy - ry) * 0.18;
      ring.style.transform = `translate(${rx}px,${ry}px) translate(-50%,-50%)`;
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
    $$('a, button, summary, [data-magnetic], .qa summary').forEach(el => {
      el.addEventListener('mouseenter', () => ring.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => ring.classList.remove('is-hover'));
    });
  }

  /* ---------- Nav scroll + mobile ---------- */
  const nav = $('#nav'), burger = $('#burger'), prog = $('#progress');
  const onScroll = () => {
    nav.classList.toggle('is-scrolled', scrollY > 40);
    if (prog) { const h = document.documentElement.scrollHeight - innerHeight; prog.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + '%'; }
  };
  onScroll(); addEventListener('scroll', onScroll, { passive: true });
  burger?.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    burger.setAttribute('aria-expanded', open);
  });
  $$('#navLinks a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('is-open'); burger?.setAttribute('aria-expanded', false);
  }));

  /* ---------- Reveal on scroll ---------- */
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  $$('[data-reveal]').forEach(el => io.observe(el));

  /* ---------- Counters ---------- */
  const fmt = n => n.toLocaleString('it-IT');
  const countIO = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, target = +el.dataset.count, suffix = el.dataset.suffix || '';
      if (reduce) { el.textContent = fmt(target) + suffix; countIO.unobserve(el); return; }
      const dur = 1600, t0 = performance.now();
      const tick = (t) => {
        const p = Math.min((t - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(Math.round(target * eased)) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      countIO.unobserve(el);
    });
  }, { threshold: 0.5 });
  $$('[data-count]').forEach(el => countIO.observe(el));

  /* ---------- Parallax ---------- */
  const para = $$('[data-parallax]');
  if (para.length && !reduce) {
    let ticking = false;
    const upd = () => {
      const vh = innerHeight;
      para.forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        const prog = (r.top + r.height / 2 - vh / 2) / vh;
        const img = el.querySelector('img') || el;
        img.style.transform = `translateY(${prog * -26}px) scale(1.06)`;
      });
      ticking = false;
    };
    addEventListener('scroll', () => { if (!ticking) { requestAnimationFrame(upd); ticking = true; } }, { passive: true });
    upd();
  }

  /* ---------- FAQ accordion (smooth, single-open) ---------- */
  $$('.qa').forEach(qa => {
    const sum = qa.querySelector('summary');
    const body = qa.querySelector('.qa__a');
    sum.addEventListener('click', (e) => {
      e.preventDefault();
      const isOpen = qa.hasAttribute('open');
      if (!isOpen) {
        $$('.qa[open]').forEach(o => { if (o !== qa) closeQa(o); });
        qa.setAttribute('open', '');
        if (reduce) return;
        body.animate(
          [{ height: '0px', opacity: 0 }, { height: body.scrollHeight + 'px', opacity: 1 }],
          { duration: 420, easing: 'cubic-bezier(.22,.61,.36,1)' }
        );
      } else {
        closeQa(qa);
      }
    });
    function closeQa(node) {
      const b = node.querySelector('.qa__a');
      if (reduce) { node.removeAttribute('open'); return; }
      const a = b.animate(
        [{ height: b.scrollHeight + 'px', opacity: 1 }, { height: '0px', opacity: 0 }],
        { duration: 320, easing: 'cubic-bezier(.22,.61,.36,1)' }
      );
      a.onfinish = () => node.removeAttribute('open');
    }
  });

  /* ---------- Magnetic buttons ---------- */
  if (fine && !reduce) {
    $$('[data-magnetic]').forEach(el => {
      const strength = 0.28;
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const mx = e.clientX - (r.left + r.width / 2);
        const my = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${mx * strength}px, ${my * strength}px)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  /* ============================================================
     WebGL HERO — flowing champagne/wine gradient
     ============================================================ */
  function initGL() {
    const canvas = $('#gl');
    if (!canvas) return;
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) { canvas.style.display = 'none'; return; }

    const vert = `
      attribute vec2 p; void main(){ gl_Position = vec4(p,0.,1.); }`;

    const frag = `
      precision highp float;
      uniform vec2  u_res;
      uniform float u_time;
      uniform vec2  u_mouse;

      // 2D simplex noise (Ashima Arts)
      vec3 mod289(vec3 x){ return x - floor(x*(1./289.))*289.; }
      vec2 mod289(vec2 x){ return x - floor(x*(1./289.))*289.; }
      vec3 permute(vec3 x){ return mod289(((x*34.)+1.)*x); }
      float snoise(vec2 v){
        const vec4 C = vec4(0.211324865,0.366025403,-0.577350269,0.024390243);
        vec2 i = floor(v + dot(v, C.yy));
        vec2 x0 = v - i + dot(i, C.xx);
        vec2 i1 = (x0.x > x0.y) ? vec2(1.,0.) : vec2(0.,1.);
        vec4 x12 = x0.xyxy + C.xxzz; x12.xy -= i1;
        i = mod289(i);
        vec3 perm = permute( permute( i.y + vec3(0., i1.y, 1.)) + i.x + vec3(0., i1.x, 1.));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.);
        m = m*m; m = m*m;
        vec3 x = 2.*fract(perm * C.www) - 1.;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291 - 0.85373472 * (a0*a0 + h*h);
        vec3 g;
        g.x = a0.x*x0.x + h.x*x0.y;
        g.yz = a0.yz*x12.xz + h.yz*x12.yw;
        return 130.*dot(m, g);
      }
      float fbm(vec2 p){
        float s=0., a=0.5;
        for(int i=0;i<5;i++){ s += a*snoise(p); p*=2.02; a*=0.5; }
        return s;
      }
      void main(){
        vec2 uv = gl_FragCoord.xy / u_res.xy;
        vec2 p = (gl_FragCoord.xy - 0.5*u_res.xy) / u_res.y;
        float t = u_time * 0.045;
        vec2 mo = (u_mouse - 0.5) * 0.5;

        // domain-warped flow
        vec2 q = vec2(fbm(p*1.6 + t), fbm(p*1.6 - t + 4.0));
        vec2 r = vec2(fbm(p*1.6 + 1.7*q + mo + t*0.7),
                      fbm(p*1.6 + 1.7*q - t*0.5));
        float f = fbm(p*1.6 + 2.0*r);

        vec3 dark  = vec3(0.040,0.024,0.035);
        vec3 wine  = vec3(0.290,0.050,0.180);
        vec3 gold  = vec3(0.894,0.000,0.471);
        vec3 lite  = vec3(1.000,0.667,0.840);

        vec3 col = mix(dark, wine, smoothstep(-0.4,0.5,f));
        col = mix(col, gold, smoothstep(0.25,0.95,r.x*0.9+0.4));
        col += lite * pow(max(0.,f),3.0) * 0.30;

        // soft vignette toward edges
        float vig = smoothstep(1.25,0.25, length(p));
        col *= 0.55 + 0.45*vig;
        col *= 0.92;
        gl_FragColor = vec4(col,1.0);
      }`;

    const compile = (type, src) => {
      const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh);
      if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) { console.warn(gl.getShaderInfoLog(sh)); return null; }
      return sh;
    };
    const vs = compile(gl.VERTEX_SHADER, vert), fs = compile(gl.FRAGMENT_SHADER, frag);
    if (!vs || !fs) { canvas.style.display = 'none'; return; }
    const prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { canvas.style.display = 'none'; return; }
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 3,-1, -1,3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, 'p');
    gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    const uRes = gl.getUniformLocation(prog, 'u_res');
    const uTime = gl.getUniformLocation(prog, 'u_time');
    const uMouse = gl.getUniformLocation(prog, 'u_mouse');
    let mouse = [0.5, 0.5], tmouse = [0.5, 0.5];

    const dpr = Math.min(devicePixelRatio || 1, 1.6);
    const resize = () => {
      const w = canvas.clientWidth, h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };
    resize(); addEventListener('resize', resize);
    addEventListener('mousemove', e => { tmouse = [e.clientX / innerWidth, 1 - e.clientY / innerHeight]; });

    const hero = $('#hero');
    let running = true;
    const heroIO = new IntersectionObserver(es => { running = es[0].isIntersecting; if (running) raf(); }, { threshold: 0 });
    if (hero) heroIO.observe(hero);

    const t0 = performance.now();
    let rafId = null;
    const render = (now) => {
      rafId = null;
      mouse[0] += (tmouse[0] - mouse[0]) * 0.04;
      mouse[1] += (tmouse[1] - mouse[1]) * 0.04;
      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uTime, reduce ? 8.0 : (now - t0) / 1000);
      gl.uniform2f(uMouse, mouse[0], mouse[1]);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      if (running && !reduce) raf();
    };
    const raf = () => { if (rafId == null) rafId = requestAnimationFrame(render); };
    raf();
    if (reduce) render(performance.now());
  }
  initGL();
})();
