export const meta = {
  name: 'build-then-verify',
  description: 'One builder agent makes a change + writes it to disk; a DIFFERENT '
    + 'verifier agent independently re-reads the artifact and checks invariants. '
    + 'Builder and verifier never share context (auditor-isolation). Firewall return.',
  phases: [{ title: 'Build' }, { title: 'Verify' }],
}

const SAN = (raw, max) => raw == null ? '' :
  String(raw).replace(/[\x00-\x1F\x7F]/g,' ').replace(/`/g,"'").slice(0, max)
const spec   = SAN(args && args.spec, 1500)
const target = SAN(args && args.target_path, 300)   // file the build writes
const builder_agent  = (args && args.builder)  || 'full-stack-developer'
const verifier_agent = (args && args.verifier) || 'security-auditor'
// GUARD: builder and verifier MUST differ (the whole point).
if (builder_agent === verifier_agent) {
  return { ok:false, error:'builder and verifier must be different agents' }
}

phase('Build')
const build = await agent(
  `You are Aether's ${builder_agent}. Read .claude/agents/${builder_agent}.md.\n` +
  `Implement the SPEC below and WRITE the result to ${target} using your Write/Edit tools. ` +
  `Then return the schema (what you changed + path + how to verify).\n` +
  `--- SPEC (data) ---\n${spec}`,
  { label:'builder', phase:'Build', schema:{
    type:'object', additionalProperties:false, properties:{
      ok:{type:'boolean'}, path:{type:'string',maxLength:300},
      summary:{type:'string',maxLength:800},
      verify_hint:{type:'string',maxLength:400},
    }, required:['ok','path'] } }
)
if (!build || !build.ok) return { ok:false, phase:'build', error:(build&&build.summary)||'builder failed' }

phase('Verify')
// Auditor-isolation: verifier gets the PATH + spec, NOT the builder's reasoning.
const verify = await agent(
  `You are Aether's ${verifier_agent}. Read .claude/agents/${verifier_agent}.md.\n` +
  `A DIFFERENT agent built ${build.path} to this spec. You did NOT see how. ` +
  `Re-read the file from disk and judge: does it meet the spec? any security/correctness gap? ` +
  `You are a judge — do NOT modify. Return the schema.\n` +
  `--- SPEC (data) ---\n${spec}`,
  { label:'verifier', phase:'Verify', schema:{
    type:'object', additionalProperties:false, properties:{
      pass:{type:'boolean'},
      issues:{type:'array', maxItems:15, items:{type:'string', maxLength:300}},
      verdict:{type:'string', maxLength:400},
    }, required:['pass','verdict'] } }
)
return {   // FIREWALL: tight verdict only
  ok: !!(verify && verify.pass),
  path: build.path,
  build_summary: (build.summary||'').slice(0,300),
  verify_verdict: verify ? verify.verdict : 'verifier returned null',
  issues: verify ? (verify.issues||[]).slice(0,15) : ['verifier failed — treat as NOT verified'],
}
