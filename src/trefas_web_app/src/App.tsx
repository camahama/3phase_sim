import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  angle,
  calculateLineAndNeutralCurrents,
  type Complex,
  magnitude,
  resistiveImpedanceFromPower,
} from "./core/physics";

const V_PHASE_RMS = 230;
const WAVE_SAMPLES = 220;
const WAVE_CYCLES = 1.25;
const GRID_MAX_AMP = 20;
const CURRENT_TICKS_A = [5, 10, 15, 20];
const PERIOD_MS = 20;
const MAX_PHASE_POWER_W = 2000;
const MAX_DELTA_POWER_W = 3000;
const IMAGE_URL = "/3fas.jpg";
const ROTATION_HZ = 0.3;
const ROTATION_OMEGA = 2 * Math.PI * ROTATION_HZ;

const LOAD_COLORS = {
  p1: "#ff4d4d",
  p2: "#4ddc6f",
  p3: "#4f8fff",
  p12: "#ffd84d",
  p23: "#ff5ed4",
  p31: "#ff9b3d",
};

type Language = "en" | "sv";

const UI_TEXT: Record<Language, {
  kicker: string;
  title: string;
  intro: string;
  phaseLoadsHeading: string;
  lineLoadsHeading: string;
  p1Suffix: string;
  p2Suffix: string;
  p3Suffix: string;
  p12Suffix: string;
  p23Suffix: string;
  p31Suffix: string;
  resetButton: string;
  resultingCurrents: string;
  linkedHeading: string;
  startTime: string;
  stopTime: string;
  t0: string;
  ampUnit: string;
  msUnit: string;
  imageAlt: string;
  linkedAriaLabel: string;
  languageToggle: string;
}> = {
  en: {
    kicker: "Trefas Web Prototype",
    title: "Structured Three-Phase Simulator",
    intro:
      "New web-native shell using a pure TypeScript physics engine. Start by adjusting active loads and verify current phasors.",
    phaseLoadsHeading: "Phase Loads (Y)",
    lineLoadsHeading: "Line Loads (Delta)",
    p1Suffix: " (L1-N)",
    p2Suffix: " (L2-N)",
    p3Suffix: " (L3-N)",
    p12Suffix: " (L1-L2)",
    p23Suffix: " (L2-L3)",
    p31Suffix: " (L3-L1)",
    resetButton: "Reset (all P=0)",
    resultingCurrents: "Resulting currents",
    linkedHeading: "Phasor + Waveform (Linked)",
    startTime: "Start time",
    stopTime: "Stop time (t=0)",
    t0: "t=0",
    ampUnit: "A",
    msUnit: "ms",
    imageAlt: "Three-phase circuit diagram",
    linkedAriaLabel: "Linked phasor and waveform diagrams",
    languageToggle: "Svenska",
  },
  sv: {
    kicker: "Trefas Web Prototyp",
    title: "Strukturerad trefassimulator",
    intro:
      "Ny webbaserad version med ren TypeScript-fysikmotor. Justera lasterna och kontrollera str\u00f6mfasorerna.",
    phaseLoadsHeading: "Faslaster (Y)",
    lineLoadsHeading: "Linjelaster (Delta)",
    p1Suffix: " (L1-N)",
    p2Suffix: " (L2-N)",
    p3Suffix: " (L3-N)",
    p12Suffix: " (L1-L2)",
    p23Suffix: " (L2-L3)",
    p31Suffix: " (L3-L1)",
    resetButton: "Nollst\u00e4ll (alla P=0)",
    resultingCurrents: "Resulterande str\u00f6mmar",
    linkedHeading: "Fasor + v\u00e5gform (l\u00e4nkad)",
    startTime: "Starta tid",
    stopTime: "Stoppa tid (t=0)",
    t0: "t=0",
    ampUnit: "A",
    msUnit: "ms",
    imageAlt: "Kopplingsschema trefas",
    linkedAriaLabel: "L\u00e4nkade fasor- och v\u00e5gformsdiagram",
    languageToggle: "English",
  },
};

function formatDecimal(value: number, decimals: number, language: Language): string {
  const locale = language === "sv" ? "sv-SE" : "en-US";
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

function ampLabel(value: number, text: (typeof UI_TEXT)[Language], language: Language): string {
  return `${formatDecimal(value, 2, language)} ${text.ampUnit}`;
}

function deg(rad: number): number {
  return (rad * 180) / Math.PI;
}

const FIXED_MAX_AMP = GRID_MAX_AMP;

export default function App() {
  const [language, setLanguage] = useState<Language>("en");
  const text = UI_TEXT[language];
  const [p1, setP1] = useState(0);
  const [p2, setP2] = useState(0);
  const [p3, setP3] = useState(0);
  const [p12, setP12] = useState(0);
  const [p23, setP23] = useState(0);
  const [p31, setP31] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [timePhase, setTimePhase] = useState(0);

  useEffect(() => {
    if (!isRunning) {
      return;
    }

    let rafId = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const dt = (now - last) / 1000;
      last = now;
      setTimePhase((prev) => {
        const next = prev + dt * ROTATION_OMEGA;
        return next % (2 * Math.PI);
      });
      rafId = requestAnimationFrame(tick);
    };

    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, [isRunning]);

  function handleRunToggle(): void {
    if (isRunning) {
      setIsRunning(false);
      setTimePhase(0);
      return;
    }
    setIsRunning(true);
  }

  const currents = useMemo(() => {
    const yImpedances: [Complex | null, Complex | null, Complex | null] = [
      resistiveImpedanceFromPower(p1, V_PHASE_RMS),
      resistiveImpedanceFromPower(p2, V_PHASE_RMS),
      resistiveImpedanceFromPower(p3, V_PHASE_RMS),
    ];

    const vLineRms = V_PHASE_RMS * Math.sqrt(3);
    const deltaImpedances: [Complex | null, Complex | null, Complex | null] = [
      resistiveImpedanceFromPower(p12, vLineRms),
      resistiveImpedanceFromPower(p23, vLineRms),
      resistiveImpedanceFromPower(p31, vLineRms),
    ];

    return calculateLineAndNeutralCurrents({
      yImpedances,
      deltaImpedances,
      voltageRms: V_PHASE_RMS,
    });
  }, [p1, p2, p3, p12, p23, p31]);

  const [i1, i2, i3] = currents.lineCurrents;
  const inNeutral = currents.neutralCurrent;

  function resetLoads(): void {
    setP1(0);
    setP2(0);
    setP3(0);
    setP12(0);
    setP23(0);
    setP31(0);
  }

  return (
    <main className="page">
      <section className="hero-card">
        <button
          type="button"
          className="lang-toggle-btn"
          onClick={() => setLanguage((prev) => (prev === "en" ? "sv" : "en"))}
        >
          {text.languageToggle}
        </button>
        <p className="kicker">{text.kicker}</p>
        <h1>{text.title}</h1>
        <p>{text.intro}</p>
      </section>

      <section className="panel-grid">
        <article className="panel panel-controls">
          <div className="controls-layout">
            <div>
              <h2>{text.phaseLoadsHeading}</h2>
              <LoadSlider label={<PowerLabel base="P" sub="1" suffix={text.p1Suffix} />} value={p1} onChange={setP1} max={MAX_PHASE_POWER_W} color={LOAD_COLORS.p1} />
              <LoadSlider label={<PowerLabel base="P" sub="2" suffix={text.p2Suffix} />} value={p2} onChange={setP2} max={MAX_PHASE_POWER_W} color={LOAD_COLORS.p2} />
              <LoadSlider label={<PowerLabel base="P" sub="3" suffix={text.p3Suffix} />} value={p3} onChange={setP3} max={MAX_PHASE_POWER_W} color={LOAD_COLORS.p3} />

              <h2>{text.lineLoadsHeading}</h2>
              <LoadSlider label={<PowerLabel base="P" sub="12" suffix={text.p12Suffix} />} value={p12} onChange={setP12} max={MAX_DELTA_POWER_W} color={LOAD_COLORS.p12} />
              <LoadSlider label={<PowerLabel base="P" sub="23" suffix={text.p23Suffix} />} value={p23} onChange={setP23} max={MAX_DELTA_POWER_W} color={LOAD_COLORS.p23} />
              <LoadSlider label={<PowerLabel base="P" sub="31" suffix={text.p31Suffix} />} value={p31} onChange={setP31} max={MAX_DELTA_POWER_W} color={LOAD_COLORS.p31} />
              <button type="button" className="reset-btn" onClick={resetLoads}>{text.resetButton}</button>

              <p className="scale-note">{text.resultingCurrents}</p>
              <div className="current-strip instrument-strip">
                <CurrentChip symbolBase="I" symbolSub="1" amp={magnitude(i1)} phaseDeg={deg(angle(i1))} text={text} language={language} />
                <CurrentChip symbolBase="I" symbolSub="2" amp={magnitude(i2)} phaseDeg={deg(angle(i2))} text={text} language={language} />
                <CurrentChip symbolBase="I" symbolSub="3" amp={magnitude(i3)} phaseDeg={deg(angle(i3))} text={text} language={language} />
                <CurrentChip symbolBase="I" symbolSub="N" amp={magnitude(inNeutral)} phaseDeg={deg(angle(inNeutral))} text={text} language={language} strong />
              </div>
            </div>

            <figure className="circuit-image-wrap">
              <img src={IMAGE_URL} alt={text.imageAlt} className="circuit-image" />
            </figure>
          </div>
        </article>

        <article className="panel panel-viz-combined">
          <h2>{text.linkedHeading}</h2>
          <LinkedDiagrams currents={[i1, i2, i3, inNeutral]} maxAmp={FIXED_MAX_AMP} timePhase={timePhase} text={text} />
          <div className="viz-controls">
            <button type="button" className="run-btn" onClick={handleRunToggle}>
              {isRunning ? text.stopTime : text.startTime}
            </button>
          </div>
        </article>
      </section>
    </main>
  );
}

function LoadSlider(props: {
  label: ReactNode;
  value: number;
  max: number;
  color: string;
  onChange: (v: number) => void;
}) {
  return (
    <label className="slider-row">
      <span className="symbol-wrap" style={{ color: props.color }}>{props.label}</span>
      <input
        type="range"
        min={0}
        max={props.max}
        step={10}
        value={props.value}
        style={{ accentColor: props.color }}
        onChange={(e) => props.onChange(Number(e.target.value))}
      />
      <strong style={{ color: props.color }}>{props.value.toFixed(0)} W</strong>
    </label>
  );
}

function PowerLabel(props: { base: string; sub: string; suffix?: string }) {
  return (
    <>
      <em>{props.base}</em>
      <sub>{props.sub}</sub>
      {props.suffix ?? ""}
    </>
  );
}

function vectorEnd(
  current: Complex,
  center: number,
  radius: number,
  maxAmp: number,
  phaseOffset = 0
): [number, number] {
  const amp = magnitude(current);
  const ang = angle(current) + phaseOffset;
  const r = (amp / maxAmp) * radius;
  return [center + r * Math.cos(ang), center - r * Math.sin(ang)];
}

function LinkedDiagrams(props: {
  currents: [Complex, Complex, Complex, Complex];
  maxAmp: number;
  timePhase: number;
  text: (typeof UI_TEXT)[Language];
}) {
  const pane = 340;
  const gap = 24;
  const width = pane * 2 + gap;
  const height = pane;

  const centerX = pane / 2;
  const centerY = pane / 2;
  const radius = 116;

  const waveOffsetX = pane + gap;
  const plotLeft = waveOffsetX + 36;
  const plotRight = waveOffsetX + pane - 12;
  const plotTop = 32;
  const plotBottom = pane - 32;
  const plotWidth = plotRight - plotLeft;
  const yScale = radius / props.maxAmp;

  const colors = ["#ff7b78", "#7ef0a4", "#7ec6ff", "#fff0ac"];
  const labels = [
    { base: "I", sub: "1" },
    { base: "I", sub: "2" },
    { base: "I", sub: "3" },
    { base: "I", sub: "N" },
  ];
  const markers = ["arrow-l1", "arrow-l2", "arrow-l3", "arrow-ln"];
  const scaleFractions = CURRENT_TICKS_A.map((tick) => tick / props.maxAmp);
  const yTicks = [-20, -15, -10, -5, 0, 5, 10, 15, 20];
  const xTicksMs = [0, 5, 10, 15, 20, 25];

  function waveformPath(current: Complex): string {
    const amp = magnitude(current);
    const phase = angle(current) + props.timePhase;
    const xScale = plotWidth / (WAVE_SAMPLES - 1);
    let path = "";
    for (let i = 0; i < WAVE_SAMPLES; i += 1) {
      const t = (i / (WAVE_SAMPLES - 1)) * (Math.PI * 2) * WAVE_CYCLES;
      const x = plotLeft + i * xScale;
      const y = centerY - amp * Math.sin(t + phase) * yScale;
      path += i === 0 ? `M ${x.toFixed(2)} ${y.toFixed(2)}` : ` L ${x.toFixed(2)} ${y.toFixed(2)}`;
    }
    return path;
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="viz-svg viz-linked" role="img" aria-label={props.text.linkedAriaLabel}>
      <defs>
        <marker id="arrow-l1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#ff7b78" />
        </marker>
        <marker id="arrow-l2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#7ef0a4" />
        </marker>
        <marker id="arrow-l3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#7ec6ff" />
        </marker>
        <marker id="arrow-ln" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#fff0ac" />
        </marker>
      </defs>

      {scaleFractions.map((fraction) => (
        <circle key={fraction} cx={centerX} cy={centerY} r={radius * fraction} className="phasor-grid" />
      ))}
      <line x1={centerX - radius} y1={centerY} x2={centerX + radius} y2={centerY} className="phasor-axis" />
      <line x1={centerX} y1={centerY - radius} x2={centerX} y2={centerY + radius} className="phasor-axis" />
      {CURRENT_TICKS_A.map((tick) => {
        const y = centerY - (tick / props.maxAmp) * radius;
        return (
          <g key={`tick-${tick}`}>
            <line x1={centerX - 4} y1={y} x2={centerX + 4} y2={y} className="phasor-axis" />
            <text x={centerX + 8} y={y + 4} className="viz-scale-label">{tick} {props.text.ampUnit}</text>
          </g>
        );
      })}

      <line x1={plotLeft} y1={plotTop} x2={plotLeft} y2={plotBottom} className="phasor-axis" />
      <line x1={plotLeft} y1={centerY} x2={plotRight} y2={centerY} className="phasor-axis" />
      {yTicks.map((tick) => {
        const y = centerY - (tick / props.maxAmp) * radius;
        return (
          <g key={`y-${tick}`}>
            <line x1={plotLeft} y1={y} x2={plotRight} y2={y} className="wave-grid" />
            <text x={waveOffsetX + 4} y={y + 4} className="viz-scale-label">{tick} {props.text.ampUnit}</text>
          </g>
        );
      })}
      {xTicksMs.map((tickMs) => {
        const x = plotLeft + (tickMs / (WAVE_CYCLES * PERIOD_MS)) * plotWidth;
        return (
          <g key={`x-${tickMs}`}>
            <line x1={x} y1={plotTop} x2={x} y2={plotBottom} className="wave-grid" />
            <text x={x - 10} y={height - 8} className="viz-scale-label">{tickMs} {props.text.msUnit}</text>
          </g>
        );
      })}

      {props.currents.map((current, idx) => {
        const [x2, y2] = vectorEnd(current, centerX, radius, props.maxAmp, props.timePhase);
        const t0y = centerY - magnitude(current) * Math.sin(angle(current) + props.timePhase) * yScale;
        return (
          <g key={`phase-${idx}`}>
            <line x1={x2} y1={y2} x2={plotLeft} y2={t0y} stroke={colors[idx]} className="phasor-dashed" />
            <line
              x1={centerX}
              y1={centerY}
              x2={x2}
              y2={y2}
              stroke={colors[idx]}
              strokeWidth={2}
              markerEnd={`url(#${markers[idx]})`}
            />
            <text x={x2 + 6} y={y2 - 6} fill={colors[idx]} className="viz-label">
              <tspan fontStyle="italic">{labels[idx].base}</tspan>
              <tspan baselineShift="sub" fontSize="9">{labels[idx].sub}</tspan>
            </text>
            <path d={waveformPath(current)} fill="none" stroke={colors[idx]} strokeWidth={idx === 3 ? 3 : 2} />
            <circle cx={plotLeft} cy={t0y} r={3} fill={colors[idx]} />
          </g>
        );
      })}

      <text x={plotLeft + 4} y={plotBottom + 16} className="viz-scale-label">{props.text.t0}</text>
    </svg>
  );
}

function CurrentChip(props: {
  symbolBase: string;
  symbolSub: string;
  amp: number;
  phaseDeg: number;
  text: (typeof UI_TEXT)[Language];
  language: Language;
  strong?: boolean;
}) {
  return (
    <div className={`current-chip ${props.strong ? "strong" : ""}`}>
      <span className="name"><em>{props.symbolBase}</em><sub>{props.symbolSub}</sub></span>
      <span className="amp">{ampLabel(props.amp, props.text, props.language)}</span>
      <span className="angle">{formatDecimal(props.phaseDeg, 1, props.language)}°</span>
    </div>
  );
}
