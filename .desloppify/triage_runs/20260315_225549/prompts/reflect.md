You are a triage analysis subagent with full codebase access.
Your job is to complete the **REFLECT** stage of triage planning.

Repo root: /Users/peteromalley/Documents/hermes-agent

## Standards

You are expected to produce **exceptional** work. The output of this triage becomes the
actual plan that an executor follows — if you are lazy, vague, or sloppy, real work gets
wasted. Concretely:

- **Read the actual source code.** Every opinion you form must come from reading the file,
  not from reading the issue title. Issues frequently exaggerate, miscount, or describe
  code that has already been fixed. Trust nothing until you verify it.
- **Have specific opinions.** "This seems like it could be an issue" is worthless. "This is
  a false positive because line 47 already uses the pattern the issue suggests" is useful.
- **Do the hard thinking.** If two issues seem related, figure out WHY. If something should
  be skipped, explain the specific reason for THIS issue, not a generic category.
- **Don't take shortcuts.** Reading 5 files and extrapolating to 30 is lazy. Read all 30.
  If you have too many, use subagents to parallelize — don't skip.
- The prompt below already contains the authoritative stage contract and prior reports.
  Do NOT search old triage run artifacts for alternate instructions unless you hit a
  concrete mismatch you need to explain.

## Output Contract

- **Do NOT run any `desloppify` commands.**
- **Do NOT debug, repair, reinstall, or inspect the `desloppify` CLI/environment.**
- **Do NOT mutate `plan.json` directly or indirectly.**
- Use shell/read-only repo inspection as needed, but your only deliverable is a plain-text
  stage report for the orchestrator to record and confirm.
- If the prompt mentions CLI commands, treat them as background context for the orchestrator,
  not instructions for you to execute.


## Prior Stage Reports


### OBSERVE Report
## Dimensions: logic_clarity, low_level_elegance, cross_module_architecture

- hash: review::.::holistic::cross_module_architecture::registry_violates_own_contract
  verdict: genuine
  verdict_reasoning: The documented contract is explicit in both [AGENTS.md](/Users/peteromalley/Documents/hermes-agent/AGENTS.md) and [website/docs/developer-guide/adding-tools.md](/Users/peteromalley/Documents/hermes-agent/website/docs/developer-guide/adding-tools.md): handlers must return JSON strings. `ToolRegistry.dispatch()` in [tools/registry.py](/Users/peteromalley/Documents/hermes-agent/tools/registry.py) catches exceptions and returns JSON on failure, but it does not validate successful handler returns at all. If a handler accidentally returns a raw dict/string/object, the registry passes it through unchanged. That means the central registry does not actually enforce the contract it tells all tool authors to follow. Tests in [tests/tools/test_registry.py](/Users/peteromalley/Documents/hermes-agent/tests/tools/test_registry.py) only cover the happy path where handlers already return JSON, so this gap is real and currently unguarded.
  files_read: [/Users/peteromalley/Documents/hermes-agent/tools/registry.py, /Users/peteromalley/Documents/hermes-agent/website/docs/developer-guide/adding-tools.md, /Users/peteromalley/Documents/hermes-agent/AGENTS.md, /Users/peteromalley/Documents/hermes-agent/tests/tools/test_registry.py]
  recommendation: Add a small enforcement layer in `dispatch()` that rejects or wraps non-string / non-JSON returns, and add a regression test for a handler that returns a raw dict.

- hash: review::.::holistic::logic_clarity::dead_code_checkpoint_manager
  verdict: genuine
  verdict_reasoning: In `CheckpointManager.list_checkpoints()` there are two consecutive `_run_git()` calls in [tools/checkpoint_manager.py](/Users/peteromalley/Documents/hermes-agent/tools/checkpoint_manager.py). The first assigns `ok, stdout, _` using a `--no-walk=unsorted`/`HEAD` command, then those variables are immediately overwritten by a second `git log` call before any branch can inspect the first result. The inline comment even says “Simpler: just use regular log”, which confirms the first call is leftover dead code rather than intentional fallback logic.
  files_read: [/Users/peteromalley/Documents/hermes-agent/tools/checkpoint_manager.py, /Users/peteromalley/Documents/hermes-agent/run_agent.py]
  recommendation: Remove the first `_run_git()` invocation and keep the single regular `git log` path.

- hash: review::.::holistic::logic_clarity::duplicated_dead_countdown_check
  verdict: genuine
  verdict_reasoning: In [cli.py](/Users/peteromalley/Documents/hermes-agent/cli.py) around the clarify polling loop, the countdown refresh condition is duplicated back-to-back with identical bodies: `if now - _last_countdown_refresh >= 5.0: ... self._invalidate()` appears twice in succession. Because the first branch updates `_last_countdown_refresh`, the second branch is dead on every execution. This is not just stylistic duplication; the second check is unreachable after the first runs.
  files_read: [/Users/peteromalley/Documents/hermes-agent/cli.py]
  recommendation: Delete the second duplicate `if now - _last_countdown_refresh >= 5.0` block.

- hash: review::.::holistic::logic_clarity::identical_branches_skills_sync
  verdict: not-worth-it
  verdict_reasoning: The claimed duplication is real but minor. In [tools/skills_sync.py](/Users/peteromalley/Documents/hermes-agent/tools/skills_sync.py), the `if not origin_hash:` branch increments `skipped += 1` in both the `user_hash == bundled_hash` and `else` cases. The behavior is intentionally the same because the branch is preserving a safe migration baseline for old v1 manifests while the comments explain the two distinct meanings: “already in sync” vs “cannot tell whether user modified or bundle changed.” Collapsing it would save a couple lines but make the migration reasoning slightly less explicit.
  files_read: [/Users/peteromalley/Documents/hermes-agent/tools/skills_sync.py]
  recommendation: Leave it unless someone is already touching this migration branch; at most, replace the inner conditional with one `skipped += 1` and keep the explanatory comments.

- hash: review::.::holistic::logic_clarity::identical_branches_telegram_document
  verdict: false-positive
  verdict_reasoning: I checked the current `send_document()` implementation in [gateway/platforms/telegram.py](/Users/peteromalley/Documents/hermes-agent/gateway/platforms/telegram.py). There is no identical-branch structure in that method. The control flow is: early return if `_bot` is missing, early return if the file path is missing, normal send path, and exception fallback to the base adapter. Those branches do different things. The nearby `send_video()` method has a similar shape, but that is normal method-level consistency, not “identical branches” within `send_document()`.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/platforms/telegram.py]
  recommendation: No change needed for this specific issue.

- hash: review::.::holistic::logic_clarity::identical_branches_uninstall
  verdict: genuine
  verdict_reasoning: In [hermes_cli/uninstall.py](/Users/peteromalley/Documents/hermes-agent/hermes_cli/uninstall.py), the branch checking whether the install lives under `~/.hermes/` has identical bodies on both sides: both branches call `shutil.rmtree(project_root)` and then `log_success(f"Removed {project_root}")`. The condition currently communicates caution, but it does not alter behavior at all.
  files_read: [/Users/peteromalley/Documents/hermes-agent/hermes_cli/uninstall.py]
  recommendation: Collapse the conditional to one removal path, or introduce genuinely different safety behavior if the distinction matters.

- hash: review::.::holistic::low_level_elegance::defensive_hasattr_after_init
  verdict: exaggerated
  verdict_reasoning: There are several `hasattr` checks in [tools/delegate_tool.py](/Users/peteromalley/Documents/hermes-agent/tools/delegate_tool.py), but they are not all pointless. For real `AIAgent` instances, `_client_kwargs` and `_active_children` are initialized in [run_agent.py](/Users/peteromalley/Documents/hermes-agent/run_agent.py), so the guards are redundant in the mainline production path. But `delegate_task()` is also exercised with mocks and looser parent-like objects in [tests/tools/test_delegate.py](/Users/peteromalley/Documents/hermes-agent/tests/tools/test_delegate.py), and the function signature does not hard-require a concrete `AIAgent` type. That makes the guards at least partially intentional compatibility code rather than pure clutter. The issue overstates this as a clear elegance defect.
  files_read: [/Users/peteromalley/Documents/hermes-agent/tools/delegate_tool.py, /Users/peteromalley/Documents/hermes-agent/run_agent.py, /Users/peteromalley/Documents/hermes-agent/tests/tools/test_delegate.py]
  recommendation: Only remove these guards if the code is tightened to require a real `AIAgent`; otherwise leave them or replace them with one clearer helper for optional parent capabilities.

- hash: review::.::holistic::low_level_elegance::patch_parser_duplicated_flush
  verdict: false-positive
  verdict_reasoning: I read the parser state transitions in [tools/patch_parser.py](/Users/peteromalley/Documents/hermes-agent/tools/patch_parser.py). The repeated `if current_op: if current_hunk and current_hunk.lines: current_op.hunks.append(current_hunk); operations.append(current_op)` blocks occur at each operation boundary (`Update`, `Add`, `Delete`, `Move`) because the parser is flushing the previous operation before starting a new one. That repetition is real, but it is not a duplicated “flush” bug: each site is part of the same finite-state transition and only runs on different marker types. The current implementation is straightforward and correct.
  files_read: [/Users/peteromalley/Documents/hermes-agent/tools/patch_parser.py]
  recommendation: No urgent change. If this file is refactored later, a tiny helper like `_flush_current_op()` would reduce repetition, but this is optional cleanup.

- hash: review::.::holistic::low_level_elegance::repeated_config_yaml_loading
  verdict: not-worth-it
  verdict_reasoning: There is definitely repeated `config.yaml` loading across [hermes_cli/config.py](/Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py), [cli.py](/Users/peteromalley/Documents/hermes-agent/cli.py), [gateway/run.py](/Users/peteromalley/Documents/hermes-agent/gateway/run.py), [cron/scheduler.py](/Users/peteromalley/Documents/hermes-agent/cron/scheduler.py), [tools/delegate_tool.py](/Users/peteromalley/Documents/hermes-agent/tools/delegate_tool.py), and [tools/code_execution_tool.py](/Users/peteromalley/Documents/hermes-agent/tools/code_execution_tool.py). But the duplication is partly structural, not accidental: the codebase explicitly has separate config loaders for CLI startup vs persistent config, gateway refreshes config live without restart, cron re-reads config on each job, and some tools intentionally consult runtime `CLI_CONFIG` first. A forced central abstraction here risks breaking those different freshness and precedence rules. This is a real aesthetic smell, but the issue as framed pushes too hard toward unification.
  files_read: [/Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py, /Users/peteromalley/Documents/hermes-agent/cli.py, /Users/peteromalley/Documents/hermes-agent/gateway/run.py, /Users/peteromalley/Documents/hermes-agent/cron/scheduler.py, /Users/peteromalley/Documents/hermes-agent/tools/delegate_tool.py, /Users/peteromalley/Documents/hermes-agent/tools/code_execution_tool.py]
  recommendation: Do not centralize blindly. If this area is improved, extract only small shared helpers for file reading/normalization while preserving separate loader semantics and hot-reload behavior.

---

## Dimensions: type_safety, error_consistency, incomplete_migration

- hash: review::.::holistic::error_consistency::mixed_logging_for_errors
  verdict: genuine
  verdict_reasoning: I verified that gateway/session handling mixes `logger.*` calls with direct `print(...)` warnings for comparable error paths. In `gateway/session.py`, SQLite initialization and JSON load failures use `print`, while later DB failures in session updates, resets, transcript rewrites, and loads use `logger.debug`. `gateway/platforms/base.py` also mixes structured logging with direct prints for send/interrupt failures. That inconsistency means error visibility depends on which path failed and whether stdout is attached, which is exactly the kind of inconsistent behavior this issue claims.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/session.py, /Users/peteromalley/Documents/hermes-agent/gateway/platforms/base.py]
  recommendation: Standardize on the logger for gateway/platform errors, and choose explicit levels (`warning` for degraded fallback, `error` for user-visible failures, `debug` only for expected low-signal noise).

- hash: review::.::holistic::error_consistency::session_db_errors_invisible
  verdict: exaggerated
  verdict_reasoning: The claim is partly real, but overstated. I confirmed many `SessionDB` operation failures in `gateway/session.py` are logged only at `debug` level, for example token count updates, ending sessions, transcript rewrites, and transcript loads. In quiet/default production runs those are easy to miss. However, the most important startup/create-session failures are not invisible: SQLite init failure and create-session failure emit explicit warnings via `print(...)`, and transcript persistence still falls back to JSONL in several paths. So the issue exists, but it is not a blanket “session DB errors are invisible” situation.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/session.py, /Users/peteromalley/Documents/hermes-agent/hermes_state.py]
  recommendation: Promote a small set of important DB failures from `debug` to `warning`, especially when the system is falling back, losing metadata, or diverging from SQLite/JSONL parity.

- hash: review::.::holistic::incomplete_migration::deprecated_env_var_still_read
  verdict: false-positive
  verdict_reasoning: I verified that `gateway/config.py` still reads `SESSION_IDLE_MINUTES` and `SESSION_RESET_HOUR`, but I did not find evidence that these env vars are deprecated. The opposite is true in this repo: they are still documented in `website/docs/reference/environment-variables.md`, and the gateway loader intentionally bridges newer `config.yaml` `session_reset` settings while still allowing env overrides. This looks like supported backward-compatible behavior, not an incomplete migration.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/config.py, /Users/peteromalley/Documents/hermes-agent/website/docs/reference/environment-variables.md]
  recommendation: Keep as-is unless the project explicitly decides to deprecate these env vars; if that decision is made later, add warnings and remove the docs first.

- hash: review::.::holistic::incomplete_migration::deprecated_on_auto_reset_param
  verdict: not-worth-it
  verdict_reasoning: `gateway/session.py` still accepts `on_auto_reset=None` in `SessionStore.__init__`, and the inline comment explicitly says it is deprecated and no longer used because memory flushing moved to the background watcher. Tests in `tests/gateway/test_async_memory_flush.py` also assert the old callback path is gone. So the parameter is indeed stale, but it is a tiny compatibility shim and removing it could break older callers for almost no gain.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/session.py, /Users/peteromalley/Documents/hermes-agent/tests/gateway/test_async_memory_flush.py]
  recommendation: Leave it for compatibility unless there is a planned breaking-change release; if removed, do it intentionally with a changelog entry.

- hash: review::.::holistic::type_safety::adapters_dict_any_any
  verdict: genuine
  verdict_reasoning: I confirmed `gateway/channel_directory.py` declares `build_channel_directory(adapters: Dict[Any, Any]) -> Dict[str, Any]`. The actual callers use platform adapters keyed by `Platform`, and the function immediately branches on `Platform.DISCORD` / `Platform.SLACK`, so `Dict[Any, Any]` throws away type information the code already relies on. This is a real type-safety gap, not a false alarm.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/channel_directory.py, /Users/peteromalley/Documents/hermes-agent/gateway/run.py]
  recommendation: Narrow the signature to something like `dict[Platform, BasePlatformAdapter]` and keep the return type structured if practical.

- hash: review::.::holistic::type_safety::message_event_source_not_optional
  verdict: genuine
  verdict_reasoning: In `gateway/platforms/base.py`, `MessageEvent.source` is annotated as `SessionSource` but defaulted to `None`. That is a direct mismatch. The mismatch is not theoretical either: repo tests construct `MessageEvent(text=\"/new\")` without a source in `tests/gateway/test_platform_base.py`, so the field is observably optional in practice.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/platforms/base.py, /Users/peteromalley/Documents/hermes-agent/tests/gateway/test_platform_base.py]
  recommendation: Change the annotation to `Optional[SessionSource]` or require `source` at construction and update tests/callers accordingly.

- hash: review::.::holistic::type_safety::optional_without_annotation
  verdict: genuine
  verdict_reasoning: I verified multiple concrete cases where parameters default to `None` but are annotated as non-optional types. Examples include `run_agent.AIAgent.__init__(base_url: str = None, api_key: str = None, provider: str = None, api_mode: str = None, ...)`, `gateway/platforms/base.py` `source: SessionSource = None`, and several `hermes_state.SessionDB` methods such as `create_session(..., model: str = None, system_prompt: str = None, user_id: str = None, parent_session_id: str = None)`. This issue is real and repeated, not a one-off.
  files_read: [/Users/peteromalley/Documents/hermes-agent/run_agent.py, /Users/peteromalley/Documents/hermes-agent/gateway/platforms/base.py, /Users/peteromalley/Documents/hermes-agent/hermes_state.py]
  recommendation: Replace these with `Optional[...]` or PEP 604 `| None` annotations in public signatures, starting with the most central APIs.

- hash: review::.::holistic::type_safety::untyped_discriminator_api_mode
  verdict: genuine
  verdict_reasoning: `run_agent.py` uses `api_mode: str = None` and then dispatches on a fixed literal set: `"chat_completions"`, `"codex_responses"`, and `"anthropic_messages"`. The code clearly treats this as a discriminator, but the type system only sees an arbitrary string. That weakens static checking around mode-specific branches throughout the file.
  files_read: [/Users/peteromalley/Documents/hermes-agent/run_agent.py, /Users/peteromalley/Documents/hermes-agent/hermes_cli/runtime_provider.py]
  recommendation: Introduce a `Literal[...]` alias or small enum for API mode and thread it through resolver and agent initialization.

- hash: review::.::holistic::type_safety::untyped_discriminator_reset_mode
  verdict: genuine
  verdict_reasoning: `gateway/config.py` defines `SessionResetPolicy.mode: str = "both"` and the rest of the gateway logic branches on the closed set `"daily"`, `"idle"`, `"both"`, and `"none"`. This is the same pattern as `api_mode`: semantically a discriminator, but typed as plain `str`. The claim matches the code.
  files_read: [/Users/peteromalley/Documents/hermes-agent/gateway/config.py, /Users/peteromalley/Documents/hermes-agent/gateway/session.py]
  recommendation: Narrow `mode` to a `Literal["daily", "idle", "both", "none"]` or enum, and keep `from_dict` validation aligned with that set.

---

## Dimensions: ai_generated_debt, contract_coherence, test_strategy

- hash: review::.::holistic::ai_generated_debt::dotenv_loading_boilerplate
  verdict: genuine
  verdict_reasoning: I verified the same UTF-8-then-latin-1 dotenv loading pattern is repeated in multiple entrypoints instead of being centralized. `run_agent.py` has the full `~/.hermes/.env` plus project fallback block, `gateway/run.py` repeats a slightly different variant, `hermes_cli/main.py` repeats it again, `hermes_cli/doctor.py` repeats it again, and `cron/scheduler.py` repeats the reload logic for each run. This is real duplication, not a false positive.
  files_read: [run_agent.py, gateway/run.py, hermes_cli/main.py, hermes_cli/doctor.py, cron/scheduler.py]
  recommendation: Extract a shared helper for env loading and use it from these entrypoints; keep per-call `override=True` behavior only where the scheduler genuinely needs it.

- hash: review::.::holistic::ai_generated_debt::stale_probability_comments
  verdict: false-positive
  verdict_reasoning: I searched the assigned code for probability-style comments and found only one relevant instance: `run_agent.py` says rate limiting is the "likely cause of None choices" near the invalid-response backoff path. That is a live heuristic comment aligned with the adjacent returned error text ("Likely rate limited or malformed provider response"), not a stale numeric/probabilistic annotation that has drifted from the code. I did not find a broader pattern of stale probability comments in the files tied to this batch.
  files_read: [run_agent.py, gateway/run.py, hermes_cli/main.py, toolsets.py]
  recommendation: Leave it alone unless there is a concrete example of a misleading probability comment elsewhere; this one is a reasonable heuristic note.

- hash: review::.::holistic::ai_generated_debt::toolsets_docstring_bloat
  verdict: genuine
  verdict_reasoning: `toolsets.py` opens with a large module docstring containing feature bullets and usage examples. The examples are not even coherent with the current file: they reference `get_toolset("research")` and `resolve_toolset("full_stack")`, but those toolsets do not exist in the current `TOOLSETS` map. That makes the docstring both bloated and partially stale, which is a real AI-generated-debt smell rather than just "a bit wordy."
  files_read: [toolsets.py]
  recommendation: Trim the module docstring to a short description and either delete the examples or replace them with current toolset names that actually exist.

- hash: review::.::holistic::ai_generated_debt::toolsets_restating_comments
  verdict: not-worth-it
  verdict_reasoning: The file does contain several comments that restate nearby code, for example `# Return toolset definition` immediately before `return TOOLSETS.get(name)`, `# Get toolset definition`, and section headers that repeat the obvious structure. The issue is technically real. However, this file is still readable, and the comments are not causing behavioral risk. Cleaning all of them up would be cosmetic churn, not a meaningful code-health fix.
  files_read: [toolsets.py]
  recommendation: Only remove the most obviously redundant comments opportunistically when editing `toolsets.py` for a real change; don’t do a dedicated cleanup pass just for this.

- hash: review::.::holistic::contract_coherence::cache_getters_mutate_filesystem
  verdict: genuine
  verdict_reasoning: The contract mismatch is real. `gateway/platforms/base.py` exposes `get_image_cache_dir()`, `get_audio_cache_dir()`, and `get_document_cache_dir()` as getter-style functions, but each one calls `.mkdir(parents=True, exist_ok=True)` before returning. That means a read-sounding API has side effects on the filesystem. The tests confirm and lock this behavior in place for documents: `tests/gateway/test_document_cache.py` explicitly asserts that `get_document_cache_dir()` creates the directory.
  files_read: [gateway/platforms/base.py, tests/gateway/test_document_cache.py]
  recommendation: Rename these helpers to something explicit like `ensure_*_cache_dir()` or split into a pure getter plus an ensuring helper.

- hash: review::.::holistic::contract_coherence::deliver_returns_sendresult_not_dict
  verdict: exaggerated
  verdict_reasoning: I checked `DeliveryRouter.deliver()` in `gateway/delivery.py`. It returns a top-level dict keyed by target string, and each entry is shaped like `{"success": True, "result": result}`. For local delivery, `result` is a dict from `_deliver_local()`. For platform delivery, `_deliver_to_platform()` returns whatever `adapter.send()` returns, which in current adapters is a `SendResult` object. So the inconsistency is real, but the title overstates it: `deliver()` itself does not return a bare `SendResult`; it returns a dict that may contain a `SendResult` under `"result"`.
  files_read: [gateway/delivery.py, gateway/platforms/base.py]
  recommendation: Normalize `deliver()` results so each target entry is plain JSON-serializable data, for example by converting `SendResult` to a dict before storing it.

- hash: review::.::holistic::contract_coherence::toolset_info_returns_none
  verdict: genuine
  verdict_reasoning: `toolsets.py` declares `def get_toolset_info(name: str) -> Dict[str, Any]:` but returns `None` when the toolset is missing. That is a direct type-contract violation, not an interpretation issue. The function body clearly does `if not toolset: return None`.
  files_read: [toolsets.py]
  recommendation: Change the signature to `Optional[Dict[str, Any]]` or raise on unknown toolsets; the current annotation is incorrect.

- hash: review::.::holistic::test_strategy::gateway_run_untested_pipeline
  verdict: exaggerated
  verdict_reasoning: The pipeline is not untested. I verified multiple tests that exercise `gateway.run` behavior directly, including `_run_agent` progress routing in `tests/gateway/test_run_progress_topics.py`, Codex credential-refresh behavior through `_run_agent` in `tests/test_codex_execution_paths.py`, session-hygiene handling in `tests/gateway/test_session_hygiene.py`, background-process watcher behavior in `tests/gateway/test_background_process_notifications.py`, and config-bridge parity checks in `tests/test_auxiliary_config_bridge.py`. There are still gaps: some assertions are textual/parity-based rather than full end-to-end tests, and I did not find focused tests for the per-platform toolset-selection branch inside `_run_agent`. But calling the pipeline "untested" is wrong.
  files_read: [gateway/run.py, tests/gateway/test_run_progress_topics.py, tests/test_codex_execution_paths.py, tests/gateway/test_session_hygiene.py, tests/gateway/test_background_process_notifications.py, tests/test_auxiliary_config_bridge.py]
  recommendation: Reframe this as targeted coverage gaps in specific `gateway.run` branches, not an untested pipeline wholesale.

- hash: review::.::holistic::test_strategy::object_new_fragility
  verdict: genuine
  verdict_reasoning: I verified widespread use of `object.__new__(GatewayRunner)` and `GatewayRunner.__new__(GatewayRunner)` in tests such as `tests/gateway/test_resume_command.py`, `tests/gateway/test_autoreply_command.py`, `tests/gateway/test_title_command.py`, `tests/gateway/test_background_command.py`, `tests/gateway/test_run_progress_topics.py`, and others. These tests manually set only the attributes they happen to need. `GatewayRunner.__init__` initializes many fields (`config`, `session_store`, `delivery_router`, `_pending_approvals`, `_honcho_managers`, `_autoreply_configs`, etc.), so bypassing it is fragile: adding a new implicit dependency in a handler can break unrelated tests or, worse, leave tests passing with unrealistic object state if the handler never touches the missing field.
  files_read: [gateway/run.py, tests/gateway/test_resume_command.py, tests/gateway/test_autoreply_command.py, tests/gateway/test_background_command.py, tests/gateway/test_run_progress_topics.py, tests/test_personality_none.py]
  recommendation: Introduce lightweight test builders/factories that construct minimally valid `GatewayRunner` instances through a controlled path, or extract smaller units so tests do not need partially initialized runner objects.

---

## Dimensions: dependency_health, convention_outlier, abstraction_fitness, design_coherence

- hash: review::.::holistic::abstraction_fitness::tools_init_redundant_barrel
  verdict: genuine
  verdict_reasoning: I read `tools/__init__.py` and checked actual imports across the repo. The file is a 264-line barrel that eagerly re-exports a large set of tool functions and schemas, but the codebase almost never imports from the package root. `rg` found only one real `from tools import ...` use in `tools/file_tools.py`, and that import exists only to reach `check_file_requirements()`. The main tool-loading path is already `model_tools._discover_tools()`, which imports concrete modules directly. That makes the barrel largely redundant and a second abstraction surface to maintain.
  files_read: [tools/__init__.py, tools/file_tools.py, model_tools.py]
  recommendation: Remove or sharply reduce the root barrel. If `check_file_requirements()` is the only live package-root API, move that helper into `tools/file_tools.py` or a small dedicated module and stop treating `tools/__init__.py` as a broad export layer.

- hash: review::.::holistic::convention_outlier::check_ha_requirements_naming
  verdict: false-positive
  verdict_reasoning: The flagged name exists in `gateway/platforms/homeassistant.py` as `check_ha_requirements()`. I checked surrounding code and tests: the same HA abbreviation is used consistently for tool names (`ha_list_entities`, `ha_get_state`, etc.), config vars (`HASS_TOKEN`, `HASS_URL`), docs within the module, and tests that import `check_ha_requirements` directly. This is not an isolated naming outlier; it is the local convention for Home Assistant in this codebase.
  files_read: [gateway/platforms/homeassistant.py, tools/homeassistant_tool.py, tests/gateway/test_homeassistant.py]
  recommendation: Leave the name as-is. Rename only if the project decides to remove the `ha_*` shorthand everywhere, which would be a broad convention change rather than a targeted cleanup.

- hash: review::.::holistic::convention_outlier::large_tools_init_barrel
  verdict: genuine
  verdict_reasoning: `tools/__init__.py` is unusually large for an `__init__` file and acts as a heavy export barrel rather than a light package marker. It imports many submodules up front and maintains a long `__all__`, while the rest of the repo generally imports specific tool modules directly. That makes this `__init__` materially different from the other package initializers in the repository, which are mostly empty or minimal.
  files_read: [tools/__init__.py, agent/__init__.py, gateway/__init__.py, cron/__init__.py]
  recommendation: Treat `tools/__init__.py` as a minimal package file instead of a bulk barrel. Keep only package metadata or a very small set of intentionally supported root exports.

- hash: review::.::holistic::convention_outlier::platform_sys_path_split
  verdict: genuine
  verdict_reasoning: I verified repeated manual `sys.path.insert(...)` bootstrapping in multiple files: `gateway/run.py`, `gateway/platforms/base.py`, `gateway/platforms/slack.py`, `gateway/platforms/telegram.py`, `gateway/platforms/discord.py`, `gateway/platforms/whatsapp.py`, `cron/scheduler.py`, and `tools/cronjob_tools.py`. The platform adapters are inside a package and still mutate import paths individually, which is a real convention outlier and creates multiple entrypoint-specific import assumptions.
  files_read: [gateway/run.py, gateway/platforms/base.py, gateway/platforms/slack.py, gateway/platforms/telegram.py, gateway/platforms/discord.py, gateway/platforms/whatsapp.py, cron/scheduler.py, tools/cronjob_tools.py]
  recommendation: Centralize path bootstrapping at true script entrypoints only, and remove it from importable package modules like the platform adapters.

- hash: review::.::holistic::dependency_health::dual_http_clients
  verdict: exaggerated
  verdict_reasoning: The repo does use multiple HTTP clients, but the situation is more nuanced than a simple dependency-health defect. I verified `httpx` is the dominant client across CLI auth, skills hub, signal, Slack media fetches, and shared gateway helpers; `aiohttp` is used where async web server or WebSocket/session behavior matters, especially Home Assistant and WhatsApp; `requests` appears in only a few synchronous spots such as `tools/browser_tool.py` and `agent/model_metadata.py`. That is some inconsistency, but it is not arbitrary duplication across the same call sites.
  files_read: [tools/browser_tool.py, agent/model_metadata.py, gateway/control_api.py, gateway/platforms/base.py, gateway/platforms/homeassistant.py, gateway/platforms/signal.py, tools/homeassistant_tool.py, tools/send_message_tool.py, hermes_cli/auth.py]
  recommendation: If cleanup is desired, target `requests` first and converge those few sync call sites onto `httpx`. Keeping both `httpx` and `aiohttp` is defensible given the async server/WebSocket usage.

- hash: review::.::holistic::dependency_health::orphaned_mini_swe_deps
  verdict: genuine
  verdict_reasoning: I checked the declared deps and the live imports. `pyproject.toml` and `requirements.txt` both carry `litellm`, `typer`, and `platformdirs` with comments saying they are for mini-swe-agent, but `rg` found no direct imports of those packages anywhere in the Hermes code. I also checked the repository state: `mini-swe-agent/` exists but is empty in this workspace, so the root package is carrying backend-related deps without the vendored backend source actually being present.
  files_read: [pyproject.toml, requirements.txt, tools/terminal_tool.py, mini_swe_runner.py]
  recommendation: Move these dependencies behind a terminal-specific optional extra, or ensure the mini-swe-agent backend is actually vendored/pinned in the repo so the dependency relationship is explicit and live.

- hash: review::.::holistic::dependency_health::requirements_txt_drift
  verdict: genuine
  verdict_reasoning: The drift is real and visible from the files themselves. `requirements.txt` explicitly says it is convenience-only and that `pyproject.toml` is canonical, but the contents already differ: `pyproject.toml` includes `anthropic>=0.39.0` and optional extras like Slack separately, while `requirements.txt` includes `croniter`, `python-telegram-bot`, `discord.py`, and `aiohttp` inline and omits `anthropic`. This is a real duplicated dependency surface with mismatched contents.
  files_read: [requirements.txt, pyproject.toml]
  recommendation: Either generate `requirements.txt` from `pyproject.toml` or remove the handwritten file and document one installation path. As it stands, it will keep drifting.

- hash: review::.::holistic::dependency_health::unused_jinja2_dep
  verdict: genuine
  verdict_reasoning: I searched the non-doc codebase and found no runtime imports of `jinja2` at all. The only hits are dependency declarations in `pyproject.toml`, `requirements.txt`, and lockfile entries in `uv.lock`. Based on the current source tree, `jinja2` is not used by application code.
  files_read: [pyproject.toml, requirements.txt]
  recommendation: Remove `jinja2` from declared dependencies unless there is an external or optional path that truly requires it and should be documented.

- hash: review::.::holistic::design_coherence::gateway_config_yaml_reload
  verdict: genuine
  verdict_reasoning: `gateway/run.py` rereads `~/.hermes/config.yaml` in many separate helper methods instead of loading once and reusing a coherent config object. I verified repeated `yaml.safe_load()` calls at module import time and again in methods such as `_load_prefill_messages`, `_load_ephemeral_system_prompt`, `_load_reasoning_config`, `_load_show_reasoning`, `_load_background_notifications_mode`, `_load_provider_routing`, `_load_fallback_model`, plus several command handlers later in the file. Some rereads are intentional for dynamic reload behavior, but the current pattern is fragmented and mixes startup config, per-run config, and ad hoc command-time config access.
  files_read: [gateway/run.py, gateway/config.py, cron/scheduler.py]
  recommendation: Introduce one clear config access layer for the gateway: either cache the parsed config on `GatewayRunner` with explicit refresh points, or formalize which features intentionally reread disk. Right now the behavior is scattered enough to be a real coherence issue.

---

## Dimensions: mid_level_elegance, initialization_coupling, authorization_consistency, high_level_elegance

- hash: review::.::holistic::authorization_consistency::allowlist_env_var_magic_strings
  verdict: genuine
  verdict_reasoning: I verified that gateway authorization policy is still encoded through multiple hand-maintained env-var maps and string literals in [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py) around `_is_user_authorized()`. The platform allowlist map and allow-all map are separate dicts, and the repo’s own platform authoring guide explicitly warns maintainers to update "BOTH dicts" when adding a platform in [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/ADDING_A_PLATFORM.md`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/ADDING_A_PLATFORM.md). Signal also has a separate `SIGNAL_GROUP_ALLOWED_USERS` path in [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/signal.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/signal.py), so authorization rules are not centralized. This is a real consistency risk, not just a style complaint.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/gateway/run.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/ADDING_A_PLATFORM.md", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/signal.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/discord.py"]
  recommendation: Centralize platform authorization config in one source of truth, ideally on `Platform` or `PlatformConfig`, so allowlist env names and allow-all env names are derived instead of duplicated.

- hash: review::.::holistic::high_level_elegance::agents_md_structure_drift
  verdict: genuine
  verdict_reasoning: `AGENTS.md` is materially out of sync with the code in a few places. The clearest verified mismatch is that it says `_config_version` is "currently 5" at line 182, while [`/Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py`](file:///Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py) sets `_config_version` to `7`. It also describes the gateway as doing "Direct YAML load" in `gateway/run.py`, but config loading is now split across `gateway/run.py` and `gateway/config.py`. This is real documentation drift, though not catastrophic architecture damage.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/AGENTS.md", "/Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py", "/Users/peteromalley/Documents/hermes-agent/gateway/run.py", "/Users/peteromalley/Documents/hermes-agent/gateway/config.py"]
  recommendation: Treat `AGENTS.md` as maintained architecture docs and update the stale claims; a targeted docs refresh is enough.

- hash: review::.::holistic::initialization_coupling::gateway_run_import_side_effects
  verdict: genuine
  verdict_reasoning: Importing [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py) has substantial top-level side effects before `GatewayRunner` is constructed. It mutates `sys.path`, loads `.env`, parses `~/.hermes/config.yaml`, bridges config values into `os.environ`, and unconditionally sets `HERMES_QUIET`, `HERMES_EXEC_ASK`, and `TERMINAL_CWD` at import time. That is real initialization coupling: import order affects global process state.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/gateway/run.py"]
  recommendation: Move the env/config bootstrapping into an explicit initialization function called by the gateway entrypoint, leaving module import mostly declarative.

- hash: review::.::holistic::initialization_coupling::model_tools_stale_snapshots
  verdict: exaggerated
  verdict_reasoning: The issue is based on a real mechanism, but the current code already documents and partially mitigates it. [`/Users/peteromalley/Documents/hermes-agent/model_tools.py`](file:///Users/peteromalley/Documents/hermes-agent/model_tools.py) still keeps `TOOL_TO_TOOLSET_MAP` and `TOOLSET_REQUIREMENTS` as module-level snapshots and `_last_resolved_tool_names` as process-global state. However, `handle_function_call()` now prefers caller-supplied `enabled_tools` for `execute_code`, and the repo docs explicitly call the global a "Known bug" in [`/Users/peteromalley/Documents/hermes-agent/AGENTS.md`](file:///Users/peteromalley/Documents/hermes-agent/AGENTS.md). So the problem exists, but "stale snapshots" overstates it as a broad system defect; the verified live risk is narrower and mostly centered on backward-compat globals.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/model_tools.py", "/Users/peteromalley/Documents/hermes-agent/AGENTS.md"]
  recommendation: Keep the finding focused on the remaining process-global state, especially `_last_resolved_tool_names`; the static registry-derived maps are lower priority unless there is evidence they go stale at runtime.

- hash: review::.::holistic::initialization_coupling::sys_path_insert_gateway_modules
  verdict: genuine
  verdict_reasoning: I confirmed repeated `sys.path.insert(0, ...)` bootstrapping in gateway modules: [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py), [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/base.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/base.py), [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/discord.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/discord.py), [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/slack.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/slack.py), [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/telegram.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/telegram.py), and [`/Users/peteromalley/Documents/hermes-agent/gateway/platforms/whatsapp.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/platforms/whatsapp.py). This is not hypothetical; the package currently depends on import-path mutation in multiple files.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/gateway/run.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/base.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/discord.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/slack.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/telegram.py", "/Users/peteromalley/Documents/hermes-agent/gateway/platforms/whatsapp.py"]
  recommendation: Remove per-module path mutation and rely on package execution/imports only; if a compatibility shim is needed, keep it in one entrypoint instead of scattering it.

- hash: review::.::holistic::mid_level_elegance::ad_hoc_temporary_agent_construction
  verdict: genuine
  verdict_reasoning: I verified several separate "temporary" `AIAgent(...)` constructions in [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py): memory flush at lines 397-404, hygiene compression at 1276-1283, manual `/compress` at 2596-2603, plus the main runtime agent construction paths at 2394-2412 and 3557-3582. These are not identical, but they duplicate resolution logic around runtime credentials, model selection, iteration caps, session IDs, and toolsets. The pattern is real and already causing special-case comments explaining why model/runtime kwargs must be resolved carefully.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/gateway/run.py"]
  recommendation: Introduce a small internal gateway agent factory for the common defaults, with explicit overrides for flush/compress/main-run use cases.

- hash: review::.::holistic::mid_level_elegance::hasattr_on_init_attributes
  verdict: exaggerated
  verdict_reasoning: The repo does use some unnecessary `hasattr(...)` checks on attributes that are initialized in constructors, but the issue is overstated if framed as a pervasive design problem. In [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py), `_honcho_managers` and `_honcho_configs` are always initialized in `GatewayRunner.__init__`, so the later `hasattr(self, ...)` guards are redundant. In contrast, the `run_agent.py` cases are mixed: `context_compressor`, `_anthropic_api_key`, and retry counters are initialized, but some guards are harmless defensive checks around evolving response paths. This is cleanup-worthy, not a major architectural smell.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/gateway/run.py", "/Users/peteromalley/Documents/hermes-agent/run_agent.py"]
  recommendation: Remove the clearly redundant `hasattr(self, ...)` cases in `GatewayRunner` first; do not spend time mass-refactoring every defensive `hasattr` in `run_agent.py` unless it obscures logic.

- hash: review::.::holistic::mid_level_elegance::monolithic_handle_message
  verdict: genuine
  verdict_reasoning: `GatewayRunner._handle_message()` in [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py) is a real monolith. I measured the method body from line 915 until the next method definition: it spans roughly 2000+ lines of mixed concerns, with the initial pipeline segment alone covering about 500 lines between command dispatch, approval handling, session setup, transcript hygiene, media enrichment, agent execution, persistence, hooks, and auto-reply scheduling. The structure is still readable in places because of comments, but the function is undeniably carrying too many responsibilities.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/gateway/run.py"]
  recommendation: Split by responsibility, not by arbitrary size: command routing, session preparation, pre-agent enrichment, agent execution/persistence, and post-response scheduling are the obvious extraction seams.

- hash: review::.::holistic::mid_level_elegance::scattered_config_yaml_parsing
  verdict: genuine
  verdict_reasoning: I verified repeated direct `yaml.safe_load` parsing of `~/.hermes/config.yaml` across multiple modules: [`/Users/peteromalley/Documents/hermes-agent/cli.py`](file:///Users/peteromalley/Documents/hermes-agent/cli.py), [`/Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py`](file:///Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py), [`/Users/peteromalley/Documents/hermes-agent/gateway/run.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/run.py), [`/Users/peteromalley/Documents/hermes-agent/gateway/config.py`](file:///Users/peteromalley/Documents/hermes-agent/gateway/config.py), [`/Users/peteromalley/Documents/hermes-agent/cron/scheduler.py`](file:///Users/peteromalley/Documents/hermes-agent/cron/scheduler.py), [`/Users/peteromalley/Documents/hermes-agent/rl_cli.py`](file:///Users/peteromalley/Documents/hermes-agent/rl_cli.py), and [`/Users/peteromalley/Documents/hermes-agent/hermes_time.py`](file:///Users/peteromalley/Documents/hermes-agent/hermes_time.py). This is not just different consumers reading config once; `gateway/run.py` alone reparses the YAML many times for specific getters. The scattering is real.
  files_read: ["/Users/peteromalley/Documents/hermes-agent/cli.py", "/Users/peteromalley/Documents/hermes-agent/hermes_cli/config.py", "/Users/peteromalley/Documents/hermes-agent/gateway/run.py", "/Users/peteromalley/Documents/hermes-agent/gateway/config.py", "/Users/peteromalley/Documents/hermes-agent/cron/scheduler.py", "/Users/peteromalley/Documents/hermes-agent/rl_cli.py", "/Users/peteromalley/Documents/hermes-agent/hermes_time.py"]
  recommendation: Consolidate read paths around a shared config loader/helpers. Prioritize gateway read-heavy paths first, since that file currently repeats the most YAML parsing.


## Issue Data

## Resolved since last triage (14)
- review::.::holistic::abstraction_fitness::aiagent_wide_constructor
- review::.::holistic::abstraction_fitness::triplicated_cache_utilities
- review::.::holistic::api_surface_coherence::cache_param_inconsistency
- review::.::holistic::cross_module_architecture::bidirectional_root_hermes_cli_coupling
- review::.::holistic::cross_module_architecture::gateway_tools_bidirectional_coupling
- review::.::holistic::cross_module_architecture::private_symbols_crossed_across_boundaries
- review::.::holistic::cross_module_architecture::tools_import_cli_config
- review::.::holistic::design_coherence::aiagent_init_parameter_sprawl
- review::.::holistic::design_coherence::command_dispatch_chain
- review::.::holistic::design_coherence::media_cache_triplication
- review::.::holistic::high_level_elegance::monolithic_gateway_run
- review::.::holistic::incomplete_migration::sqlite_jsonl_dual_write
- review::.::holistic::low_level_elegance::handle_message_monolith
- review::.::holistic::naming_quality::do_prefix_skills_hub

## Resolved review issues available for recurrence context (14)
- review::.::holistic::abstraction_fitness::aiagent_wide_constructor [abstraction_fitness]: AIAgent.__init__ accepts ~40 parameters acting as an implicit configuration bag
- review::.::holistic::abstraction_fitness::triplicated_cache_utilities [abstraction_fitness]: Image, audio, and document cache utilities in base.py repeat the same pattern three times
- review::.::holistic::api_surface_coherence::cache_param_inconsistency [api_surface_coherence]: cache_document_from_bytes takes filename while sibling functions take ext — inconsistent parameter semantics
- review::.::holistic::cross_module_architecture::bidirectional_root_hermes_cli_coupling [cross_module_architecture]: Root-level files and hermes_cli/ have 24 bidirectional import edges, creating a dependency cycle
- review::.::holistic::cross_module_architecture::gateway_tools_bidirectional_coupling [cross_module_architecture]: gateway/ and tools/ have bidirectional import edges (13 total), blurring their boundary
- review::.::holistic::cross_module_architecture::private_symbols_crossed_across_boundaries [cross_module_architecture]: Private functions/variables imported across package boundaries in 6+ locations
- review::.::holistic::cross_module_architecture::tools_import_cli_config [cross_module_architecture]: tools/code_execution_tool.py and tools/delegate_tool.py import CLI_CONFIG from root cli.py
- review::.::holistic::design_coherence::aiagent_init_parameter_sprawl [design_coherence]: AIAgent.__init__ accepts 40+ parameters spanning 6 distinct responsibility groups
- review::.::holistic::design_coherence::command_dispatch_chain [design_coherence]: gateway/run.py _handle_message uses a 60-line if/elif chain for command dispatch despite having a _known_commands set
- review::.::holistic::design_coherence::media_cache_triplication [design_coherence]: Three nearly identical media cache implementations (image/audio/document) in gateway/platforms/base.py
- review::.::holistic::high_level_elegance::monolithic_gateway_run [high_level_elegance]: gateway/run.py (4,067 lines) concentrates message routing, slash commands, model resolution, and cron ticker
- review::.::holistic::incomplete_migration::sqlite_jsonl_dual_write [incomplete_migration]: Session transcript dual-writes to both SQLite and JSONL with no migration completion plan
- review::.::holistic::low_level_elegance::handle_message_monolith [low_level_elegance]: _handle_message in gateway/run.py is ~720 lines with deeply nested session hygiene logic
- review::.::holistic::naming_quality::do_prefix_skills_hub [naming_quality]: do_ prefix on 8 skills_hub.py functions adds no information and obscures domain

## Potential recurring dimensions (resolved issues still have open peers)
- abstraction_fitness: 1 open / 2 recently resolved
- cross_module_architecture: 1 open / 4 recently resolved
- design_coherence: 1 open / 3 recently resolved
- high_level_elegance: 1 open / 1 recently resolved
- incomplete_migration: 2 open / 1 recently resolved
- low_level_elegance: 3 open / 1 recently resolved

## All open review issues (45)
- [medium] review::.::holistic::abstraction_fitness::tools_init_redundant_barrel
  File: .
  Dimension: abstraction_fitness
  Summary: tools/__init__.py re-exports 81+ symbols redundant with registry-based tool discovery
  Suggestion: Reduce tools/__init__.py to only re-export the truly public symbols needed by external callers (if any exist beyond model_tools.py). Most callers should import from model_tools or directly from the specific tool module.
- [high] review::.::holistic::ai_generated_debt::dotenv_loading_boilerplate
  File: .
  Dimension: ai_generated_debt
  Summary: Identical .env loading try/except boilerplate duplicated across 7+ entry-point files
  Suggestion: Extract a shared load_hermes_env() helper (e.g., in hermes_constants.py or a new hermes_bootstrap.py) that encapsulates the env file resolution, encoding fallback, and MSWEA_GLOBAL_CONFIG_DIR setup. Each entry point then calls one function instead of duplicating 10+ lines.
- [high] review::.::holistic::ai_generated_debt::stale_probability_comments
  File: .
  Dimension: ai_generated_debt
  Summary: toolset_distributions.py has inline probability comments that contradict their actual values
  Suggestion: Remove all these inline probability comments -- the numeric values are self-documenting and the stale comments are actively misleading. If comments are kept, they should describe the reasoning for the weight, not restate the number.
- [high] review::.::holistic::ai_generated_debt::toolsets_docstring_bloat
  File: .
  Dimension: ai_generated_debt
  Summary: toolsets.py has verbose multi-section docstrings on trivial 1-2 line functions
  Suggestion: Replace verbose Args/Returns docstrings with single-line docstrings. For example, get_toolset() needs only: """Return toolset definition by name, or None.""" -- the types are already in the signature annotations.
- [high] review::.::holistic::ai_generated_debt::toolsets_restating_comments
  File: .
  Dimension: ai_generated_debt
  Summary: toolsets.py contains inline comments that restate the code without adding insight
  Suggestion: Delete these restating comments. The code is self-explanatory -- 'return TOOLSETS.get(name)' does not need a '# Return toolset definition' caption.
- [medium] review::.::holistic::authorization_consistency::allowlist_env_var_magic_strings
  File: .
  Dimension: authorization_consistency
  Summary: Allowlist env var names repeated as magic strings across 6+ files instead of shared constants
  Suggestion: Define a dict mapping Platform enum values to their env var names (e.g., PLATFORM_ALLOWLIST_VARS = {Platform.TELEGRAM: 'TELEGRAM_ALLOWED_USERS', ...}) in gateway/config.py, and import it everywhere these strings appear. This centralizes the mapping and prevents drift if a new platform is added.
- [medium] review::.::holistic::contract_coherence::cache_getters_mutate_filesystem
  File: .
  Dimension: contract_coherence
  Summary: get_image_cache_dir, get_audio_cache_dir, get_document_cache_dir create directories as a side effect
  Suggestion: Rename to ensure_image_cache_dir() / ensure_audio_cache_dir() / ensure_document_cache_dir() to signal the side effect. Alternatively, move the mkdir to module init or a separate ensure_cache_dirs() function.
- [high] review::.::holistic::contract_coherence::deliver_returns_sendresult_not_dict
  File: .
  Dimension: contract_coherence
  Summary: _deliver_to_platform annotated -> Dict[str, Any] but returns SendResult dataclass
  Suggestion: Either change the annotation to -> SendResult, or convert the return value: return a dict like {'success': result.success, 'message_id': result.message_id} from _deliver_to_platform.
- [high] review::.::holistic::contract_coherence::toolset_info_returns_none
  File: .
  Dimension: contract_coherence
  Summary: get_toolset_info() annotated as -> Dict[str, Any] but returns None when toolset not found
  Suggestion: Change return annotation to Optional[Dict[str, Any]] to match the actual behavior, consistent with get_toolset() on line 300 which correctly uses Optional.
- [high] review::.::holistic::convention_outlier::check_ha_requirements_naming
  File: .
  Dimension: convention_outlier
  Summary: check_ha_requirements uses abbreviated name while all 6 other adapters use full platform name
  Suggestion: Rename check_ha_requirements to check_homeassistant_requirements to match the naming convention used by all other platform adapters. Update the 1-2 call sites accordingly.
- [medium] review::.::holistic::convention_outlier::large_tools_init_barrel
  File: .
  Dimension: convention_outlier
  Summary: tools/__init__.py is a 264-line re-export barrel that consumers largely bypass via direct imports
  Suggestion: Slim tools/__init__.py down to minimal re-exports or just the package docstring. Since the registry pattern handles tool discovery and consumers already import directly from submodules, the large barrel adds maintenance burden without value.
- [high] review::.::holistic::convention_outlier::platform_sys_path_split
  File: .
  Dimension: convention_outlier
  Summary: 4 of 7 platform adapters use sys.path.insert while 3 import directly — inconsistent sibling convention
  Suggestion: Remove the sys.path.insert calls from telegram.py, discord.py, slack.py, and whatsapp.py to match the direct-import convention used by signal.py, email.py, and homeassistant.py. The gateway package is already importable via normal Python path resolution when running through the entry points.
- [high] review::.::holistic::cross_module_architecture::registry_violates_own_contract
  File: .
  Dimension: cross_module_architecture
  Summary: tools/registry.py imports _run_async from model_tools, contradicting its own documented import chain
  Suggestion: Move _run_async to a shared utility (e.g., agent/async_utils.py or tools/async_support.py) that sits below registry in the import chain, or have model_tools set an async runner on the registry during initialization.
- [medium] review::.::holistic::dependency_health::dual_http_clients
  File: .
  Dimension: dependency_health
  Summary: Both requests and httpx are core dependencies used for the same purpose (synchronous HTTP calls)
  Suggestion: Consolidate on httpx since it is already the dominant client (66 vs 6 call sites) and supports both sync and async usage. Replace the 6 requests.post/get calls in browser_tool.py and model_metadata.py with httpx equivalents, then remove requests from dependencies.
- [high] review::.::holistic::dependency_health::orphaned_mini_swe_deps
  File: .
  Dimension: dependency_health
  Summary: litellm, typer, and platformdirs are core deps for mini-swe-agent but that subproject directory is empty
  Suggestion: Move litellm, typer, and platformdirs to a new optional extra (e.g. [mini-swe]) or remove them from core dependencies until mini-swe-agent is actually present. The terminal tool already handles the missing import gracefully.
- [high] review::.::holistic::dependency_health::requirements_txt_drift
  File: .
  Dimension: dependency_health
  Summary: requirements.txt has diverged from canonical pyproject.toml: includes messaging extras as core, missing anthropic
  Suggestion: Either regenerate requirements.txt from pyproject.toml to match the canonical source, or delete it entirely since pyproject.toml is the canonical dependency list and the file header already directs users to 'pip install -e .[all]'.
- [high] review::.::holistic::dependency_health::unused_jinja2_dep
  File: .
  Dimension: dependency_health
  Summary: jinja2 is a core dependency but is never imported or used anywhere in the codebase
  Suggestion: Remove jinja2 from dependencies in pyproject.toml and requirements.txt. If it was intended for future template rendering, add it back when actually needed.
- [high] review::.::holistic::design_coherence::gateway_config_yaml_reload
  File: .
  Dimension: design_coherence
  Summary: gateway/run.py opens and parses config.yaml 11 times independently across 7 _load_* methods
  Suggestion: Load config.yaml once in __init__ into a dict, then have each _load_* method extract its section from the pre-loaded dict. A single _load_config_yaml() -> dict method replaces 7+ file opens with 7 dict lookups.
- [high] review::.::holistic::error_consistency::mixed_logging_for_errors
  File: .
  Dimension: error_consistency
  Summary: Error logging inconsistently uses print(), logger.debug(), logger.warning(), and logger.error()
  Suggestion: Replace print() error reporting with logger.warning() throughout gateway/session.py and gateway/platforms/base.py. Promote SQLite operation failures from logger.debug() to logger.warning() since database issues should be visible in normal operation.
- [high] review::.::holistic::error_consistency::session_db_errors_invisible
  File: .
  Dimension: error_consistency
  Summary: All SQLite session DB operations log failures at debug level, hiding database problems
  Suggestion: Catch sqlite3.Error specifically instead of Exception. Log first occurrence per session at warning level, then suppress subsequent failures for the same session to avoid log spam. This preserves the graceful-degradation pattern while making the initial failure visible.
- [high] review::.::holistic::high_level_elegance::agents_md_structure_drift
  File: .
  Dimension: high_level_elegance
  Summary: AGENTS.md project structure lists nonexistent acp_adapter/ and omits many real directories and files
  Suggestion: Update AGENTS.md project structure to remove acp_adapter/ and add the missing directories and key files. For large packages, listing representative files plus '...' is fine, but the top-level structure must be accurate.
- [medium] review::.::holistic::incomplete_migration::deprecated_env_var_still_read
  File: .
  Dimension: incomplete_migration
  Summary: Deprecated HERMES_TOOL_PROGRESS_MODE env var still read as active fallback in gateway/run.py
  Suggestion: Remove the os.getenv('HERMES_TOOL_PROGRESS_MODE') fallback from gateway/run.py:3297 since the config migration system already handles converting old env vars to config.yaml entries. This would complete the deprecation.
- [high] review::.::holistic::incomplete_migration::deprecated_on_auto_reset_param
  File: .
  Dimension: incomplete_migration
  Summary: Deprecated on_auto_reset parameter still accepted by SessionStore.__init__ but never used
  Suggestion: Remove the on_auto_reset parameter from SessionStore.__init__ since no caller passes it.
- [high] review::.::holistic::initialization_coupling::gateway_run_import_side_effects
  File: .
  Dimension: initialization_coupling
  Summary: gateway/run.py performs dotenv loading, YAML parsing, and os.environ mutation at module scope
  Suggestion: Move the dotenv loading and config.yaml bridging into a function like _bootstrap_environment() called explicitly by start_gateway() and the GatewayRunner constructor, rather than at module scope. Tests can call it explicitly or skip it.
- [medium] review::.::holistic::initialization_coupling::model_tools_stale_snapshots
  File: .
  Dimension: initialization_coupling
  Summary: TOOL_TO_TOOLSET_MAP and TOOLSET_REQUIREMENTS are stale snapshots built once at import time
  Suggestion: Replace the module-level constants with thin functions that delegate to the registry: e.g. def get_tool_to_toolset_map(): return registry.get_tool_to_toolset_map(). Callers already have registry access via the import.
- [high] review::.::holistic::initialization_coupling::sys_path_insert_gateway_modules
  File: .
  Dimension: initialization_coupling
  Summary: sys.path.insert(0, ...) at import time in 6 gateway platform modules pollutes sys.path
  Suggestion: Install the project as a package (pip install -e .) or use a single conftest/bootstrap that sets sys.path once. The gateway modules should use relative imports (from gateway.config import ...) which already work when the package is properly installed.
- [high] review::.::holistic::logic_clarity::dead_code_checkpoint_manager
  File: .
  Dimension: logic_clarity
  Summary: checkpoint_manager.py:255-260 runs git log whose result is immediately overwritten by lines 263-266
  Suggestion: Remove lines 255-260 entirely. The second git log call (lines 263-266) is the one actually used.
- [high] review::.::holistic::logic_clarity::duplicated_dead_countdown_check
  File: .
  Dimension: logic_clarity
  Summary: cli.py:3549-3551 duplicates the countdown refresh check from lines 3546-3548, second block never fires
  Suggestion: Remove the duplicated block at lines 3549-3551.
- [high] review::.::holistic::logic_clarity::identical_branches_skills_sync
  File: .
  Dimension: logic_clarity
  Summary: if user_hash == bundled_hash / else in skills_sync.py:204 both just increment skipped
  Suggestion: Collapse to a single skipped += 1 with a comment noting the ambiguity during v1 migration. The conditional adds no value since both paths do the same thing.
- [high] review::.::holistic::logic_clarity::identical_branches_telegram_document
  File: .
  Dimension: logic_clarity
  Summary: elif msg.document / else branches both assign MessageType.DOCUMENT identically
  Suggestion: Remove the elif msg.document branch and let the else handle all remaining cases as DOCUMENT, or if DOCUMENT should only apply when msg.document is truthy, change the else to assign a different type (e.g., MessageType.UNKNOWN).
- [high] review::.::holistic::logic_clarity::identical_branches_uninstall
  File: .
  Dimension: logic_clarity
  Summary: if/else in uninstall.py:280 performs identical shutil.rmtree + log_success in both branches
  Suggestion: Remove the if/else condition and unconditionally call shutil.rmtree(project_root) followed by log_success(). If there was intended to be different behavior (e.g., only removing a subdirectory), implement the actual distinction.
- [high] review::.::holistic::low_level_elegance::defensive_hasattr_after_init
  File: .
  Dimension: low_level_elegance
  Summary: _get_or_create_gateway_honcho uses hasattr checks for attributes initialized in __init__
  Suggestion: Remove the two hasattr guards (lines 323-326) since these attributes are guaranteed to exist after __init__.
- [high] review::.::holistic::low_level_elegance::patch_parser_duplicated_flush
  File: .
  Dimension: low_level_elegance
  Summary: parse_v4a_patch duplicates the 'save previous operation' block 4 times identically
  Suggestion: Extract a local helper _flush_current_op(current_op, current_hunk, operations) that performs the flush-and-append, then call it at each transition point. This removes 12 lines of duplication and makes the state machine transitions clearer.
- [high] review::.::holistic::low_level_elegance::repeated_config_yaml_loading
  File: .
  Dimension: low_level_elegance
  Summary: config.yaml loading boilerplate duplicated 11 times across gateway/run.py methods
  Suggestion: Add a module-level helper like _load_config_yaml() -> dict that loads and caches ~/.hermes/config.yaml once, then replace all 11 inline load-and-parse blocks with calls to that helper. Each _load_* method would become a simple dict traversal.
- [high] review::.::holistic::mid_level_elegance::ad_hoc_temporary_agent_construction
  File: .
  Dimension: mid_level_elegance
  Summary: Temporary AIAgent instances are constructed in 4+ places with inconsistent initialization parameters
  Suggestion: Add a GatewayRunner._create_utility_agent(session_id, toolsets, max_iterations) helper that encapsulates the common pattern: resolve model, resolve runtime kwargs, construct AIAgent with quiet_mode=True. The 3 utility sites call this instead of duplicating construction. The main _run_agent stays separate since it has many additional concerns.
- [high] review::.::holistic::mid_level_elegance::hasattr_on_init_attributes
  File: .
  Dimension: mid_level_elegance
  Summary: _get_or_create_gateway_honcho uses hasattr() to check attributes that __init__ already sets
  Suggestion: Remove the hasattr/getattr guards since __init__ guarantees these attributes exist. The defensive checks obscure the actual contract and suggest the object might be in a partially-initialized state, which is not the case.
- [high] review::.::holistic::mid_level_elegance::monolithic_handle_message
  File: .
  Dimension: mid_level_elegance
  Summary: _handle_message is a 700+ line method mixing authorization, command dispatch, media enrichment, and agent orchestration
  Suggestion: Extract the major phases into focused methods: _authorize_user(event) -> bool, _dispatch_command(event) -> Optional[str], _enrich_media(event, message_text) -> str, _persist_transcript(session_entry, ...). The top-level _handle_message becomes a ~50-line pipeline that composes these steps. This reduces the cognitive load of any single method without adding indirection layers.
- [high] review::.::holistic::mid_level_elegance::scattered_config_yaml_parsing
  File: .
  Dimension: mid_level_elegance
  Summary: gateway/run.py re-parses config.yaml 20+ times in independent methods instead of using a shared config object
  Suggestion: Create a GatewayConfig.from_yaml() or extend the existing load_gateway_config() to eagerly parse all config.yaml keys into typed fields at startup. Each method then reads from the config object instead of re-parsing YAML. For hot-reloading, add a refresh() method that re-reads once and updates all fields atomically.
- [high] review::.::holistic::test_strategy::gateway_run_untested_pipeline
  File: .
  Dimension: test_strategy
  Summary: gateway/run.py (4067 lines, 26 importers) lacks dedicated test coverage for its core _handle_message pipeline
  Suggestion: Add a test_gateway_run.py with tests for _handle_message dispatch (command routing, agent launch flow, error paths). Consider extracting a factory method or builder for GatewayRunner to reduce test setup boilerplate.
- [high] review::.::holistic::test_strategy::object_new_fragility
  File: .
  Dimension: test_strategy
  Summary: 9 test files bypass GatewayRunner.__init__ via object.__new__, creating fragile coupling to internal attributes
  Suggestion: Extract a shared _make_runner() fixture in tests/gateway/conftest.py that constructs a properly initialized GatewayRunner with a test config. Alternatively, add a GatewayRunner.for_testing() classmethod that sets safe defaults.
- [high] review::.::holistic::type_safety::adapters_dict_any_any
  File: .
  Dimension: type_safety
  Summary: build_channel_directory uses Dict[Any, Any] where specific types exist
  Suggestion: Change parameter type to Dict[Platform, BasePlatformAdapter] which matches actual usage and enables static analysis of the key comparisons.
- [high] review::.::holistic::type_safety::message_event_source_not_optional
  File: .
  Dimension: type_safety
  Summary: MessageEvent.source typed as SessionSource but defaults to None -- annotation lies about nullability
  Suggestion: Change to source: Optional[SessionSource] = None. Alternatively, if source is always set before use, make it a required field and remove the default.
- [high] review::.::holistic::type_safety::optional_without_annotation
  File: .
  Dimension: type_safety
  Summary: 15+ parameters typed as concrete types (str, int, dict, callable) but default to None without Optional annotation
  Suggestion: Add Optional[] to all parameters that accept None. For example: base_url: Optional[str] = None, last_prompt_tokens: Optional[int] = None. This is a mechanical find-and-replace that can be done per-file.
- [high] review::.::holistic::type_safety::untyped_discriminator_api_mode
  File: .
  Dimension: type_safety
  Summary: AIAgent.api_mode is bare str but acts as a 3-value discriminated union compared 50+ times
  Suggestion: Define ApiMode = Literal['chat_completions', 'codex_responses', 'anthropic_messages'] and type the field as Optional[ApiMode]. This enables static analysis to catch typos in the 50+ comparison sites.
- [high] review::.::holistic::type_safety::untyped_discriminator_reset_mode
  File: .
  Dimension: type_safety
  Summary: SessionResetPolicy.mode is bare str but only valid as 'daily' | 'idle' | 'both' | 'none'
  Suggestion: Define ResetMode = Literal['daily', 'idle', 'both', 'none'] and type SessionResetPolicy.mode as ResetMode. The enum is already documented in the docstring; making it a type gives static analysis teeth.

## Dimension scores (context)
- AI generated debt: 79.5% (strict: 79.5%, 4 issues)
- API coherence: 82.5% (strict: 82.5%, 0 issues)
- Abstraction fit: 76.0% (strict: 76.0%, 1 issues)
- Auth consistency: 89.5% (strict: 89.5%, 1 issues)
- Code quality: 76.8% (strict: 51.4%, 739 issues)
- Contracts: 74.5% (strict: 74.5%, 3 issues)
- Convention drift: 85.0% (strict: 85.0%, 3 issues)
- Cross-module arch: 62.5% (strict: 62.5%, 1 issues)
- Dep health: 78.5% (strict: 78.5%, 4 issues)
- Design coherence: 62.5% (strict: 62.5%, 1 issues)
- Duplication: 98.9% (strict: 98.8%, 31 issues)
- Error consistency: 62.5% (strict: 62.5%, 2 issues)
- File health: 72.7% (strict: 45.4%, 70 issues)
- High elegance: 72.5% (strict: 72.5%, 1 issues)
- Init coupling: 82.5% (strict: 82.5%, 3 issues)
- Logic clarity: 82.5% (strict: 82.5%, 5 issues)
- Low elegance: 68.5% (strict: 68.5%, 3 issues)
- Mid elegance: 62.5% (strict: 62.5%, 4 issues)
- Naming quality: 82.5% (strict: 82.5%, 0 issues)
- Security: 91.0% (strict: 81.5%, 5372 issues)
- Stale migration: 82.5% (strict: 82.5%, 2 issues)
- Structure nav: 72.5% (strict: 72.5%, 0 issues)
- Test health: 67.5% (strict: 13.6%, 71 issues)
- Test strategy: 62.5% (strict: 62.5%, 2 issues)
- Type safety: 52.0% (strict: 52.0%, 5 issues)

## Auto-cluster candidates (6398 items: 63 in 2 auto-clusters, 6335 unclustered)
These are detector-created findings grouped by rule type. Each auto-cluster is a first-class triage candidate — decide its fate just like review issues.
You MUST make an explicit decision for each auto-cluster listed below. Include every auto-cluster in your `auto_cluster_decisions` output with one of: promote (add to active queue with a priority position), skip (with a specific reason — e.g. 'mostly false positives per sampling'), or break_up (split into smaller sub-clusters with a reason).
### Auto-clusters (decision required for each)
Each cluster below includes a statistical summary with severity breakdown and sample issues. Decide for each: promote, skip (with reason), or break_up.
- auto/test_coverage (61 items)
  Fix 63 test coverage issues
  severity=[unknown: 61] confidence=[high: 32, medium: 29] top_rules=[transitive_only(29), untested_module(22), untested_critical(10)] samples: environments/hermes_swe_env/hermes_swe_env.py: Untested module (227 LOC, 0 importers) | tools/mixture_of_agents_tool.py: No direct tests (544 LOC, 1 importers) — covered only via imports from tested mo | skills/productivity/powerpoint/scripts/office/helpers/merge_runs.py: Untested module (199 LOC, 0 importers) | skills/mlops/training/grpo-rl-training/templates/basic_grpo_training.py: Untested module (228 LOC, 0 importers) | environments/tool_call_parsers/deepseek_v3_parser.py: No direct tests (76 LOC, 1 importers) — covered only via imports from tested mod
- auto/unused_enums (2 items)
  Fix 2 unused enums issues
  severity=[unknown: 2] confidence=[high: 2] top_rules=[unknown(2)] samples: tests/tools/test_daytona_environment.py: Unused enum: _SandboxState (4 members) — never imported externally | tools/skills_tool.py: Unused enum: SkillReadinessStatus (3 members) — never imported externally
### Unclustered items (6335 items — needs human judgment or isolated findings)
Promote individually with `desloppify plan promote <issue-id>`, or group related items into a manual cluster.
- [high] cycles::environments/tool_call_parsers/__init__.py::environments/tool_call_parsers/__init__.py::environments/tool_call_parsers/deepseek_v3_1_parser.py::environments/tool_call_parsers/deepseek_v3_parser.py::environments/tool_call_parsers/glm45_parser.py::+8 — Import cycle (12 files): environments/tool_call_parsers/__init__.py -> environments/tool_call_parsers/deepseek_v3_1_parser.py -> environments/tool_call_parsers/deepseek_v3_parser.py -> environments/tool_call_parsers/glm45_parser.py -> environments/tool_call_parsers/glm47_parser.py -> +7
- [high] dict_keys::agent/autoreply.py::schema_drift::literal::73 — Schema drift: 24/27 dict literals use different key, but agent/autoreply.py:73 uses "literal".
- [high] dict_keys::agent/auxiliary_client.py::schema_drift::client::739 — Schema drift: 8/9 dict literals use different key, but agent/auxiliary_client.py:739 uses "client".
- [high] dict_keys::agent/context_compressor.py::schema_drift::timeout::124 — Schema drift: 7/8 dict literals use different key, but agent/context_compressor.py:124 uses "timeout".
- [high] dict_keys::cli.py::phantom_read::cp_cfg::max_snapshots — Dict key "max_snapshots" read at line 1107 but never written to `cp_cfg`
- [high] dict_keys::cli.py::phantom_read::defaults::auxiliary — Dict key "auxiliary" read at line 368 but never written to `defaults`
- [high] dict_keys::cli.py::phantom_read::defaults::security — Dict key "security" read at line 387 but never written to `defaults`
- [high] dict_keys::cron/scheduler.py::phantom_read::_cfg::agent — Dict key "agent" read at line 204 but never written to `_cfg`
- [high] dict_keys::cron/scheduler.py::phantom_read::_cfg::max_turns — Dict key "max_turns" read at line 231 but never written to `_cfg`
- [high] dict_keys::cron/scheduler.py::phantom_read::_cfg::model — Dict key "model" read at line 192 but never written to `_cfg`
- ... and 6325 more unclustered items
Browse full backlog: `desloppify backlog`
Inspect a cluster: `desloppify plan cluster show auto/<name>`
Inspect an issue: `desloppify show <issue-id>`


## Required Issue Hashes
Total open review issues: 45
Every one of these hashes must appear exactly once in your cluster/skip blueprint.
Do not repeat hashes outside that blueprint.
ad_hoc_temporary_agent_construction, adapters_dict_any_any, agents_md_structure_drift, allowlist_env_var_magic_strings, cache_getters_mutate_filesystem, check_ha_requirements_naming, dead_code_checkpoint_manager, defensive_hasattr_after_init, deliver_returns_sendresult_not_dict, deprecated_env_var_still_read, deprecated_on_auto_reset_param, dotenv_loading_boilerplate, dual_http_clients, duplicated_dead_countdown_check, gateway_config_yaml_reload, gateway_run_import_side_effects, gateway_run_untested_pipeline, hasattr_on_init_attributes, identical_branches_skills_sync, identical_branches_telegram_document, identical_branches_uninstall, large_tools_init_barrel, message_event_source_not_optional, mixed_logging_for_errors, model_tools_stale_snapshots, monolithic_handle_message, object_new_fragility, optional_without_annotation, orphaned_mini_swe_deps, patch_parser_duplicated_flush, platform_sys_path_split, registry_violates_own_contract, repeated_config_yaml_loading, requirements_txt_drift, scattered_config_yaml_parsing, session_db_errors_invisible, stale_probability_comments, sys_path_insert_gateway_modules, tools_init_redundant_barrel, toolset_info_returns_none, toolsets_docstring_bloat, toolsets_restating_comments, untyped_discriminator_api_mode, untyped_discriminator_reset_mode, unused_jinja2_dep

## Coverage Ledger Template
Your final report MUST contain a `## Coverage Ledger` section with one line per issue.
Allowed forms:
- `- abcd1234 -> cluster "cluster-name"`
- `- abcd1234 -> skip "specific-reason-tag"`
Do not mention hashes outside the `## Coverage Ledger` section.
- ad_hoc_temporary_agent_construction -> TODO
- adapters_dict_any_any -> TODO
- agents_md_structure_drift -> TODO
- allowlist_env_var_magic_strings -> TODO
- cache_getters_mutate_filesystem -> TODO
- check_ha_requirements_naming -> TODO
- dead_code_checkpoint_manager -> TODO
- defensive_hasattr_after_init -> TODO
- deliver_returns_sendresult_not_dict -> TODO
- deprecated_env_var_still_read -> TODO
- deprecated_on_auto_reset_param -> TODO
- dotenv_loading_boilerplate -> TODO
- dual_http_clients -> TODO
- duplicated_dead_countdown_check -> TODO
- gateway_config_yaml_reload -> TODO
- gateway_run_import_side_effects -> TODO
- gateway_run_untested_pipeline -> TODO
- hasattr_on_init_attributes -> TODO
- identical_branches_skills_sync -> TODO
- identical_branches_telegram_document -> TODO
- identical_branches_uninstall -> TODO
- large_tools_init_barrel -> TODO
- message_event_source_not_optional -> TODO
- mixed_logging_for_errors -> TODO
- model_tools_stale_snapshots -> TODO
- monolithic_handle_message -> TODO
- object_new_fragility -> TODO
- optional_without_annotation -> TODO
- orphaned_mini_swe_deps -> TODO
- patch_parser_duplicated_flush -> TODO
- platform_sys_path_split -> TODO
- registry_violates_own_contract -> TODO
- repeated_config_yaml_loading -> TODO
- requirements_txt_drift -> TODO
- scattered_config_yaml_parsing -> TODO
- session_db_errors_invisible -> TODO
- stale_probability_comments -> TODO
- sys_path_insert_gateway_modules -> TODO
- tools_init_redundant_barrel -> TODO
- toolset_info_returns_none -> TODO
- toolsets_docstring_bloat -> TODO
- toolsets_restating_comments -> TODO
- untyped_discriminator_api_mode -> TODO
- untyped_discriminator_reset_mode -> TODO
- unused_jinja2_dep -> TODO

## REFLECT Stage Instructions

Your task: using the verdicts from observe, design the cluster structure.

**A strategy is NOT a restatement of observe.** Observe says "here's what I found." Reflect
says "here's what we should DO about it, and here's what we should NOT do, and here's WHY."

**The Structured Observe Assessments table (provided below) is your primary input.** It contains
a per-issue verdict (genuine/false-positive/exaggerated/over-engineering/not-worth-it) with reasoning. Use
these verdicts as authoritative — do not second-guess observe unless you have specific evidence.

**Important: Issues with verdict `false-positive` or `exaggerated` have already been auto-skipped
by observe confirmation.** They are NOT in your issue set and do NOT need ledger entries.

For issues with verdict `over-engineering` or `not-worth-it`: observe flagged these as
questionable, but YOU decide. If you agree they're not worth fixing, skip them. If you disagree
and think the fix has value, cluster them. These are judgment calls, not factual determinations.

### What you must do:

1. **Filter:** which issues are genuine (from the observe assessments table)?
2. **Map:** for each genuine issue, what file/directory does it touch?
3. **Group:** which issues share files or directories? These become clusters.
4. **Skip:** which issues should be skipped? Apply YAGNI: if the fix is more complex than the
   problem, skip it. Valid skip reasons:
   - "the fix would add a 50-line abstraction to save 3 lines of duplication"
   - "the current code is clear and simple despite being theoretically suboptimal"
   - "observe verdict: not-worth-it — the improvement is marginal"
   - "fixing this requires touching 8 files for a naming consistency issue nobody notices"
   Invalid: "low priority" (everything is low priority compared to something)
5. **Order:** which clusters depend on others? What's the execution sequence?
6. **Check recurring patterns** — compare current issues against resolved history. If the same
   dimension keeps producing issues, that's a root cause that needs addressing, not just
   another round of fixes.
7. **Decide on auto-clusters** — auto-clusters are first-class triage candidates, not
   an afterthought. The observe stage includes cluster-level verdicts with false-positive
   rates from sampling. Use these verdicts to make informed decisions:
   - **promote**: add to the active queue. Prefer clusters with `[autofix: ...]` hints
     (lower risk) and low false-positive rates from observe sampling.
   - **skip**: explicitly skip with a reason citing the observe sampling results
     (e.g., "80% false positive rate per observe sampling", "low value").
   - **supersede**: absorb into a review cluster when the same files or root cause overlap.
   You MUST make an explicit decision for every auto-cluster. Include a `## Backlog Decisions`
   section listing each auto-cluster with: promote, skip (with reason), or supersede.
   For unclustered items: promote individually or group related ones into a manual cluster.
   The Coverage Ledger remains review-issues only — auto-clusters are covered by Backlog Decisions.
8. **Account for every issue exactly once** — every open issue hash must appear in exactly one
   cluster line or one skip line. Do not drop hashes, and do not repeat a hash in multiple
   clusters or in both a cluster and a skip.

### Your report MUST include both a coverage ledger and a concrete cluster blueprint

This blueprint is what the organize stage will execute. Be specific:
```
## Coverage Ledger
- a5996373 -> cluster "travel-structure-contract-unification"
- fb113678 -> skip "false-positive-current-code"

## Cluster Blueprint
Cluster "media-lightbox-hooks" (all in src/domains/media-lightbox/)
Cluster "task-typing" (both touch src/types/database.ts)

## Backlog Decisions
- auto/unused-imports -> promote (overlaps with the files in cluster "task-typing")
- auto/dead-code -> skip "mostly test noise, low value"
- auto/type-assertions -> supersede "absorbed into cluster task-typing"

## Skip Decisions
Skip "false-positive-current-code" (false positive per observe)
```

### Hard accounting rule

- Start your report with a `## Coverage Ledger` section.
- In that section, mention each issue hash **once and only once** on its own ledger line.
- Do **not** mention issue hashes again in cluster rationale paragraphs, recurring-pattern notes,
  or ordering explanations. After the ledger, refer to clusters by name.
- Before finishing, do a self-check: the ledger must cover all open issue hashes exactly once.

### What a LAZY reflect looks like (will be rejected):
- Restating observe findings in slightly different words
- "We should prioritize high-impact items and defer low-priority ones"
- A bulleted list of dimensions without any strategic thinking
- Ignoring recurring patterns
- No `## Coverage Ledger`
- No cluster blueprint (just vague grouping ideas)
- Missing or duplicated issue hashes

### What a GOOD reflect looks like:
- "50% false positive rate. Of 34 issues, 17 are genuine. 10 of those are batch-scriptable
  convention fixes (zero risk, 30 min) — cluster 'convention-batch'. The remaining 7 split into
  3 clusters by file proximity: 'media-lightbox-hooks' (issues X,Y,Z — all in src/domains/media-lightbox/),
  'timeline-cleanup' (issues A,B,C — touching Timeline components), 'task-typing' (issues D,E).
  Skip: issue W (false positive), issue V (over-engineering), issue U (not-worth-it:
  adds ErrorBoundary wrapper around 3 components that already handle errors inline —
  technically cleaner but doubles the JSX nesting depth for no behavioral change).
  design_coherence recurs (2 resolved, 5 open) but only 1 of the 5 actually warrants work."

When done, write a plain-text reflect report with a concrete cluster blueprint.
The orchestrator records and confirms the stage.



## Validation Requirements
- Stage must be recorded with a 100+ char report
- Report must mention recurring dimension names (if any exist)
- Report must include a `## Coverage Ledger` section
- Report must account for every open review issue exactly once (no missing or duplicate hashes)
- Stage must be confirmed with an 80+ char attestation
