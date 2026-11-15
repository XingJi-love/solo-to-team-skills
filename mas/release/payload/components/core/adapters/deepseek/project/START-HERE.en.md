# Start a three-role project in DeepSeek Harness

Unzip the whole download. In DeepSeek Harness choose **Add workspace**, then select the folder named **一人成阵-DSH**. This Chinese name is the team project. It contains `inputs` and the hidden `.dsh` folder. The outer extraction directory and the hidden folder are different locations. Leave the neighbouring **试用者第二步** folder outside this workspace; it contains the change to send later.

1. Start a new chat in **一人成阵-DSH**. Type `/solo-to-team` and select the project skill. If it cannot be found, check your workspace name and make sure your extraction preserved the hidden `.dsh/skills/solo-to-team/SKILL.md` file.
2. Tell the lead: “Open the starting brief in inputs. Please acknowledge the draft version, budget and constraints. I will send a change in this same chat.” The brief contains both languages. When the lead confirms MAP-20-R1, open the card inside **试用者第二步**, and send its English change text to the same chat.
3. Let production prepare the plan and a separate reviewer check it. Open the final plan and review record in the original chat. Check the headcount, budget and that the review names the delivered revision.

Use a configured DeepSeek Harness and your own available model. In the local 0.2.1-rc.5 desktop run, the default subagent tools supported separate production and review. The team skill is project-local. The user-visible workflow can depend on which tools your instance exposes. Persistent DS Bot identities use a separate adapter.
