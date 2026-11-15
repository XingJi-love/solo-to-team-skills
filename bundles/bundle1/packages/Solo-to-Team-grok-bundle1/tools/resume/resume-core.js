'use strict';
/* Pure local checks. File adapters supply actual bytes; this module cannot send work. */
const ResumeCheck = (() => {
  const parts=['artifact','review','dispatch','receipt'];
  const stages=['review','dispatch','receipt'];
  const required=(s)=>typeof s==='string' && s.trim().length>0;
  const hex=(s)=>typeof s==='string' && /^[0-9a-f]{64}$/i.test(s);
  const exact=(o,keys)=>o && !Array.isArray(o) && typeof o==='object' && Object.keys(o).sort().join('|')===keys.slice().sort().join('|');
  const roles=['lead','producer','reviewer','recipient'];
  // The writer's label is for display only. Evidence actors are checked separately.
  function ownerId(label) {
    const id=label.trim().toLowerCase();
    if(id==='review') return 'reviewer';
    return roles.includes(id) ? id : null;
  }
  function validate(cp) {
    if(!exact(cp,['format','version','task','artifact',...stages,'next','do_not_repeat']) || cp.format!=='solo-to-team.checkpoint'||cp.version!==1)throw Error('无法识别这份断点文件的格式或版本。保留原件。');
    if(!exact(cp.task,['id','request','latest_change','return_to']) || Object.values(cp.task).some(v=>typeof v!=='string'))throw Error('任务字段不完整。');
    for(const k of parts){
      if(!exact(cp[k],k==='artifact'?['file','version','sha256']:['file','sha256'])||Object.values(cp[k]).some(v=>typeof v!=='string'))throw Error(k+' 的文件字段无效。');
      if(cp[k].sha256&&!hex(cp[k].sha256))throw Error(k+' 的 SHA-256 应为 64 位十六进制字符。');
      if(cp[k].file && (cp[k].file.split(/[\\/]/).some(p=>!p||p==='.'||p==='..')||/^(?:[a-z]:|[\\/]|~\/)/i.test(cp[k].file)||/[\x00-\x1f]/.test(cp[k].file)))throw Error('文件位置须是共享文件夹内的相对名称。');
    }
    if(!exact(cp.next,['owner','action'])||typeof cp.next.owner!=='string'||typeof cp.next.action!=='string')throw Error('下一棒须含文字字段 owner（席位标签）和 action（此前记载的动作）。');
    if(!Array.isArray(cp.do_not_repeat)||!cp.do_not_repeat.every(required))throw Error('不可重做清单须是逐条填写的文字。');
  }
  function scopeText(task){return JSON.stringify([task.id,task.request,task.latest_change,task.return_to])}
  async function hash(bytes){
    if(!globalThis.crypto?.subtle)throw Error('当前浏览器不能在此页核对 SHA-256。请用支持本地文件的现代浏览器打开。');
    return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  }
  async function scopeHash(task){return hash(new TextEncoder().encode(scopeText(task)))}
  function marker(text,kind){
    const lines=text.split(/\r?\n/);const found=[];
    for(const line of lines)if(line.startsWith('CHECKPOINT ')){
      const value=JSON.parse(line.slice(11));if(value?.kind===kind)found.push(value);
    }
    if(found.length!==1||!lines.some(line=>line.trim()&&!line.startsWith('CHECKPOINT ')&& !/^(?:`|$|#\s*$)/.test(line.trim())))throw Error('需要一条明确的 '+kind+' 绑定行，以及实际来源记录正文。');
    return found[0];
  }
  function evidence(text,kind,scope,cp){
    let m;try{m=marker(text,kind)}catch(error){return {ok:false,reason:'记录不完整或有冲突。'+error.message}}
    const actor={review:'reviewer',dispatch:'lead',receipt:'recipient'}[kind];
    if(!required(m.source_ref) || m.actor!==actor || m.task_id!==cp.task.id || !hex(m.scope_sha256)||m.scope_sha256.toLowerCase()!==scope || m.artifact_version!==cp.artifact.version || !hex(m.artifact_sha256)||m.artifact_sha256.toLowerCase()!==cp.artifact.sha256.toLowerCase())return {ok:false,reason:'记录的席位、任务、当前变更范围、产物版本或指纹未对齐。'};
    if(kind==='review'){
      if(!['pass','revise'].includes(m.result))return {ok:false,reason:'审核结果不能判为通过或退修。'};
    }else{
      if(m.target!==cp.task.return_to){
        const found=typeof m.target==='string'?JSON.stringify(m.target):'（未登记）';
        const fix=kind==='dispatch'
          ?'请原发件席先核原送件入口。若实际交对、仅标注有误，保留原件，在更正正文注明原送件出处，说明写在正文。用绑定草稿更正 target，再更新断点中的 dispatch 文件与 SHA-256。已有实收记录只核它引用的交件指纹，无需重审或重发产物。实际交错时请核实真实去向。'
          :'请原接收席核对原入口与真实收件。如仅为标注差异，由原席更正此回执的 target，保留来源，再更新 receipt 文件和 SHA-256。无需重发产物。';
        return {ok:false,field:kind+'.target',reason:kind+'.target 不符。断点原值 '+JSON.stringify(cp.task.return_to)+'，原记录写作 '+found+'。'+fix};
      }
      if(m.result!==(kind==='dispatch'?'sent':'received'))return {ok:false,reason:kind+'.result 未写明本席的实际结果。请原席查实行为与出处；草稿不能作凭据。'};
    }
    if(kind==='receipt' && (!hex(m.dispatch_sha256)||m.dispatch_sha256.toLowerCase()!==cp.dispatch.sha256.toLowerCase()))return {ok:false,reason:'receipt.dispatch_sha256 与登记的交件记录不符。请接收席核对原交件及其更正记录，再按已核的交件指纹登记真实收件，无需重发产物。'};
    return {ok:true,result:m.result,source:m.source_ref};
  }
  async function bindingDraft(cp,kind,getBytes){
    validate(cp);
    if(!stages.includes(kind))throw Error('请选择独审、交件或实收。');
    if(!Object.values(cp.task).every(required))throw Error('请先打开已填完整任务和原交还入口的断点。');
    if(!required(cp.artifact.version))throw Error('请先核回真实产物的版次。');
    async function frozen(part){
      const entry=cp[part];
      if(!entry.file || !hex(entry.sha256))throw Error('缺少 '+part+' 的文件名或冻结指纹。先找回原记录。');
      const got=await getBytes(part,entry);
      if(!got?.bytes)throw Error(got?.reason||'请选择断点登记的 '+part+' 原文件。');
      const actual=await hash(got.bytes);
      if(actual!==entry.sha256.toLowerCase())throw Error(part+'.sha256 与所选文件不符。先核原版和差异，保留当前进度。');
      return {actual,bytes:got.bytes};
    }
    const artifact=await frozen('artifact');
    const scope=await scopeHash(cp.task);
    const record={
      kind,task_id:cp.task.id,scope_sha256:scope,artifact_version:cp.artifact.version,
      artifact_sha256:artifact.actual,actor:'',source_ref:'',result:''
    };
    if(kind!=='review')record.target=cp.task.return_to;
    if(kind==='receipt'){
      const dispatch=await frozen('dispatch');
      let text;
      try{text=new TextDecoder('utf-8',{fatal:true}).decode(dispatch.bytes)}
      catch{throw Error('交件记录未能作为 UTF-8 读取。请保留原件，找回可核的对应记录。')}
      const check=evidence(text,'dispatch',scope,cp);
      if(!check.ok)throw Error(check.reason);
      record.dispatch_sha256=dispatch.actual;
    }
    return 'CHECKPOINT '+JSON.stringify(record);
  }
  async function decide(cp,getBytes){
    validate(cp);const log=[];const output=(code,title,owner,action)=>({code,title,owner,action,log});
    if(!Object.values(cp.task).every(required))return output('task-incomplete','先补断点中的任务范围','lead','从原委托核回任务标识、原要求、最新变更和交还入口。已有工作继续保留。');
    const scope=await scopeHash(cp.task);
    async function inspect(k){
      const entry=cp[k];
      if(!entry.file && !entry.sha256)return {state:'undeclared'};
      if(!entry.file||!entry.sha256)return {state:'pending',reason:'已登记了部分信息，需补回另一个字段。'};
      const got=await getBytes(k,entry);
      if(!got||!got.bytes)return {state:'pending',reason:got?.reason||'未提供登记文件的实际字节。'};
      const actual=await hash(got.bytes);log.push({part:k,file:entry.file,actual});
      if(actual!==entry.sha256.toLowerCase())return {state:'changed',reason:'所选实际内容与冻结指纹不同。'};
      return {state:'ok',bytes:got.bytes};
    }
    const a=await inspect('artifact');
    if(a.state==='changed')return output('artifact-changed','文件内容变过，先核差异','lead','请生产席找回原审版本，对照当前变化。只在明确版本与差异后安排增量审核。');
    if(a.state!=='ok'||!required(cp.artifact.version))return output('find-artifact','找回已做的产物或版次','lead',a.reason||'查原委托和生产席现有交件；取回原文件、版本与指纹。单凭缺件不能从零重做。');
    let sent=false;
    for(const k of stages){
      const v=await inspect(k);const label={review:'独立审核',dispatch:'交件',receipt:'实收'}[k];
      if(v.state==='changed')return output('evidence-changed','先核'+label+'记录的变化','lead','从该环的原席或原会话找回冻结凭据。不得用新文件名、旧结论或口头确认补作证明。');
      if(v.state==='pending')return output('find-'+k,'找回已有'+label+'记录','lead',v.reason+' 核回原件再接续。不要重跑已经通过的步骤。');
      if(v.state==='undeclared'){
        if(k==='review'){
          if(cp.dispatch.file||cp.dispatch.sha256||cp.receipt.file||cp.receipt.sha256)return output('reconcile-review','已登记后段，先核遗漏的独审','lead','查回原审核席的同版结论。完整证据恢复前保留已发／实收记录，不重复投递。');
          return output('review-only','只补同版审核','reviewer','先核是否已有同版独审，找到就沿用。确实未审，再由独立审核席打开原件核审；不重做生产。');
        }
        if(k==='dispatch'){
          if(cp.receipt.file||cp.receipt.sha256)return output('reconcile-dispatch','有回执线索，先找原交件','lead','先查原交件与接收回执是否对应，未查清前不补发。');
          return output('delivery-only','只接交件','lead','查询原约定入口是否已有同次交件；已有则补原记录，确实未交才把已审同版交回一次。');
        }
        return output('receipt-only','已交，只核目标是否实收','recipient','目标席在约定入口回执实际收到的文件；沿用原交件，无须再发。');
      }
      let text;try{text=new TextDecoder('utf-8',{fatal:true}).decode(v.bytes)}catch{return output('binding-'+k,label+'原记录未能作为 UTF-8 读取','lead','保留原件，取同一来源可读的记录和指纹。');}
      const e=evidence(text,k,scope,cp);
      if(!e.ok)return output('binding-'+k,label+'记录与断点待核','lead',e.reason+' 回到原始记录核清，再决定下一步。');
      log[log.length-1].source=e.source;
      if(k==='review'&&e.result==='revise')return output('targeted-revision','原审结论为退修，只补退项','producer','按原审核所列问题修订、另存新版本，再核受影响部分。旧版通过项照旧。');
      if(k==='dispatch')sent=true;
    }
    if(sent)return output('complete','已终结，无需再做','lead','当前范围的产物、独审、交件和目标实收证据相互对应。保留这些文件即可。');
  }
  return {validate,ownerId,scopeText,scopeHash,hash,bindingDraft,decide};
})();
