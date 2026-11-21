import assert from "node:assert/strict";
import {checkGoalIntegrity} from "../gate.mjs";
const lock={goal_version:"v1",user_authorized_goal:"提升作品思想深度和文学质量",non_goals:["仅资料核对冒充总审"],quality_evidence:["正文差异"]};
const ok={goal_version:"v1",goal_conflict:false};
const tests=[
["normal",ok,"ALLOW_SCOPED"],
["10 turns",ok,"ALLOW_SCOPED"],
["stale next",{...ok,latest_user_correction_conflict:true},"STOP_WORK"],
["facts replace literary quality",{...ok,goal_conflict:true},"STOP_WORK"],
["unverified semantic alignment",{...ok,goal_conflict:null},"STOP_WORK"],
["missing manuscript delta",{...ok,claims_quality_improvement:true},"STOP_WORK"],
["self pass",{...ok,claims_human_acceptance:true},"STOP_WORK"],
["unauthorized goal change",{...ok,proposed_goal_change:true},"STOP_WORK"],
["stale goal version",{...ok,goal_version:"v0"},"STOP_WORK"],
["unverified recovery",{...ok,recovery:true,checkpoint_verified:false},"STOP_WORK"],
["verified recovery",{...ok,recovery:true,checkpoint_verified:true},"ALLOW_SCOPED"]];
for(const [name,input,want] of tests){assert.equal(checkGoalIntegrity(lock,input).decision,want,name);console.log("PASS",name)}
console.log("STATIC SIMULATION ONLY",tests.length);
