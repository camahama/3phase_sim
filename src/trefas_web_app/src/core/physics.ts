export type Complex = { re: number; im: number };

export type ThreePhaseCurrentResult = {
  lineCurrents: [Complex, Complex, Complex];
  neutralCurrent: Complex;
};

const EPS = 1e-12;

export function complex(re: number, im = 0): Complex {
  return { re, im };
}

function add(a: Complex, b: Complex): Complex {
  return { re: a.re + b.re, im: a.im + b.im };
}

function sub(a: Complex, b: Complex): Complex {
  return { re: a.re - b.re, im: a.im - b.im };
}

function div(a: Complex, b: Complex): Complex {
  const den = b.re * b.re + b.im * b.im;
  if (den < EPS) {
    throw new Error("Impedance magnitude must be > 0");
  }
  return {
    re: (a.re * b.re + a.im * b.im) / den,
    im: (a.im * b.re - a.re * b.im) / den,
  };
}

export function magnitude(z: Complex): number {
  return Math.hypot(z.re, z.im);
}

export function angle(z: Complex): number {
  return Math.atan2(z.im, z.re);
}

function phasor(mag: number, rad: number): Complex {
  return { re: mag * Math.cos(rad), im: mag * Math.sin(rad) };
}

export function phaseVoltages(vPhaseRms: number): [Complex, Complex, Complex] {
  return [
    phasor(vPhaseRms, 0),
    phasor(vPhaseRms, (-2 * Math.PI) / 3),
    phasor(vPhaseRms, (-4 * Math.PI) / 3),
  ];
}

export function lineVoltages(vPhaseRms: number): [Complex, Complex, Complex] {
  const [v1, v2, v3] = phaseVoltages(vPhaseRms);
  return [sub(v1, v2), sub(v2, v3), sub(v3, v1)];
}

function currentFromBranch(v: Complex, z: Complex | null): Complex {
  if (z == null) {
    return complex(0, 0);
  }
  return div(v, z);
}

export function calculateLineAndNeutralCurrents(args: {
  yImpedances: [Complex | null, Complex | null, Complex | null];
  deltaImpedances?: [Complex | null, Complex | null, Complex | null];
  voltageRms: number;
}): ThreePhaseCurrentResult {
  const { yImpedances, voltageRms } = args;
  const deltaImpedances = args.deltaImpedances ?? [null, null, null];

  const vp = phaseVoltages(voltageRms);
  const vl = lineVoltages(voltageRms);

  const iy0 = currentFromBranch(vp[0], yImpedances[0]);
  const iy1 = currentFromBranch(vp[1], yImpedances[1]);
  const iy2 = currentFromBranch(vp[2], yImpedances[2]);

  const id12 = currentFromBranch(vl[0], deltaImpedances[0]);
  const id23 = currentFromBranch(vl[1], deltaImpedances[1]);
  const id31 = currentFromBranch(vl[2], deltaImpedances[2]);

  const i1 = add(sub(iy0, id31), id12);
  const i2 = add(sub(iy1, id12), id23);
  const i3 = add(sub(iy2, id23), id31);

  const inNeutral = add(add(i1, i2), i3);

  return {
    lineCurrents: [i1, i2, i3],
    neutralCurrent: inNeutral,
  };
}

export function resistiveImpedanceFromPower(powerW: number, voltageRms: number): Complex | null {
  if (powerW <= 0) {
    return null;
  }
  const r = (voltageRms * voltageRms) / powerW;
  return complex(r, 0);
}
