from hermes_tools import delegate_task

run_id = "20260315_214244"
base_dir = f"/Users/peteromalley/Documents/desloppify/.desloppify/subagents/runs/{run_id}"

for i in range(1, 21, 3):
    batch_nums = list(range(i, min(i+3, 21)))
    tasks = []
    for b in batch_nums:
        tasks.append({
            "goal": f"Review batch {b}. Read the prompt at .desloppify/subagents/runs/{run_id}/prompts/batch-{b}.md, follow it exactly, inspect the repository, and write ONLY valid JSON to .desloppify/subagents/runs/{run_id}/results/batch-{b}.raw.txt.",
            "context": "Repository root: /Users/peteromalley/Documents/desloppify. Blind packet: .desloppify/review_packet_blind.json. The prompt file defines the required output schema. Do not edit repository source files. Only write the review result file.",
            "toolsets": ["terminal", "file"]
        })
    print(f"Launching subagents for batches: {batch_nums}")
    results = delegate_task(tasks=tasks)
    print(f"Completed batches {batch_nums}")

print("All batches completed.")
