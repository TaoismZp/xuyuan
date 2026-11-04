// Wish Delivery self-evolution boundary checker. This is not a quality oracle.
// No dependencies; only transparent, deterministic negative-case checks.
export function decide(x) {
  const why = (state, reason, next) => ({state, reason, next});
  if (!x || typeof x !== 'object') return why('BLOCKED_CONTEXT', '缺少任务事实', '取得原始用户目标与可信状态');
  if (x.scope === 'protocol_promotion' && (!x.external_review || !x.real_trial || !x.user_approval)) {
    return why('CANDIDATE', '协议不能只靠自己写的测试晋级', '独立审核、真实任务验证并取得正式升级授权');
  }
  if (x.context_missing === true) return why('BLOCKED_CONTEXT', '外部检查点或原始材料不可验证', '检索档案或请求账号数据导出');
  if (x.status_only_no_next === true) return why('FAIL', '长任务报告没有下一可执行动作', '补充可靠检查点与下一实际动作');
  if (x.privacy === 'public_unpublished') return why('FAIL', '把未发布内容提交到公开 Git 不能保密', '保存在私有存储并停止提交');
  if (x.identity_match === false) return why('FAIL', '验收证据与目标对象的版本身份不一致', '重新绑定正确版本并重验');
  if (x.scope === 'simple' && x.reversible === true) return why('DIRECT', '低风险明确任务不需复杂工程四件套', '直接处理并检查结果');
  // Gate 0 is prospective. Never stop an already-shipped project from closing
  // its real owner gate merely because an older discovery document is absent.
  if (x.scope === 'complex' && x.artifact_exists !== true && (x.job_defined !== true || x.baseline_compared !== true)) {
    return why('DISCOVERY_REQUIRED', '复杂愿望缺真实工作目标或不造/复用基线', '完成最小低成本对照');
  }
  if (x.artifact_exists !== true || x.core_function_tested !== true)
    return why('CANDIDATE', '主成品不存在或核心功能未验证', '完成真实可操作的核心闭环');
  if (x.samesurface_tested !== true)
    return why('CANDIDATE', '尚未在真实交付表面验证', '在用户真实终端/URL/文件上执行');
  if (x.owner_action_required === true && x.owner_action_verified !== true) {
    return why('READY_FOR_OWNER_ACTION', '只有读取/预览等子系统可声明局部交付', '等待本人完成授权动作并核对结果');
  }
  if (x.aftercare_verified === true)
    return why('ADOPTED', '交付与后续实际使用均有证据', '保存新使用记录并继续维护');
  return why('DELIVERED', '核心交付闭环已验收，长期使用尚未证明', '记录首次使用、修订或回滚行为');
}
