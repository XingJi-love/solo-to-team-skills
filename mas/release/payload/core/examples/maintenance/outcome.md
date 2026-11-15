# 临时封楼，哪一份通知也得改？ / When one site closes

这是一道合成维修预约题。以下过程据本机测试人员的界面观察和交回文件整理，云端审阅者可核数字与文本，未取得平台运行日志。收到 FIX-4-R0 的回执后，才在首席原对话追加北楼封闭的要求。首席通过生产、审核两席交回了调度表、通知草稿和审核记录。以下内容适合交卷后对照。

| 工单 | 原起点 | 最终作业时间 | 地点 |
|---|---|---|---|
| C 工具车 | 10:00 | 09:00–09:20 | 院内 |
| B 照明 | 09:30 | 09:30–09:50 | 南楼 |
| A 门铃 | 09:00 | 10:00–10:20 | 北楼 |
| D 工具柜 | 10:30 | 10:30–10:50 | 南楼 |

只有北楼封闭，院内工单却也要提前。两项工作共用一个维修班；把 A 移到 10:00，就占用了 C 的原预约。南楼两单各按原时刻执行。独立核算穷举了四个起点的 24 种排列，只有上表同时满足全部约束。

**第一次审核漏了什么？** R1 已排对四项作业。它把记录日期填成了作业生效日期，又在北楼通知里说其他工单不受影响。本机复核人员打开调度表和通知后退回这两项。原生产席修成 R2，原审核席复核，首席在原会话交回三个可打开的文件。R2 把作业日期留待填写，北楼的通知只说明本站调整，院内另有提前到场草稿。交回的是通知草稿。本机观察范围内未见站点外发。

[读交件前对照卡](../../delivery-check/README.md) · [原始题面](01-intake.md) · [变更卡](02-change.md)

## English

This account is based on the local test observer and returned files. Cloud reviewers checked the arithmetic and text; platform run logs were unavailable. One fictional crew handled four jobs across three sites. When the North Building closed until 10:00, job A took job C’s slot, requiring a second notice for the courtyard. Jobs B and D kept their times. Only one of the 24 possible slot assignments met all requirements.

The team’s first version got the times right. Its independent reviewer missed an invented effective date and an overbroad claim that other jobs were unaffected. The person checking the returned files spotted both, requested a targeted fix, and received the revised schedule, draft notices and same-version review in the original chat. The exercise illustrates both the benefit of tracing a change across documents and a limit of independent AI review. The local observer saw draft notices and no dispatch to the sites.
