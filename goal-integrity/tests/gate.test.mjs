import test from "node:test";
import assert from "node:assert/strict";
import {checkGoalIntegrity as check} from "../gate.mjs";
const hex = c => c.repeat(40);
const lock={project_id:"test-book",goal_version:"v1",user_authorized_goal:"提升真实书稿的思想和叙事质量",non_goals:["只做项目管理"],quality_evidence:["正文diff"],approval:"USER_CONFIRMED",privacy:"PUBLIC_GENERIC",primary_deliverable:"MANUSCRIPT",supporting_deliverables:["AUDIT","TOOL"]};
const context={latest_user_intent:{id:"u23"},authoritative_checkpoint:{id:"R23",blob_sha:hex("a"),next_action_id:"REVIEW_NEXT"},authoritative_source_verified:true};
const action={project_id:"test-book",goal_version:"v1",user_intent_id:"u23",checkpoint_id:"R23",checkpoint_blob_sha:hex("a"),next_action_id:"REVIEW_NEXT",goal_conflict:false,semantic_reviewed:true,deliverable_kind:"MANUSCRIPT"};
const checkDecision=(a=action,c=context,l=lock)=>check(l,a,c).decision;
test("normal scoped action",()=>assert.equal(checkDecision(),"ALLOW_SCOPED"));
test("self reported goal_conflict false without review fails",()=>assert.equal(checkDecision({...action,semantic_reviewed:false}),"STOP_WORK"));
test("wrong project",()=>assert.equal(checkDecision({...action,project_id:"other"}),"STOP_WORK"));
test("candidate goal unconfirmed",()=>assert.equal(checkDecision(action,context,{...lock,approval:"CANDIDATE_UNCONFIRMED"}),"STOP_WORK"));
test("stale goal version",()=>assert.equal(checkDecision({...action,goal_version:"v0"}),"STOP_WORK"));
test("stale index checkpoint",()=>assert.equal(checkDecision({...action,checkpoint_id:"R6"}),"STOP_WORK"));
test("stale index same name but wrong blob",()=>assert.equal(checkDecision({...action,checkpoint_blob_sha:hex("b")}),"STOP_WORK"));
test("newer authoritative checkpoint flagged",()=>assert.equal(checkDecision(action,{...context,newer_checkpoint_known:true}),"STOP_WORK"));
test("unverified source",()=>assert.equal(checkDecision(action,{...context,authoritative_source_verified:false}),"STOP_WORK"));
test("stale historical NEXT",()=>assert.equal(checkDecision({...action,next_action_id:"OLD_NEXT"}),"STOP_WORK"));
test("latest user instruction overrides prior NEXT",()=>assert.equal(checkDecision({...action,next_action_id:"NEW_NEXT"},{...context,latest_user_intent:{id:"u23",explicit_next_action_id:"NEW_NEXT"}}),"ALLOW_SCOPED"));
test("old user intent",()=>assert.equal(checkDecision({...action,user_intent_id:"u19"}),"STOP_WORK"));
test("latest correction conflict",()=>assert.equal(checkDecision(action,{...context,latest_user_correction_conflict:true}),"STOP_WORK"));
test("unauthorized goal change",()=>assert.equal(checkDecision({...action,proposed_goal_change:true}),"STOP_WORK"));
test("support work cannot claim editorial completion",()=>assert.equal(checkDecision({...action,deliverable_kind:"TOOL",claims_main_goal_complete:true}),"STOP_WORK"));
test("support displacement stops",()=>assert.equal(checkDecision({...action,deliverable_kind:"TOOL"},{...context,mainline_due:true}),"STOP_WORK"));
test("explicit support-first exception",()=>assert.equal(checkDecision({...action,deliverable_kind:"TOOL"},{...context,mainline_due:true,latest_user_intent:{id:"u23",explicitly_authorizes_support_first:true}}),"ALLOW_SCOPED"));
test("fake improvement without manuscript evidence",()=>assert.equal(checkDecision({...action,claims_quality_improvement:true}),"STOP_WORK"));
test("same content hash not a quality improvement",()=>assert.equal(checkDecision({...action,claims_quality_improvement:true,manuscript_delta_evidence:{before_blob:hex("a"),after_blob:hex("a"),diff_ref:"compare",editorial_reason:"x"}}),"STOP_WORK"));
test("scoped editorial change can be reported as candidate",()=>assert.equal(checkDecision({...action,claims_quality_improvement:true,manuscript_delta_evidence:{before_blob:hex("a"),after_blob:hex("b"),diff_ref:"compare",editorial_reason:"repaired causal proof"}}),"ALLOW_SCOPED"));
test("self-certified human acceptance blocked",()=>assert.equal(checkDecision({...action,claims_human_acceptance:true}),"STOP_WORK"));
test("release without independent supervision blocked",()=>assert.equal(checkDecision({...action,claims_full_release:true}),"STOP_WORK"));
test("10 sequential intents and checkpoints (simulation, NOT live turns)",()=>{
 let c={...context},prev=hex("a");
 for(let i=1;i<=10;i++){
  const intent="u"+i,cp="R"+i,next="A"+i;
  c={latest_user_intent:{id:intent},authoritative_checkpoint:{id:cp,blob_sha:prev,next_action_id:next},authoritative_source_verified:true};
  const a={...action,user_intent_id:intent,checkpoint_id:cp,checkpoint_blob_sha:prev,next_action_id:next};
  assert.equal(checkDecision(a,c),"ALLOW_SCOPED","round "+i);
  prev=hex(String(i%10));
 }
});
test("round 11 stale action against refreshed checkpoint stops",()=>{
 const c={...context,authoritative_checkpoint:{id:"R24",blob_sha:hex("b"),next_action_id:"NEXT24"}};
 assert.equal(checkDecision(action,c),"STOP_WORK");
});
