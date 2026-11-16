const fs = require("fs");
const L = require("./lib"); const { D, NAVY, GREY, PAGE_W, MARG, FONT, MATH } = L;
const { Document, Packer, Paragraph, TextRun, Footer, Header, PageNumber, AlignmentType, LevelFormat, HeadingLevel } = D;
const p1 = require("./report_p1"), p2 = require("./report_p2"), p3 = require("./report_p3"), p4 = require("./report_p4");

const body = [
  ...p1.frontMatter(), ...p1.partI(), ...p1.partII(),
  ...p2.partIII(), ...p2.partIV(), ...p2.partV(),
  ...p3.partVI(), ...p4.partVII(), ...p4.partVIII(), ...p4.partIX(), ...p4.partX(), ...p4.partXI(), ...p4.appendices(),
];
Object.assign(L.refs.E, p2.E);   // equation numbers registered by the report parts

const doc = new Document({
  creator: "propsim research", title: "What the Topstep 50K Contract Does to a Trading Process — and What a Genuine Edge Is Worth Within Its Terms",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Cambria", size: 36, bold: true, color: NAVY }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Cambria", size: 28, bold: true, color: NAVY }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 22, bold: true, color: NAVY }, paragraph: { spacing: { before: 120, after: 40 } } },
      { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 20 }, paragraph: { spacing: { before: 0, after: 20 }, indent: { left: 360 } } },
      { id: "TOC3", name: "toc 3", basedOn: "Normal", next: "Normal", run: { font: FONT, size: 19, color: GREY }, paragraph: { spacing: { before: 0, after: 20 }, indent: { left: 720 } } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Cambria", size: 24, bold: true, color: "2E7D8C" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
  ] },
  features: { updateFields: true },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 15840 }, margin: { top: 1200, bottom: 1100, left: MARG, right: MARG } } },
    headers: { default: new Header({ children: [new Paragraph({ children: [new TextRun({ text: "Topstep 50K contract study  ·  propsim  ·  final version 2026-09-21", size: 16, color: GREY, font: FONT })], alignment: AlignmentType.RIGHT })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun({ text: "Page ", size: 16, color: GREY, font: FONT }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GREY, font: FONT })], alignment: AlignmentType.CENTER })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(__dirname + "/report_raw.docx", buf); fs.writeFileSync(__dirname + "/headings.json", JSON.stringify(L.headings)); fs.writeFileSync(__dirname + "/refs.json", JSON.stringify(L.refs, null, 1)); console.log("written", buf.length, "eqs", L.eqNum(), "figs", L.figNum(), "tables", L.tabNum(), "headings", L.headings.length); });
