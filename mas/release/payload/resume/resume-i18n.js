'use strict';
// Presentation only. Values from the checkpoint and source records stay verbatim.
const ResumeEnglish = (() => {
  const staticText = new Map(Object.entries({
    '一人成阵 · 本地续办':'Solo to Team · Offline handoff',
    '下一棒该做什么？':'What happens next?',
    '打开断点和它引用的实物。这里核文件、指出下一棒，所有内容都留在此页，不会派工或发件。':'Open your checkpoint and the files it refers to. This tool checks them locally and shows who can act next.',
    '打开这次的证据':'Open the checkpoint and files',
    '选择 checkpoint.json':'Choose checkpoint.json',
    '选择已保存的文件，可多选':'Choose supporting files (multiple allowed)',
    '先选断点，再选产物及已有的审核、交件或接收记录。':'Choose the checkpoint first. Then select the deliverable and any existing review, dispatch or receipt records.',
    '核收结果':'What the records show',
    '尚未读取断点':'No checkpoint open',
    '本次核到的文件与来源':'Files and source references checked',
    '页面会重算本地 SHA-256。记录的作者和交件是否真的来自所称宿主，需要回到记录给出的原入口核实。':'Each fingerprint is recomputed locally. To verify authorship or a real delivery, open the original location named in the record.',
    '原席出记录 · 复制一条绑定草稿':'Prepare a record · Copy a binding line',
    '由实际出件人使用。选择原始断点和对应文件后，本页复制任务范围、实物指纹和原交还入口。回执中的目标逐字取自断点，说明另写在正文。':'For the person making the record. Select the original checkpoint and matching files. The draft copies the scope, file fingerprint and exact destination. Write any explanation in the record body.',
    '这次由哪一席出记录':'Who is making this record?',
    '审核席 · 独审':'Reviewer · Independent review',
    '首席 · 交件':'Lead · Dispatch',
    '接收席 · 实收':'Recipient · Receipt',
    '只读绑定草稿':'Read-only binding line',
    '复制绑定草稿':'Copy draft line',
    '填写或更新 checkpoint.json':'Create or update checkpoint.json',
    '可以打开已有断点继续填。更换文件时不会自动覆盖已登记指纹。只有核过实际版本、明确要写入新断点时才点“登记这份文件”。':'You can start from an existing checkpoint. Choose “Register this file” only after checking the version; it replaces that entry in your editable copy.',
    '任务标识':'Task ID',
    '交还入口（共同约定的别名）':'Agreed return destination (exact label)',
    '原任务':'Original request',
    '最新变更（确无变更填“无”）':'Latest change (enter “none” if there was no change)',
    '本次范围的 SHA-256':'Scope fingerprint (SHA-256)',
    '先填写上述四项。':'Complete the four task fields above.',
    '产物版次':'Deliverable version',
    '台账中的下一责任席':'Next owner recorded in the checkpoint',
    '首席 · lead':'Lead · lead','生产官 · producer':'Producer · producer','审核官 · reviewer':'Reviewer · reviewer','接收席 · recipient':'Recipient · recipient',
    '台账中的下一具体动作':'Next action recorded in the checkpoint',
    '不可盲重做的项目（每行一条）':'Work to preserve (one item per line)',
    '另存当前断点 JSON':'Download checkpoint copy',
    '保存是下载副本。把核准的断点与原文件放回同一共享文件夹；两端只需访问该文件夹。缺文件时可保留当前记录后继续找回。':'Saving downloads a copy. Keep the agreed checkpoint with the original files in the shared folder. If a file is missing, preserve the current record while locating it.',
    '原件怎样对应这项工作':'How the records bind to this task',
    '展开上方“原席出记录”复制草稿，由原席如实填写并附在原记录正文后，再将该记录的指纹写回断点。格式与开工／换会话短指令见':'Open “Prepare a record”, copy the line and have the actual author complete it beneath the original account. Register the resulting file fingerprint in the checkpoint. For the format and handoff instructions, see the ',
    '使用说明':'English guide',
    '。只有实际接收席才能出具实收记录。没有回执就保留“待接收”。':'. Only the actual recipient can confirm receipt. If it is missing, leave receipt pending.'
  }));
  const names={artifact:'deliverable',review:'independent review',dispatch:'dispatch',receipt:'receipt'};
  const actions={
    'task-incomplete':['Complete the task scope','Recover the task ID, original request, latest change and agreed destination from the original brief. Preserve completed work.'],
    'artifact-changed':['The deliverable changed. Compare versions first.','Ask the producer for the reviewed version. Establish the difference before arranging review of the changes.'],
    'reconcile-review':['A later stage is recorded. Find the original review.','Retrieve the reviewer’s decision for this version. Preserve the dispatch or receipt and avoid duplicate delivery.'],
    'review-only':['Only the independent review is outstanding','Look for an existing review of this exact version. If none exists, have the independent reviewer open and check it. Keep the production work.'],
    'reconcile-dispatch':['A receipt is listed. Find its original dispatch.','Check which dispatch the receipt refers to before sending anything.'],
    'delivery-only':['Only dispatch is outstanding','Check the agreed destination for an existing delivery. Recover its record if it was sent; otherwise deliver the reviewed version there once.'],
    'receipt-only':['Sent. Only the recipient’s confirmation is outstanding.','At the agreed destination, confirm the actual file that arrived and reference the existing dispatch. It does not need to be sent again.'],
    'targeted-revision':['The reviewer requested changes','Have the producer address the findings, save a new version and ask for review of the affected parts. Preserve earlier passes.'],
    complete:['Complete. No further action.','The deliverable, independent review, dispatch and recipient’s receipt match the current scope. Retain these files.']
  };
  const reasons={
    '无法识别这份断点文件的格式或版本。保留原件。':'Unknown checkpoint format or version. Preserve the original.',
    '任务字段不完整。':'The task must include all four text fields.',
    '文件位置须是共享文件夹内的相对名称。':'File names must be relative to the shared folder.',
    '下一棒须含文字字段 owner（席位标签）和 action（此前记载的动作）。':'The next step must include owner and action as text.',
    '不可重做清单须是逐条填写的文字。':'do_not_repeat must contain one nonempty text entry per item.',
    '当前浏览器不能在此页核对 SHA-256。请用支持本地文件的现代浏览器打开。':'Local SHA-256 is unavailable. Open the page in a current browser that supports local files.',
    '记录的席位、任务、当前变更范围、产物版本或指纹未对齐。':'Check the author role and source reference, task ID, scope fingerprint, deliverable version and SHA-256 against the original record.',
    '审核结果不能判为通过或退修。':'review.result must be the reviewer’s own pass or revise decision.',
    'receipt.dispatch_sha256 与登记的交件记录不符。请接收席核对原交件及其更正记录，再按已核的交件指纹登记真实收件，无需重发产物。':'receipt.dispatch_sha256 differs from the recorded dispatch. The recipient can check the original dispatch and any correction, then bind their actual receipt to the verified fingerprint. No resend is needed.',
    '请选择独审、交件或实收。':'Choose review, dispatch or receipt.',
    '请先打开已填完整任务和原交还入口的断点。':'Open a checkpoint with complete task fields and an agreed return destination.',
    '请先核回真实产物的版次。':'Recover the version of the actual deliverable first.',
    '交件记录未能作为 UTF-8 读取。请保留原件，找回可核的对应记录。':'The dispatch record could not be read as UTF-8. Preserve it and locate a readable record from the same source.',
    '已登记了部分信息，需补回另一个字段。':'Only part of this entry is present. Recover its missing file name or fingerprint.',
    '未提供登记文件的实际字节。':'The registered file was not selected.',
    '所选实际内容与冻结指纹不同。':'The selected file differs from its recorded fingerprint.',
    '同名候选超过一份，请只选择确切的文件。':'More than one selected file has that name. Select only the correct one.',
    '查原委托和生产席现有交件；取回原文件、版本与指纹。单凭缺件不能从零重做。':'Recover the original file, version and fingerprint from the brief or producer.',
    '请先重新打开有效断点，避免误存先前记录。':'Open a valid checkpoint before saving a copy.'
  };
  function explain(message){
    let m=message.replace(/ 回到原始记录核清，再决定下一步。$| 核回原件再接续。不要重跑已经通过的步骤。$/u,'');
    if(reasons[m])return reasons[m];
    const exact=m.match(/^(dispatch|receipt)\.target 不符。断点原值 ("(?:[^"\\]|\\.)*")，原记录写作 ("(?:[^"\\]|\\.)*"|（未登记）)。/su);
    if(exact){
      const [_,stage,want,got]=exact;
      const detail=(got==='（未登记）'?'(missing)':got);
      const fix=stage==='dispatch'?'The sender should verify where the file actually went. If delivered correctly, preserve the original, move commentary into the body, correct only the binding and register the corrected dispatch fingerprint. Keep the review and original delivery; no resend is needed. If it went elsewhere, investigate the actual destination.':'The recipient should check the original destination and actual file received. If only the label differs, correct the receipt binding and register its new fingerprint. No resend is needed.';
      return stage+'.target mismatch. Checkpoint: '+want+'. Record: '+detail+'. '+fix;
    }
    const patterns=[
      [/^(artifact|review|dispatch|receipt) 的文件字段无效。$/u,(_,k)=>k+' contains invalid file fields.'],
      [/^(artifact|review|dispatch|receipt) 的 SHA-256 应为 64 位十六进制字符。$/u,(_,k)=>k+'.sha256 must contain 64 hexadecimal characters.'],
      [/^(?:记录不完整或有冲突。)?需要一条明确的 (review|dispatch|receipt) 绑定行，以及实际来源记录正文。$/u,(_,k)=>'The original record needs source text and exactly one CHECKPOINT line of kind '+k+'.'],
      [/^(dispatch|receipt)\.result 未写明本席的实际结果。请原席查实行为与出处；草稿不能作凭据。$/u,(_,k)=>'Verify '+k+'.result with the original author and source. An unsigned draft cannot serve as evidence.'],
      [/^缺少 (artifact|dispatch) 的文件名或冻结指纹。先找回原记录。$/u,(_,k)=>'Find the original '+names[k]+' file name and fingerprint first.'],
      [/^请选择断点登记的 (artifact|dispatch) 原文件。$/u,(_,k)=>'Select the original '+names[k]+' file listed in the checkpoint.'],
      [/^(artifact|dispatch)\.sha256 与所选文件不符。先核原版和差异，保留当前进度。$/u,(_,k)=>k+'.sha256 differs from the selected file. Preserve progress and compare the original version.'],
      [/^尚未选到登记的文件，请找回 ([\s\S]+)。$/u,(_,file)=>'Locate and select the registered file: '+file+'.'],
      [/^记录不完整或有冲突。([\s\S]+)$/u,(_,detail)=>'The source record is incomplete or contains conflicting bindings. '+detail]
    ];
    for(const [pattern,toEnglish] of patterns){const values=m.match(pattern);if(values)return toEnglish(...values)}
    return m;
  }
  function verdict(r){
    if(actions[r.code])return actions[r.code];
    if(r.code==='find-artifact')return ['Locate the existing deliverable or version',explain(r.action)];
    if(r.code==='evidence-changed'){
      const stage=r.log.at(-1)?.part;
      return ['Check the changed '+(names[stage]||'evidence')+' record','Recover the frozen record from its original author or conversation before acting.'];
    }
    const [type,kind]=r.code.split('-');
    if(type==='find')return ['Find the existing '+names[kind]+' record',explain(r.action)+' Resume from that record.'];
    if(type==='binding'){
      if(r.title.includes('UTF-8'))return ['The '+names[kind]+' record could not be read as UTF-8','Preserve the original and recover a readable record from the same source.'];
      return ['Check the '+names[kind]+' binding',explain(r.action)];
    }
    return [r.title,r.action];
  }
  return {staticText,explain,verdict};
})();
