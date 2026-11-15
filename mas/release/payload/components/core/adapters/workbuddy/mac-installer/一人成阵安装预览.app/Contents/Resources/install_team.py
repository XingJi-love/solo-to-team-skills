"""Offline macOS adapter for the specific WorkBuddy 5.9.3 team package."""
import argparse
import copy
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import uuid
import zipfile

TEAM = "solo-to-team-delivery"
SOURCE = "./plugins/" + TEAM
HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / (TEAM + ".zip")
ARCHIVE_SHA = "5203211d20839fec27a276dd22bb0e99dd5510e99a952815182dd24a7fb905d4"
TOOL_SHA = "b2dd1a0141c2dc88ed7203246335fd261eca97a17f91f4e280d3ce8b10a65b1e"
APP = Path("/Applications/WorkBuddy.app")
TOOL = APP / "Contents/Resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/expert-manager/scripts/register_expert.py"
MANIFEST = Path(".codebuddy-plugin/marketplace.json")
EMPTY = {"name": "my-experts", "description": "my-experts marketplace (auto-generated)", "plugins": []}


class Stop(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Stop(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def plain(path):
    # Reject symlinks from the home/config root through every component.
    for parent in [path, *path.parents]:
        require(not parent.is_symlink(), "发现链接路径，已停止：" + str(parent))


def read_file(path):
    plain(path)
    if not path.exists():
        return None
    require(path.is_file(), "预期是普通文件：" + str(path))
    return path.read_bytes()


def require_writable_catalog(path):
    st = path.stat()
    require(st.st_nlink == 1 and st.st_mode & 0o222 and os.access(path, os.W_OK),
            "登记表受保护或有其他硬链接，已保留原状。")


def unique(pairs):
    out = {}
    for key, val in pairs:
        require(key not in out, "登记表含重复字段，已保留原文件。")
        out[key] = val
    return out


def parse(data):
    parsed = json.loads(data.decode("utf-8"), object_pairs_hook=unique)
    require(isinstance(parsed, dict) and isinstance(parsed.get("plugins"), list)
            and all(isinstance(x, dict) for x in parsed["plugins"]), "现有专家登记格式无法安全合并。")
    return parsed


def official():
    plain(TOOL)
    info = plistlib.loads((APP / "Contents/Info.plist").read_bytes())
    require(info.get("CFBundleIdentifier") == "com.tencent.workbuddy.mac"
            and info.get("CFBundleShortVersionString") == "5.9.3"
            and digest(TOOL.read_bytes()) == TOOL_SHA,
            "当前客户端或注册工具与已核 WorkBuddy 5.9.3 不一致。")


def payload():
    require(digest(ARCHIVE.read_bytes()) == ARCHIVE_SHA, "安装包与冻结的 0.1.0 不一致。")
    with zipfile.ZipFile(ARCHIVE) as z:
        return {Path(p).relative_to(TEAM).as_posix(): z.read(p) for p in z.namelist()}


def identical(folder, files, allow_marker=False):
    if not folder.is_dir() or folder.is_symlink():
        return False
    expected_dirs = {p.as_posix() for key in files for p in Path(key).parents if p != Path(".")}
    actual = set()
    for item in folder.rglob("*"):
        key = item.relative_to(folder).as_posix()
        if item.is_symlink():
            return False
        if item.is_dir() and key in expected_dirs:
            continue
        if allow_marker and key == ".created-by-session" and item.is_file():
            continue
        if not item.is_file() or key not in files or item.read_bytes() != files[key]:
            return False
        actual.add(key)
    return actual == set(files)


def refs(manifest):
    out = []
    for item in manifest["plugins"]:
        src = item.get("source")
        # In an alternate marketplace format a source may be a structured locator.
        if isinstance(src, dict):
            src = src.get("path") or src.get("url")
        match_source = False
        if isinstance(src, str):
            normal = os.path.normpath(src).casefold()
            match_source = (normal == "plugins/" + TEAM or normal.endswith("/plugins/" + TEAM))
        if str(item.get("name", "")).casefold() == TEAM or match_source:
            out.append(item)
    return out


def replace_mac(src, dst, flags):
    api = ctypes.CDLL(None, use_errno=True).renamex_np
    api.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    if api(os.fsencode(src), os.fsencode(dst), flags) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(dst))


def commit(path, before, after):
    """Publish atomically. On Darwin exchange, compare what was actually displaced."""
    plain(path)
    require(read_file(path) == before, "登记表在核对中已变动，请重新预览。")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent, prefix=".solo-team-") as temp:
        old = Path(temp) / "exchange"
        if after is None:
            # Only remove an unchanged empty catalog originally created by this installer.
            require_writable_catalog(path)
            replace_mac(path, old, 4)
            if old.read_bytes() != before:
                replace_mac(old, path, 4)
                raise Stop("登记表在撤回期间有变动，已恢复。")
            return
        old.write_bytes(after)
        if before is None:
            os.chmod(old, 0o600)
            replace_mac(old, path, 4)  # RENAME_EXCL
            return
        require_writable_catalog(path)
        copier = ctypes.CDLL(None, use_errno=True).copyfile
        copier.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_uint]
        # Darwin COPYFILE_METADATA includes mode/ownership, ACL and extended attributes.
        if copier(os.fsencode(path), os.fsencode(old), None, 7 | (3 << 18)) != 0:
            raise Stop("原登记表的权限属性不能完整保留，已停止。")
        os.utime(old, None)
        replace_mac(old, path, 2)  # RENAME_SWAP
        if old.read_bytes() != before:
            replace_mac(old, path, 2)
            raise Stop("发现并发改动，已恢复原登记表。")


def edit_plugins(raw, entry, add):
    """Keep other entries, top-level metadata and their original formatting byte-for-byte."""
    original = parse(raw)
    s = raw.decode("utf-8")
    dec = json.JSONDecoder()
    def skip(i):
        while i < len(s) and s[i].isspace():
            i += 1
        return i
    i = skip(0) + 1
    while True:
        key, i = dec.raw_decode(s, skip(i))
        i = skip(skip(i) + 1)
        if key == "plugins":
            break
        _, i = dec.raw_decode(s, i)
        i = skip(i) + 1
    start = i + 1
    i = skip(start)
    spans = []
    while s[i] != "]":
        val, end = dec.raw_decode(s, i)
        spans.append((i, end, val))
        i = skip(end)
        if s[i] == "]":
            break
        i = skip(i + 1)
    expected = copy.deepcopy(original)
    if add:
        expected["plugins"].append(entry)
        pos = spans[-1][1] if spans else start
        delta = ("," if spans else "") + json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
        s = s[:pos] + delta + s[pos:]
    else:
        k = next(n for n, (_, _, val) in enumerate(spans) if val == entry)
        a, b, _ = spans[k]
        if k:
            a = spans[k-1][1]
        elif len(spans) > 1:
            b = spans[1][0]
        s = s[:a] + s[b:]
        expected["plugins"].pop(k)
    out = s.encode("utf-8")
    require(parse(out) == expected, "登记表增量核对失败。")
    return out


def official_delta(files, raw):
    """The vendor registrar authors the entry; never run it directly on the live catalog."""
    with tempfile.TemporaryDirectory() as td:
        market = Path(td) / "my-experts"
        target = market / "plugins" / TEAM
        extract(files, target)
        if raw is not None:
            (market / MANIFEST).parent.mkdir(parents=True)
            (market / MANIFEST).write_bytes(raw)
        result = subprocess.run([sys.executable, "-I", "-B", str(TOOL), str(target),
                                 "--marketplace-dir", str(market)], capture_output=True, text=True,
                                env={"PATH": "/usr/bin:/bin", "HOME": td, "WORKBUDDY_CONFIG_DIR": td}, timeout=30)
        require(result.returncode == 0, "WorkBuddy 官方注册工具未通过。")
        new = (market / MANIFEST).read_bytes()
        parsed = parse(new)
        entry = parsed["plugins"][-1]
        expected = copy.deepcopy(parse(raw) if raw is not None else EMPTY)
        expected["plugins"].append(entry)
        require(parsed == expected and entry["name"] == TEAM and entry["source"] == SOURCE
                and identical(target, files), "官方工具输出超出这一团的增量，未登记。")
        return entry, new


def extract(files, target):
    target.mkdir(parents=True)
    for key, value in files.items():
        dest = target / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(value)


class Installer:
    def __init__(self, config):
        self.market = config / "plugins/marketplaces/my-experts"
        self.dest = self.market / "plugins" / TEAM
        self.man = self.market / MANIFEST
        self.state = config / ".solo-to-team-installer-v1"
        self.note = self.state / "active.json"
        for path in (self.dest, self.man, self.note):
            plain(path)
        self.files = payload()
        desc = json.loads(self.files[".codebuddy-plugin/plugin.json"])["description"]
        self.entry = {"name": TEAM, "source": SOURCE, "description": desc}

    def state_now(self):
        raw = read_file(self.man)
        entries = refs(parse(raw)) if raw is not None else []
        if self.dest.parent.is_dir():
            for name in os.listdir(self.dest.parent):
                require(name.casefold() != TEAM or name == TEAM, "发现仅大小写不同的同名目录。")
        note = read_file(self.note)
        rec = json.loads(note) if note else None
        if rec:
            require(rec.get("package") == ARCHIVE_SHA and rec.get("entry") == self.entry
                    and uuid.UUID(rec["id"]).hex == rec["id"], "本工具安装凭据无法验实，已停止。")
        require(not entries or entries == [self.entry], "发现同名异源、字段不同或重复登记，已保留原样。")
        if self.dest.exists():
            require(identical(self.dest, self.files, allow_marker=rec is None),
                    "目标目录有异源文件或使用后的改动，已保留原样。")
            if rec:
                require(self.ours(self.dest, rec), "目录已被换过，已保留原样。")
            elif not entries:
                raise Stop("已有未经登记的同名目录，保留原样。")
        elif entries and not rec:
            raise Stop("已有其他来源的登记，目录缺失，保留原样。")
        return raw, entries, rec

    @staticmethod
    def ours(folder, rec):
        st = folder.stat()
        return [st.st_dev, st.st_ino] == rec["directoryIdentity"]

    def preview(self):
        _, entries, rec = self.state_now()
        if rec:
            if self.dest.exists() and entries:
                return "本工具已安装。重复安装将跳过，可选择撤回。"
            return "上次安装或撤回中断，可继续安装或撤回本次新增。"
        if entries:
            return "相同版本原已存在。重复安装将跳过；它不属于本安装器，无法撤回。"
        return "可以安装。会增加本地三席专家团及一条登记。"

    def save_receipt(self, rec):
        commit(self.note, None, json.dumps(rec, ensure_ascii=False).encode())

    def install(self):
        raw, entries, rec = self.state_now()
        if entries and self.dest.is_dir():
            return "相同版本已经登记。此次没有重复安装。"
        if not entries:
            entry, generated = official_delta(self.files, raw)
            require(entry == self.entry, "官方工具生成了意外的登记内容。")
        if not rec:
            key = uuid.uuid4().hex
            txn = self.state / key
            staged = txn / "staged"
            extract(self.files, staged)
            st = staged.stat()
            rec = {"id": key, "package": ARCHIVE_SHA, "entry": self.entry,
                   "directoryIdentity": [st.st_dev, st.st_ino], "initiallyAbsent": raw is None,
                   "initialGenerated": digest(generated) if raw is None else None}
            self.save_receipt(rec)
        txn = self.state / rec["id"]
        if not self.dest.exists():
            staged = next((p for p in [txn / "staged", txn / "withdrawn"] if p.is_dir()), None)
            require(staged and self.ours(staged, rec) and identical(staged, self.files),
                    "中断状态的暂存目录无法验实，已保留现场。")
            self.dest.parent.mkdir(parents=True, exist_ok=True)
            replace_mac(staged, self.dest, 4)
        if not entries:
            commit(self.man, raw, generated if raw is None else edit_plugins(raw, entry, True))
        _, actual, installed_receipt = self.state_now()
        require(actual == [self.entry] and self.dest.is_dir() and installed_receipt == rec,
                "登记后的文件与条目未达到同一版本，保留现场。")
        return "WorkBuddy 官方工具已生成登记，冻结的 10 个文件已核对。请在「我的专家」中查看；界面出现才算可召唤。"

    def undo(self):
        raw, entries, rec = self.state_now()
        if not rec:
            return "没有本工具新增的活动安装。已保留现有专家。"
        txn = self.state / rec["id"]
        if entries:
            next_data = edit_plugins(raw, self.entry, False)
            if rec["initiallyAbsent"] and digest(raw) == rec["initialGenerated"]:
                next_data = None
            commit(self.man, raw, next_data)
        if self.dest.exists():
            require(self.ours(self.dest, rec) and identical(self.dest, self.files),
                    "撤回期间团队文件发生变化，已保留。")
            withdrawn = txn / "withdrawn"
            replace_mac(self.dest, withdrawn, 4)
            if not self.ours(withdrawn, rec) or not identical(withdrawn, self.files):
                replace_mac(withdrawn, self.dest, 4)
                raise Stop("撤回期间团队文件发生变化，已放回原位。")
        replace_mac(self.note, txn / "withdrawal-receipt.json", 4)
        return "已撤回本次新增。已安装文件收入本次凭据目录的 withdrawn，未删除其他专家。"


def run(action, config, live=True):
    official()
    inst = Installer(config)
    if action == "preview":
        return inst.preview()
    # No state directory or other change for a pre-existing copy, including a second run.
    current = inst.preview()
    if action == "install" and (current.startswith("相同版本原已") or current.startswith("本工具已安装")):
        return "相同版本已经登记。此次没有重复安装。"
    if action == "undo" and not inst.note.exists():
        return "没有本工具新增的活动安装。已保留现有专家。"
    if inst.man.exists():
        require_writable_catalog(inst.man)
    if live:
        active = subprocess.run(["/usr/bin/pgrep", "-x", "WorkBuddy"], capture_output=True)
        require(active.returncode == 1, "请先自行结束 WorkBuddy 中正在进行的任务并退出客户端，再确认安装或撤回。")
    inst.state.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = inst.state / "installer.lock"
    plain(lock_path)
    with open(lock_path, "a+b") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Stop("另一个安装窗口正在修改本团，请稍后重新预览。")
        return inst.install() if action == "install" else inst.undo()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("preview", "install", "undo"))
    p.add_argument("--test-root")
    ns = p.parse_args()
    if ns.test_root:
        root = Path(ns.test_root).resolve()
        tmp = Path(tempfile.gettempdir()).resolve()
        require(root != tmp and tmp in root.parents, "演练只接受系统临时目录内的独立路径。")
    else:
        root = Path(os.environ.get("WORKBUDDY_CONFIG_DIR") or (Path.home() / ".workbuddy")).expanduser()
        require(root.is_absolute(), "WorkBuddy 配置位置不明确。")
    print(run(ns.action, root, live=not ns.test_root))


if __name__ == "__main__":
    try:
        main()
    except (Stop, OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile) as exc:
        print("未完成操作。" + str(exc), file=sys.stderr)
        sys.exit(1)

