const fs = require("fs");
const D = require("docx");
const { Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, ImageRun, PageBreak, TabStopType, TableOfContents, LevelFormat, VerticalAlign } = D;

const NAVY = "14343B", TEAL = "2E7D8C", AMBER = "D9822B", GREY = "5F6B6D", LIGHT = "E8EEF0", PALE = "F4F7F8", RULE = "B8C4C8";
const PAGE_W = 12240, MARG = 1080, CONTENT_W = PAGE_W - 2 * MARG; // 10,080 DXA = 7"
const FONT = "Calibri", MATH = "Cambria Math";

let eqCounter = 0, figCounter = 0, tabCounter = 0;
const refs = { E: {}, T: {}, F: {} };   // key -> number; resolved into {{E:key}} / {{T:key}} / {{F:key}} tokens after the build
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const thin = { style: BorderStyle.SINGLE, size: 4, color: RULE };
const borders = (b) => ({ top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b });

const run = (t, o = {}) => new TextRun({ text: t, font: o.font || FONT, size: o.size || 22, bold: !!o.bold, italics: !!o.italics, color: o.color || "222222" });
const p = (t, o = {}) => new Paragraph({ children: Array.isArray(t) ? t : [run(t, o)], spacing: { after: o.after ?? 120, before: o.before ?? 0, line: o.line ?? 276 }, alignment: o.align || AlignmentType.LEFT, indent: o.indent, keepNext: o.keepNext, widowControl: true });
const rich = (parts, o = {}) => new Paragraph({ children: parts.map(x => typeof x === "string" ? run(x, o) : run(x.t, { ...o, ...x })), spacing: { after: o.after ?? 120, line: 276 }, indent: o.indent, alignment: o.align });
const headings = []; let tocId = 0;
function heading(t, level, opts = {}) {
  const id = "_Toc" + (++tocId); headings.push({ text: t, level, id });
  return new Paragraph({ heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][level - 1], keepNext: true, keepLines: true,
    spacing: [{ before: opts.before || 360, after: 160 }, { before: 280, after: 120 }, { before: 200, after: 80 }][level - 1], pageBreakBefore: !!opts.pb,
    children: [new D.Bookmark({ id, children: [new TextRun({ text: t })] })] });
}
const H1 = (t) => heading(t, 1, { pb: true });
const H1n = (t) => heading(t, 1, { before: 600 });
const H2 = (t) => heading(t, 2);
const H3 = (t) => heading(t, 3);
const pb = () => new Paragraph({ children: [new PageBreak()] });
const bullets = (items, ref = "bul") => items.map(t => new Paragraph({ children: Array.isArray(t) ? t.map(x => typeof x === "string" ? run(x) : run(x.t, x)) : [run(t)], numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 276 } }));
const numbered = (items) => items.map(t => new Paragraph({ children: [run(t)], numbering: { reference: "num", level: 0 }, spacing: { after: 60, line: 276 } }));

// Equation: text in Cambria Math, centred, number right-aligned by tab; followed by an optional "where" block
function eq(text, where, opts = {}) {
  const n = ++eqCounter; opts.num = n; if (opts.key) refs.E[opts.key] = n;
  const lines = text.split(" ⏎ ");
  const runs = [];
  lines.forEach((ln, i) => runs.push(new TextRun({ text: "\t" + ln, font: MATH, size: 22, color: NAVY, break: i ? 1 : 0 })));
  runs.push(new TextRun({ text: `\t(${n})`, font: FONT, size: 20, color: GREY }));
  const out = [new Paragraph({
    children: runs, keepLines: true,
    tabStops: [{ type: TabStopType.CENTER, position: CONTENT_W / 2 }, { type: TabStopType.RIGHT, position: CONTENT_W }],
    spacing: { before: 120, after: 80 }, keepNext: !!where, shading: { type: ShadingType.CLEAR, fill: PALE, color: "auto" }, border: { top: thin, left: thin, bottom: thin, right: thin },
  })];
  if (where && where.length) {
    const parts = [run("where ", { italics: true, color: GREY, size: 20 })];
    where.forEach((w, i) => { parts.push(run(w[0], { bold: true, size: 20, color: NAVY })); parts.push(run(" " + w[1] + (i < where.length - 1 ? "; " : "."), { size: 20 })); });
    out.push(new Paragraph({ children: parts, indent: { left: 360 }, spacing: { after: 140, line: 260 } }));
  }
  return out;
}
const eqNum = () => eqCounter;

function cell(text, o = {}) {
  const paras = (Array.isArray(text) ? text : [text]).map(t => new Paragraph({ children: [run(String(t), { size: o.size || 19, bold: !!o.bold, color: o.color, italics: !!o.italics })], spacing: { after: 40, line: 250 }, alignment: o.align, keepNext: !!o.keepNext, keepLines: true }));
  return new TableCell({ children: paras, width: { size: o.w, type: WidthType.DXA }, shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined, margins: { top: o.tight ? 30 : 60, bottom: o.tight ? 30 : 60, left: 90, right: 90 }, verticalAlign: VerticalAlign.CENTER });
}
// Table: header row + rows; widths sum to CONTENT_W
function table(header, rows, widths, opts = {}) {
  const tw = widths.reduce((a, b) => a + b, 0);
  const keep = opts.keep ?? rows.length <= 12;
  const hr = new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, i) => cell(h, { w: widths[i], bold: true, fill: NAVY, color: "FFFFFF", size: 18, keepNext: keep })) });
  const body = rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, { w: widths[i], fill: ri % 2 ? PALE : undefined, bold: opts.boldFirst && i === 0, size: opts.size, tight: opts.tight, keepNext: keep && ri < rows.length - 1 })) }));
  const out = [];
  if (opts.caption) { const n = ++tabCounter; if (opts.key) refs.T[opts.key] = n; out.push(new Paragraph({ children: [run(`Table ${n} — ${opts.caption}`, { bold: true, size: 20, color: NAVY })], spacing: { before: 160, after: 80 }, keepNext: true })); }
  out.push(new Table({ rows: [hr, ...body], width: { size: tw, type: WidthType.DXA }, columnWidths: widths, borders: borders(thin) }));
  if (opts.note) out.push(new Paragraph({ children: [run("Note. " + opts.note, { italics: true, size: 18, color: GREY })], spacing: { before: 60, after: 160 } }));
  else out.push(p("", { after: 120 }));
  return out;
}
const tabNum = () => tabCounter;

// Result card in the style of the example study
function card(fields) {
  const w1 = 2100, w2 = CONTENT_W - w1;
  const rows = fields.map(([k, v], i) => new TableRow({ cantSplit: true, children: [cell(k, { w: w1, bold: true, fill: LIGHT, color: NAVY, size: 18, keepNext: i < 1 }), cell(v, { w: w2, size: 20, bold: k === "RESULT", keepNext: i < 1 })] }));
  return [new Table({ rows, width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [w1, w2], borders: borders(thin) }), p("", { after: 120 })];
}

function callout(title, lines) {
  const paras = [new Paragraph({ children: [run(title, { bold: true, color: NAVY, size: 21 })], spacing: { after: 80 } }), ...lines.map(l => new Paragraph({ children: [run(l, { size: 20 })], spacing: { after: 60, line: 260 } }))];
  return [new Table({ rows: [new TableRow({ cantSplit: true, children: [new TableCell({ children: paras, width: { size: CONTENT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: PALE, color: "auto" }, margins: { top: 120, bottom: 120, left: 160, right: 160 } })] })], width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], borders: borders({ style: BorderStyle.SINGLE, size: 6, color: AMBER }) }), p("", { after: 120 })];
}

function pngSize(path) { const b = fs.readFileSync(path); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function figure(path, caption, opts = {}) {
  const maxWidthIn = typeof opts === "number" ? opts : (opts.maxWidth || 6.2);
  const { w, h } = pngSize(path); const wi = Math.min(maxWidthIn, 6.9); const hi = wi * h / w; const n = ++figCounter;
  if (opts.key) refs.F[opts.key] = n;
  return [new Paragraph({ children: [new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width: Math.round(wi * 96), height: Math.round(hi * 96) } })], alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true }),
    new Paragraph({ children: [run(`Figure ${n}. `, { bold: true, size: 19, color: NAVY }), run(caption, { size: 19, color: GREY })], spacing: { after: 200 }, alignment: AlignmentType.LEFT })];
}
const figNum = () => figCounter;

module.exports = { refs, headings, D, run, p, rich, H1, H1n, H2, H3, pb, bullets, numbered, eq, eqNum, table, tabNum, card, callout, figure, figNum, cell, NAVY, TEAL, AMBER, GREY, LIGHT, PALE, CONTENT_W, PAGE_W, MARG, FONT, MATH };
