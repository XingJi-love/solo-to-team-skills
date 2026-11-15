"""Recreate the ordinary ZIP layouts embedded in the MAS package from independent source files.

One-time import: record_zip(original_bytes, store_leaf). The callback receives a tuple
of member names (including enclosing archive names) plus the raw leaf bytes, and
returns a source reference. Store references in a checked-in JSON recipe.

Normal build: build_zip(recipe, read_leaf). The callback takes a source reference and
returns independent source bytes. No original archive or compressed payload is needed.
The default checks all original member and archive SHA-256s. For a deliberate source
change use verify=False, then review and record the SHA-256 of the new artifact.
"""
import hashlib
import io
import posixpath
import stat
import struct
import zipfile
import zlib

FORMAT = "mas-zip-layout-v1"
HEADER = struct.Struct("<4s5H3I2H")
LEVELS = (6, 9, 7, 8, 5, 4, 3, 2, 1, 0)
MAX_NESTING = 4


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _safe_name(name):
    if (not isinstance(name, str) or not name or name.startswith("/") or "\\" in name
            or ":" in name or any(ord(c) < 32 for c in name)
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError(f"Invalid ZIP member name: {name!r}")


def _compression_levels(data, compressed, method):
    if method == zipfile.ZIP_STORED:
        if data != compressed:
            raise ValueError("Stored data differs from its ZIP bytes")
        return [None]
    if method != zipfile.ZIP_DEFLATED:
        raise ValueError(f"Unsupported compression method: {method}")
    matches = []
    for level in LEVELS:
        obj = zlib.compressobj(level, zlib.DEFLATED, -15)
        if obj.compress(data) + obj.flush() == compressed:
            matches.append(level)
    if not matches:
        raise ValueError("Installed zlib cannot reproduce this compressed stream")
    return matches


def _record(data, store_leaf, prefix):
    if len(prefix) >= MAX_NESTING:
        raise ValueError("Unexpected ZIP nesting")
    entries, pending, names = [], [], set()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.comment:
            raise ValueError("This recipe supports empty archive comments")
        for info in archive.infolist():
            _safe_name(info.filename)
            if info.filename in names:
                raise ValueError(f"Duplicate ZIP member: {info.filename}")
            names.add(info.filename)
            ftype = stat.S_IFMT(info.external_attr >> 16)
            if (info.is_dir() or ftype not in (0, stat.S_IFREG)
                    or info.flag_bits not in (0, 0x800) or info.extra or info.comment):
                raise ValueError(f"Unsupported special file or metadata: {info.filename}")
            at = info.header_offset
            local = HEADER.unpack_from(data, at)
            if local[0] != b'PK\x03\x04' or local[-1]:
                raise ValueError(f"Unexpected local header: {info.filename}")
            begin = at + HEADER.size + local[-2] + local[-1]
            raw = archive.read(info)
            compressed = data[begin:begin + info.compress_size]
            levels = _compression_levels(raw, compressed, info.compress_type)
            member = dict(name=info.filename, timestamp=list(info.date_time),
                          method=info.compress_type, system=info.create_system,
                          created=info.create_version, extract=info.extract_version,
                          external=info.external_attr, internal=info.internal_attr,
                          sha256=_sha(raw))
            path = (*prefix, info.filename)
            if posixpath.splitext(info.filename)[1].lower() == ".zip":
                member["archive"] = _record(raw, store_leaf, path)
            else:
                ref = store_leaf(path, raw)
                if not isinstance(ref, str) or not ref:
                    raise ValueError(f"No source reference returned for {path!r}")
                member["source"] = ref
            entries.append(member)
            pending.append(levels)
    deflated = [set(ls) for ls in pending if ls != [None]]
    common = set.intersection(*deflated) if deflated else set()
    default = next((n for n in LEVELS if n in common), None)
    for member, choices in zip(entries, pending):
        member["level"] = default if default in choices else choices[0]
    return {"format": FORMAT, "sha256": _sha(data), "members": entries}


def record_zip(data, store_leaf):
    return _record(data, store_leaf, ())


def build_zip(recipe, read_leaf, *, verify=True):
    def build(current, depth):
        if current.get("format") != FORMAT or depth >= MAX_NESTING:
            raise ValueError("Unsupported ZIP recipe or nesting")
        dest = io.BytesIO()
        names = set()
        with zipfile.ZipFile(dest, "w", allowZip64=False) as archive:
            for member in current["members"]:
                name = member["name"]
                _safe_name(name)
                if name in names or ("archive" in member) == ("source" in member):
                    raise ValueError(f"Duplicate or ambiguous source: {name}")
                names.add(name)
                if "archive" in member:
                    raw = build(member["archive"], depth+1)
                else:
                    raw = read_leaf(member["source"])
                if verify and _sha(raw) != member["sha256"]:
                    raise ValueError(f"Source fingerprint mismatch: {name}")
                entry = zipfile.ZipInfo(name, tuple(member["timestamp"]))
                entry.create_system = member["system"]
                entry.create_version = member["created"]
                entry.extract_version = member["extract"]
                entry.external_attr = member["external"]
                entry.internal_attr = member["internal"]
                # zipfile determines the UTF-8 flag from the actual filename.
                archive.writestr(entry, raw, compress_type=member["method"],
                                 compresslevel=member["level"])
        data = dest.getvalue()
        if verify and _sha(data) != current["sha256"]:
            raise ValueError("Rebuilt ZIP differs from the frozen SHA-256. Check recipe, Python and zlib versions.")
        return data
    return build(recipe, 0)
