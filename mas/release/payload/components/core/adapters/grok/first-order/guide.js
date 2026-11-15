"use strict";
const english = document.documentElement.lang === "en";
const t = (zh, en) => english ? en : zh;
const roles = ["lead", "producer", "reviewer"];
const textOf = id => document.getElementById(id).textContent.trim();
function assignment() {
  const seen = new Set(), lines = [], cards = [];
  for (const role of roles) {
    const choice = document.getElementById("mode-" + role), input = document.getElementById("name-" + role);
    const mode = choice.value, name = input.value.trim().normalize("NFC");
    if (!mode || !name) { (mode ? input : choice).focus(); throw new Error(t("请逐席选好动作，并填写该 Bot 在 Grok 里的名称。", "Choose an action and enter each Bot’s name first.")); }
    if (/[\u0000-\u001f\u007f]/u.test(name) || name.length > 80) { input.focus(); throw new Error(t("请使用界面上的简短单行名称。", "Use the short single-line display name shown in Grok.")); }
    const key = name.toLocaleLowerCase();
    if (seen.has(key)) { input.focus(); throw new Error(t("三个岗位要指定三个不同的 Bot。", "Choose a different Bot for each role.")); }
    seen.add(key);
    lines.push(textOf("label-" + role) + " — " + name + " — " + choice.selectedOptions[0].textContent.trim());
    if (mode !== "keep") cards.push(textOf("role-" + role));
  }
  return [textOf("confirm-intro"), ...lines, textOf("confirm-limit"), ...cards].join("\n\n");
}
function showStatus(button, s) { button.parentElement.querySelector(".status").textContent = s; }
async function copy(button, text) {
  const parent = button.parentElement;
  if (parent.querySelector("textarea")) parent.querySelector("textarea").remove();
  try {
    await navigator.clipboard.writeText(text);
    showStatus(button, t("已复制。请到自己对应的 Grok 对话粘贴，检查后发送。", "Copied. Paste into your own matching Grok chat, review, then send."));
  } catch {
    const box = document.createElement("textarea"); box.rows = 5; box.className = "manual";
    box.setAttribute("aria-label",t("已选中待复制文字","Selected text to copy")); box.value = text;
    parent.appendChild(box); box.focus(); box.select();
    showStatus(button, t("文字已选中。按 ⌘C（Windows 用 Ctrl+C）或长按复制。", "Text selected. Press ⌘C (Ctrl+C on Windows), or long-press and copy."));
  }
}
document.querySelectorAll("[data-copy]").forEach(button => {
  button.addEventListener("click", async () => {
    let value;
    try { value = button.dataset.copy === "config" ? assignment() : textOf(button.dataset.copy); }
    catch (error) { showStatus(button, error.message); return; }
    await copy(button, value);
  });
});

