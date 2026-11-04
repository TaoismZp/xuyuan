// Verify GitHub portability files only. This does NOT test real AI model behavior.
// Run: node scripts/check-agent-skills.mjs
import fs from "node:fs";
import crypto from "node:crypto";

const roots = [".agents/skills", ".claude/skills", ".github/skills"];
const mirrored = [
  "socratic-review/SKILL.md",
  "elite-thinking/SKILL.md",
  "elite-thinking/references/MODEL_ROUTER.md",
  "elite-thinking/references/DOMAIN_ROUTER.md",
];
const errors = [];

function sha(text) {
  return crypto.createHash("sha256").update(text).digest("hex");
}
function read(path) {
  if (!fs.existsSync(path)) {
    errors.push(`MISSING: ${path}`);
    return null;
  }
  return fs.readFileSync(path, "utf8");
}

for (const file of mirrored) {
  const variants = roots.map((r) => [`${r}/${file}`, read(`${r}/${file}`)]);
  if (variants.some(([, content]) => content === null)) continue;
  const canonicalHash = sha(variants[0][1]);
  for (const [path, content] of variants.slice(1)) {
    if (sha(content) !== canonicalHash) errors.push(`MIRROR_DRIFT: ${file} differs at ${path}`);
  }
  if (file.endsWith("/SKILL.md")) {
    const [path, content] = variants[0];
    const header = content.match(/^---\n([\s\S]*?)\n---/);
    if (!header) errors.push(`NO_FRONTMATTER: ${path}`);
    else {
      const name = header[1].match(/^name:\s*([\w-]+)\s*$/m)?.[1];
      const description = header[1].match(/^description:\s*(.+)$/m)?.[1];
      const folder = file.split("/")[0];
      if (name !== folder) errors.push(`NAME_MISMATCH: ${path}`);
      if (!description || description.length > 1024) errors.push(`DESCRIPTION_INVALID: ${path}`);
    }
  }
  console.log(`MIRROR_CHECK ${file} sha256=${canonicalHash} copies=3`);
}

const elite = read(".agents/skills/elite-thinking/SKILL.md") ?? "";
const domain = read(".agents/skills/elite-thinking/references/DOMAIN_ROUTER.md") ?? "";
const stress = read(".agents/skills/STRESS_TESTS_V2.md") ?? "";
const expected = ["世界观与基础认识", "个人成长与长期战略", "决策、判断和风险", "学习与教育", "商业、创造价值与赚钱", "社会、经济与合作", "公司、授权与领导", "复杂系统与适应", "价值、伦理与高阶反思", "探索和生发"];
for (const category of expected) if (!domain.includes(category)) errors.push(`MISSING_DOMAIN: ${category}`);
if (!elite.includes("references/DOMAIN_ROUTER.md")) errors.push("MISSING_DOMAIN_ROUTER_LINK");
for (const id of ["L1", "B1", "S1", "C1", "V1", "E1", "R1", "N1", "Q1", "Q2"]) {
  if (!stress.includes(`| ${id} `)) errors.push(`MISSING_STRESS_TEST: ${id}`);
}
console.log(`DOMAIN_COVERAGE categories=${expected.length} stress_tests=10`);
if (errors.length) {
  for (const e of errors) console.error("FAIL", e);
  process.exitCode = 1;
} else {
  console.log("PASS: static portability / model-domain coverage checks only. Agent runtime A/B/C is UNVERIFIED.");
}
