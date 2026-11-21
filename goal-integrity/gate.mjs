// Candidate-only structural guard. Host MUST supply trusted context; this does not understand prose semantically.
const stop = (code) => ({decision:"STOP_WORK",code});
const nonempty = x => typeof x === "string" && x.trim().length > 0;
const sha = x => nonempty(x) && /^[a-f0-9]{40}$/i.test(x);
export function checkGoalIntegrity(lock, action, context) {
  if (!lock || !action || !context || !nonempty(lock.project_id) ||
      !nonempty(lock.goal_version) || !nonempty(lock.user_authorized_goal) ||
      !Array.isArray(lock.non_goals) || !lock.non_goals.length ||
      !Array.isArray(lock.quality_evidence) || !lock.quality_evidence.length ||
      !nonempty(lock.primary_deliverable) ||
      !Array.isArray(lock.supporting_deliverables) ||
      !["USER_CONFIRMED","CANDIDATE_UNCONFIRMED"].includes(lock.approval)) return stop("INVALID_GOAL_LOCK");
  if (lock.approval !== "USER_CONFIRMED") return stop("GOAL_LOCK_NOT_CONFIRMED");
  if (action.project_id !== lock.project_id) return stop("PROJECT_ID_MISMATCH");
  if (action.goal_version !== lock.goal_version) return stop("GOAL_VERSION_MISMATCH");
  if (action.proposed_goal_change && !context.explicit_user_goal_change_approval) return stop("UNAUTHORIZED_GOAL_CHANGE");
  if (context.latest_user_correction_conflict || action.latest_user_correction_conflict) return stop("LATEST_USER_CORRECTION");
  const u=context.latest_user_intent, cp=context.authoritative_checkpoint;
  if (!u || !nonempty(u.id) || !cp || !nonempty(cp.id) || !sha(cp.blob_sha) ||
      !nonempty(cp.next_action_id) || context.authoritative_source_verified !== true)
    return stop("AUTHORITATIVE_RECOVERY_UNVERIFIED");
  if (context.newer_checkpoint_known === true) return stop("STALE_CHECKPOINT");
  if (action.user_intent_id !== u.id) return stop("LATEST_INTENT_NOT_BOUND");
  if (action.checkpoint_id !== cp.id || action.checkpoint_blob_sha !== cp.blob_sha)
    return stop("CHECKPOINT_IDENTITY_MISMATCH");
  const target = nonempty(u.explicit_next_action_id) ? u.explicit_next_action_id : cp.next_action_id;
  if (action.next_action_id !== target) return stop("STALE_OR_UNAUTHORIZED_NEXT");
  if (action.goal_conflict === true) return stop("GOAL_CONFLICT");
  // goal_conflict:false is NOT sufficient to prove alignment.
  if (action.goal_conflict !== false || action.semantic_reviewed !== true)
    return stop("SEMANTIC_ALIGNMENT_UNVERIFIED");
  const main=action.deliverable_kind===lock.primary_deliverable;
  const support=lock.supporting_deliverables.includes(action.deliverable_kind);
  if (!main && !support) return stop("DELIVERABLE_SCOPE_MISMATCH");
  if (support && context.mainline_due === true && !u.explicitly_authorizes_support_first)
    return stop("SUPPORT_DISPLACES_MAIN_GOAL");
  if (action.claims_main_goal_complete && !main) return stop("SUPPORT_CANNOT_COMPLETE_GOAL");
  if (action.claims_quality_improvement) {
    const e=action.manuscript_delta_evidence;
    if (!main || !e || !sha(e.before_blob) || !sha(e.after_blob) ||
        e.before_blob===e.after_blob || !nonempty(e.diff_ref) || !nonempty(e.editorial_reason))
      return stop("QUALITY_EVIDENCE_MISSING");
  }
  if (action.claims_human_acceptance && context.human_acceptance_verified !== true)
    return stop("SELF_CERTIFIED_ACCEPTANCE");
  if (action.claims_full_release && context.independent_supervision_passed !== true)
    return stop("UNVERIFIED_RELEASE");
  return {decision:"ALLOW_SCOPED",code:"STRUCTURAL_ONLY_NOT_SEMANTIC_OR_HUMAN_ACCEPTANCE"};
}
