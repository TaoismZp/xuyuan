// Deterministic, offline routing example for 「断档重生」.
// It does NOT access ChatGPT conversations, GitHub, Library or any network.
// Caller must retrieve real checkpoints and validate sources after routing.
const norm = (s) => String(s || "").normalize("NFKC").toLocaleLowerCase("zh-CN").replace(/[\s\-_·•]+/g, "");
const statusesEnded = new Set(["COMPLETED","CANCELLED","TERMINATED","ACCEPTED"]);

export function parseRevival(message) {
  if (typeof message !== "string") return {triggered: false};
  const m = /^\s*断档重生(?:\s*[:：\-—]\s*(\S[\s\S]*?))?\s*$/u.exec(message);
  return m ? {triggered: true, topic: (m[1] || "").trim()} : {triggered: false};
}
export function resolveRevival({message, contextFocusId = null, index = []} = {}) {
  const command = parseRevival(message);
  if (!command.triggered) return {status: "NOT_TRIGGER", next: "按普通用户请求继续"};
  // Selection is NOT an acceptance or a verified recovery.
  const items = index.filter(x => x && typeof x.id === "string" && x.id.trim());
  const unique = (arr) => [...new Map(arr.map(x => [x.id, x])).values()];
  const names = (x) => [x.id, x.title, ...(Array.isArray(x.aliases) ? x.aliases : [])].map(norm).filter(Boolean);
  const choice = (matches, why) => ({
    status: "CHOOSE_TOPIC", reason: why,
    options: unique(matches).map(x => ({id:x.id,title:x.title || x.id})),
    next: "只要求选择项目或讨论主题名称，不要求重新讲历史"
  });
  const selected = (x, reason) => ({
    status: "VERIFY_CHECKPOINT", id:x.id, title:x.title || x.id,
    checkpoint: typeof x.checkpoint === "string" ? x.checkpoint : null,
    reason, next: "实际读取档案与原产物，验证版本、状态和下一可执行动作"
  });
  if (command.topic) {
    let found = items.filter(x => names(x).includes(norm(command.topic)));
    if (!found.length && norm(command.topic).length >= 3) {
      found = items.filter(x => names(x).some(y => y.includes(norm(command.topic))));
    }
    found = unique(found);
    if (found.length > 1) return choice(found, "主题名称匹配多个档案");
    if (found.length === 1) return selected(found[0],"用户明确指定了主题");
    return {status:"SEARCH_SOURCES",topic:command.topic,next:"搜索已授权 Library/连接器和项目原档；没有结果才说明缺口"};
  }
  if (contextFocusId) {
    const focused = items.filter(x => x.id === contextFocusId);
    if (focused.length === 1) return selected(focused[0],"当前对话明确且唯一的未完主题");
  }
  const unfinished = unique(items.filter(x => !statusesEnded.has(String(x.work_status || "").toUpperCase()) && x.resume_candidate === true));
  if (unfinished.length === 1) return selected(unfinished[0],"索引只有一个明确未完候选，仍需重新核验");
  if (unfinished.length > 1) return choice(unfinished,"跨对话存在多个未完主题，不能用最近时间猜目标");
  return {status:"SEARCH_SOURCES",topic:null,next:"检索私密 Library 主题档案与有权限的连接器，不能凭记忆编造"};
}
export function decideContinuation(checkpoint = {}) {
  if (!checkpoint || typeof checkpoint !== "object") return {status:"BLOCKED_CONTEXT",next:"取得可信的原始检查点"};
  if (checkpoint.privacy_violation === true)
    return {status:"BLOCKED_SAFETY",next:"暂停公开写入，将未发表内容移到私有位置"};
  if (checkpoint.exists !== true || checkpoint.source_read !== true)
    return {status:"BLOCKED_CONTEXT",next:"搜索原始材料和 Library，不能将注册表当作已读原稿"};
  if (checkpoint.identity_verified !== true || checkpoint.artifact_verified !== true)
    return {status:"VERIFY_EVIDENCE",next:"重新核对源文件、commit、验收和交付身份"};
  if (statusesEnded.has(String(checkpoint.status || "").toUpperCase()))
    return {status:"TERMINAL",next:"只提供已验收状态；用户明确重启后才能继续"};
  if (checkpoint.needs_owner_action === true && checkpoint.owner_action_verified !== true)
    return {status:"PENDING_OWNER",next:"说明必须由本人完成的唯一授权/发布动作，不假冒用户"};
  if (!checkpoint.next_action || typeof checkpoint.next_action !== "string" || !checkpoint.next_action.trim())
    return {status:"RECONSTRUCT_NEXT",next:"根据原始目标与当前未完成 Gate 重建唯一下一步并归档，不虚构执行"};
  return {status:"RESUME_EXECUTION",next:checkpoint.next_action.trim()};
}
