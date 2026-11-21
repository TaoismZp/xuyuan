// Candidate guard; NOT wired into any ChatGPT or DeepWrite runtime.
export function checkGoalIntegrity(lock, action) {
 const stop=(code)=>({decision:"STOP_WORK",code});
 if(!lock||!action||!lock.user_authorized_goal||!Array.isArray(lock.non_goals)||!Array.isArray(lock.quality_evidence))return stop("INVALID_INPUT");
 if(action.goal_version!==lock.goal_version)return stop("GOAL_VERSION_MISMATCH");
 if(action.proposed_goal_change&&!action.explicit_user_approval)return stop("UNAUTHORIZED_GOAL_CHANGE");
 if(action.latest_user_correction_conflict)return stop("LATEST_USER_CORRECTION");
 if(action.goal_conflict===true)return stop("GOAL_CONFLICT");
 if(action.goal_conflict!==false)return stop("ALIGNMENT_UNVERIFIED");
 if(action.claims_quality_improvement&&!action.manuscript_delta_evidence)return stop("QUALITY_EVIDENCE_MISSING");
 if(action.claims_human_acceptance&&!action.external_acceptance_evidence)return stop("SELF_CERTIFIED_ACCEPTANCE");
 if(action.recovery&&!action.checkpoint_verified)return stop("CHECKPOINT_UNVERIFIED");
 return {decision:"ALLOW_SCOPED",code:"STATIC_GATE_PASS_NOT_HUMAN_ACCEPTANCE"};
}
