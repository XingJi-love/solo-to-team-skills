# Team definition v1

`format` is `solo-to-team.definition`, and `version` is the string `1.0.0`. The UTF-8 JSON file is a portable project definition. Names and responsibilities are user-authored text. IDs are stable references scoped to their role or group collection. Changing a name does not change an ID.

| Field | Meaning |
| --- | --- |
| `id`, `name` | Team ID and nonempty display name. |
| `roles[]` | Each role has `id`, `name`, `responsibility` and `avatar`. |
| `groups[]` | Each group has `id`, `name`, `purpose` and `members` (role IDs). A team can use zero groups. Each declared group needs at least one member. |
| `workflow.dispatch`, `.produce`, `.review`, `.deliver` | Role IDs with the four workflow responsibilities. Production and independent review must identify different roles. |

A valid ID matches `^[a-z][a-z0-9_-]{0,63}$`. Names are unique within roles and within groups after trimming, NFC normalization and case folding by lowercase conversion. Role and group IDs cannot repeat within their own collection. Each membership and workflow reference must resolve. The format has no permission-grant field. Unknown fields and unsupported versions are rejected rather than silently discarded.

`avatar` is either `null` or an object containing exactly `mime` and `data`. The MIME must be `image/png`, `image/jpeg` or `image/webp`; the data is a complete base64 data URL of the same MIME. Per-image limit: 512 KiB of image bytes, maximum dimension 2048 pixels. The editor checks the signature, dimensions and browser decodability. There are no remote image links. The editor accepts JSON files up to 32 MiB.

Example with no groups or portraits:

```json
{
  "format": "solo-to-team.definition",
  "version": "1.0.0",
  "id": "field-team",
  "name": "Field team",
  "roles": [
    {"id":"lead","name":"Lead","responsibility":"Assign work and return the accepted file.","avatar":null},
    {"id":"producer","name":"Producer","responsibility":"Create the deliverable and revise specific findings.","avatar":null},
    {"id":"reviewer","name":"Reviewer","responsibility":"Open the submitted revision and check the agreed requirements.","avatar":null}
  ],
  "groups": [],
  "workflow":{"dispatch":"lead","produce":"producer","review":"reviewer","deliver":"lead"}
}
```

The included `solo-to-team.team` v1 starter has a different purpose and more fields. On explicit import, the editor maps its labels and responsibilities, group purposes and memberships, the assign/deliver edges and review owner to this format. It does not transfer host settings or convert unrelated legacy metadata. Keep the starter if you need those fields.
