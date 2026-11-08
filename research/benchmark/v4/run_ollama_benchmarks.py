#!/usr/bin/env python3
"""
Automated v4.0 Multi-Model Benchmark Runner for make-prompt-better (Ollama Cloud & Local).

Executes the 12-test v4.0 benchmark protocol across installed Ollama models:
  - Step A: Baseline generation (clean context, raw prompt only)
  - Step B: Prompt optimization (injects SKILL.md + domain-templates.md + research-principles.md)
  - Step C: Optimized execution (clean context, optimized prompt only)
  - Step D: Structured 5-dimension evaluation (Accuracy, Completeness, Structure, Actionability, Traceability)
  - Step E: Final Report generation across all 12 tests

Saves incremental progress after every test to:
  - .private/research/benchmark/v4/results/<model-slug>/EVALUATION_RESULTS.md
  - .private/research/benchmark/v4/results/<model-slug>/metrics.json
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import ipaddress
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    from research.benchmark.v4.blind_stats_engine import (
        build_blind_eval_instruction,
        deterministic_ab_assignment,
        merge_position_swapped_scores,
        strip_certificate_scaffolding,
        unblind_parsed_scores,
    )
except ImportError:
    from blind_stats_engine import (
        build_blind_eval_instruction,
        deterministic_ab_assignment,
        merge_position_swapped_scores,
        strip_certificate_scaffolding,
        unblind_parsed_scores,
    )

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_ROOT = REPO_ROOT / ".private" / "research" / "benchmark" / "v4" / "runs"
DEFAULT_MAX_RETRIES = 5
DEFAULT_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
# The audited predecessor saved judge output before validating it.
PRE_FIX_RUNNER_SHA256 = "79d5ea515b51233080ef7be05ee431c3a3ff837117682c1e80e075969018b635"


def migration_code_is_approved(manifest: dict, *, rejudge: bool = False) -> bool:
    try:
        approved = json.loads(Path(__file__).with_name("checkpoint-migration-hashes.json").read_text())
        return (manifest["runner_sha256"] == approved["runner_sha256"] and
                (not rejudge or manifest["code_sha256"] == approved["rejudge_sha256"]))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def has_invalid_judge_response(stages: dict) -> bool:
    for name in ("judge_1", "judge_2"):
        if name in stages:
            try:
                parse_scores(stages[name]["response"]["content"])
            except (ValueError, KeyError, TypeError):
                return True
    return False

DEFAULT_CLOUD_MODELS = [
    "glm-5.3:cloud",
    "glm-5.3-flash:cloud",
    "deepseek-v4.1-flash:cloud",
    "deepseek-v4.1-flash:1017-cloud",
    "minimax-m3.1-flash:cloud",
    "mistral-large-4:cloud",
    "kimi-k3:cloud",
    "gemma4:31b-cloud",
    "gpt-oss:20b-cloud",
    "beam:cloud",
    "muse-spark-open:cloud",
]

FAST_TIER_MODELS = [
    "glm-5.3-flash:cloud",
    "deepseek-v4.1-flash:cloud",
    "minimax-m3.1-flash:cloud",
    "gpt-oss:20b-cloud",
]

FLAGSHIP_TIER_MODELS = [
    "glm-5.3:cloud",
    "mistral-large-4:cloud",
    "kimi-k3:cloud",
    "gemma4:31b-cloud",
]

TEST_CASES: list[dict[str, Any]] = [
    {
        "id": 1,
        "domain": "Code Review",
        "task_type": "Accuracy",
        "target_mode": "Mode 1 (Max Certificate, Template 1 [P1]-[P3])",
        "raw_prompt": (
            "Look at this Python function and tell me if it has any bugs.\n\n"
            "def calculate_discount(price, discount_percent, is_member):\n"
            "    if is_member:\n"
            "        discount_percent += 10\n"
            "    final_price = price - (price * discount_percent)\n"
            "    if final_price < 0:\n"
            "        return 0\n"
            "    return final_price"
        ),
    },
    {
        "id": 2,
        "domain": "Financial Analysis",
        "task_type": "Accuracy",
        "target_mode": "Mode 1 (Max Certificate, Template 9 [P1]-[P3])",
        "raw_prompt": (
            "A company reports $50M revenue in Q1, $47M in Q2, $52M in Q3, and $61M in Q4. "
            "Operating expenses were 78% of revenue in Q1, 82% in Q2, 75% in Q3, and 71% in Q4. "
            "They took on $15M in new debt in Q3. Analyze their financial health."
        ),
    },
    {
        "id": 3,
        "domain": "Medical Reasoning",
        "task_type": "Accuracy",
        "target_mode": "Mode 1 (Max Certificate, Template 7 [P1]-[P3])",
        "raw_prompt": (
            "A 58-year-old male presents with sudden onset chest pain radiating to the left arm, "
            "diaphoresis, and shortness of breath. BP 90/60, HR 110, SpO2 94%. ECG shows ST elevation "
            "in leads II, III, and aVF. Troponin pending. What is the most likely diagnosis and what "
            "are the immediate priorities?"
        ),
    },
    {
        "id": 4,
        "domain": "Legal Analysis",
        "task_type": "Accuracy",
        "target_mode": "Mode 1 (Max Certificate, Template 8 [P1]-[P3])",
        "raw_prompt": (
            "An employee signed a non-compete agreement that prevents them from working in "
            "\"any related industry\" within a 200-mile radius for 5 years after leaving the company. "
            "They left and took a job at a competitor 150 miles away, 8 months later. The former "
            "employer is threatening to sue. Analyze the enforceability of this non-compete."
        ),
    },
    {
        "id": 5,
        "domain": "Research Synthesis",
        "task_type": "Mixed",
        "target_mode": "Mode 1 (Max Certificate, Template 3 [P1]-[P3])",
        "raw_prompt": (
            "What does the research say about whether remote work improves or hurts productivity? "
            "Give me a balanced overview."
        ),
    },
    {
        "id": 6,
        "domain": "Business Decision",
        "task_type": "Mixed",
        "target_mode": "Mode 1 (Max Certificate, Template 5 [P1]-[P3])",
        "raw_prompt": (
            "We're a 15-person SaaS startup deciding between building our own authentication system "
            "or using Auth0/Clerk. We handle sensitive healthcare data (HIPAA). What should we do?"
        ),
    },
    {
        "id": 7,
        "domain": "Compliance Check",
        "task_type": "Accuracy",
        "target_mode": "Mode 1 (Max Certificate, Template 4 [P1]-[P3])",
        "raw_prompt": (
            "Review this password policy for NIST 800-63B compliance:\n"
            "- Minimum 8 characters\n"
            "- Must include uppercase, lowercase, number, and special character\n"
            "- Passwords expire every 90 days\n"
            "- Cannot reuse last 5 passwords\n"
            "- Account locks after 3 failed attempts for 30 minutes"
        ),
    },
    {
        "id": 8,
        "domain": "Document Analysis",
        "task_type": "Mixed",
        "target_mode": "Mode 1 (Max Certificate, Template 2 [P1]-[P3])",
        "raw_prompt": (
            "Here is an executive summary from a project proposal: \"Our AI-powered customer service "
            "solution will reduce support tickets by 60% within 6 months of deployment. The system uses "
            "proprietary NLP technology that outperforms all competitors. Implementation requires minimal "
            "IT involvement and the ROI will exceed 300% in the first year.\" Analyze the credibility "
            "of these claims."
        ),
    },
    {
        "id": 9,
        "domain": "Comparative Analysis",
        "task_type": "Mixed",
        "target_mode": "Mode 2 (Lite Certificate [LITE], Template 6 [P1]-[P3], target <1.5x overhead)",
        "raw_prompt": (
            "Compare PostgreSQL and MongoDB for a new application that needs to handle both structured "
            "transaction data and semi-structured user activity logs. We expect 10M records per month "
            "growing 20% annually."
        ),
    },
    {
        "id": 10,
        "domain": "Creative Brief",
        "task_type": "Creative",
        "target_mode": "Mode 4 (Creative & Divergent v2, Template 10 [NT0] Verbalized Sampling + [SC0] Anti-SlopShape)",
        "raw_prompt": (
            "Write a product description for a new ergonomic office chair designed for people who work "
            "10+ hour days. The chair has lumbar support that auto-adjusts, breathable mesh, and a "
            "12-year warranty. Target audience is remote tech workers ages 25-45."
        ),
    },
    {
        "id": 11,
        "domain": "Context File (CLAUDE.md)",
        "task_type": "Harness",
        "target_mode": "Mode 3 (Agentic Harness [CONTEXT-FILES], Template 11, <150 lines non-inferable only)",
        "raw_prompt": (
            "Write a CLAUDE.md file for our Python FastAPI + PostgreSQL repository. Explain the project "
            "overview, list the folder structure (app/api, app/models, app/services, tests/), explain "
            "standard PEP8 coding conventions, and include our non-obvious commands: running unit tests "
            "requires `pytest -m \"not integration\" --reuse-db`, database migrations must run via "
            "`./scripts/migrate.sh check` before committing, and Redis cache keys in `app/services/billing.py` "
            "must never be mutated without bumping `SCHEMA_EPOCH`."
        ),
    },
    {
        "id": 12,
        "domain": "Async Rate Limiter (LRM)",
        "task_type": "Harness",
        "target_mode": "Mode 3 (LRM & Agentic Harness [HARNESS], Template 12 [V1]-[V3] verification gates)",
        "raw_prompt": (
            "Write a thread-safe async token bucket rate limiter in Python (`AsyncTokenBucket`) that "
            "supports burst capacity, fractional refill rates, and "
            "`acquire(tokens: int, timeout: float | None = None) -> bool`. Make sure there are no race "
            "conditions when multiple coroutines wait concurrently."
        ),
    },
]


def slugify_model(model_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", model_name.replace(":", "-")).strip("-").lower()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_host(host: str, allow_remote_http: bool = False) -> None:
    parsed = urllib.parse.urlsplit(host)
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError("host must be an HTTP(S) URL without credentials, query, or fragment")
    hostname = parsed.hostname.lower()
    try:
        loopback = hostname == "localhost" or ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        loopback = hostname == "localhost"
    if parsed.scheme == "http" and not loopback and not allow_remote_http:
        raise ValueError("remote cleartext HTTP requires --allow-remote-http")


def build_manifest(model: str, skill_bundle: str, test_ids: list[int], host: str,
                   timeout: int, judge_model: str | None, blind_eval: bool,
                   swap_positions: bool, strip_cert_markers: bool,
                   unprescribed_routing: bool, seed: int, *, skill_dir: Path | None = None,
                   strict_preservation: bool = False,
                   max_output_tokens: int | None = None) -> dict[str, Any]:
    """Bind resumable results to the exact inputs controlled by this runner."""
    return {
        "schema": 2,
        "protocol": "outcome-v2",
        "skill_dir": str(skill_dir.resolve()) if skill_dir is not None else None,
        "strict_preservation": strict_preservation,
        "max_output_tokens": max_output_tokens,
        "pricing_status": "unknown",
        "model": model,
        "judge_model": judge_model or model,
        "model_revision": "unknown: provider identifier may be mutable",
        "skill_sha256": sha256_text(skill_bundle),
        "test_suite_sha256": sha256_text(json.dumps(TEST_CASES, sort_keys=True)),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "judge_code_sha256": hashlib.sha256(Path(__file__).with_name("blind_stats_engine.py").read_bytes()).hexdigest(),
        "host_sha256": sha256_text(host),
        "test_ids": sorted(test_ids),
        "timeout": timeout,
        "blind_eval": blind_eval,
        "swap_positions": swap_positions,
        "strip_cert_markers": strip_cert_markers,
        "unprescribed_routing": unprescribed_routing,
        "seed": seed,
        "loading_strategy": "full skill, templates, and research bundle",
    }


def atomic_write(path: Path, content: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_skill_bundle(skill_dir: Path | None = None) -> str:
    root = skill_dir if skill_dir is not None else REPO_ROOT / "make-prompt-better"
    skill_md = (root / "SKILL.md").read_text(encoding="utf-8")
    templates_md = (root / "references" / "domain-templates.md").read_text(encoding="utf-8")
    principles_md = (root / "references" / "research-principles.md").read_text(encoding="utf-8")
    return (
        "# SKILL FILE 1: make-prompt-better/SKILL.md\n\n"
        f"{skill_md}\n\n"
        "# SKILL FILE 2: make-prompt-better/references/domain-templates.md\n\n"
        f"{templates_md}\n\n"
        "# SKILL FILE 3: make-prompt-better/references/research-principles.md\n\n"
        f"{principles_md}\n"
    )


def is_direct_ollama_cloud(host: str) -> bool:
    return urllib.parse.urlsplit(host).hostname == "ollama.com"


def validate_cloud_model(model: str, host: str) -> None:
    """Direct API identifiers are not local Ollama cloud-routing aliases."""
    if is_direct_ollama_cloud(host) and (
            not model.strip() or model.lower().endswith((":cloud", "-cloud"))):
        raise ValueError("Direct Ollama Cloud requires exact catalog model identifiers; "
                         "copy the API model ID from https://ollama.com/search?c=cloud, "
                         "not a local :cloud or -cloud alias")


def discover_ollama_cloud_models() -> list[str]:
    try:
        out = subprocess.check_output(["ollama", "list"], text=True, stderr=subprocess.STDOUT)
        models: list[str] = []
        for line in out.strip().splitlines()[1:]:
            parts = line.split()
            if parts and "cloud" in parts[0].lower():
                name = parts[0]
                # Filter out decision models that do not support chat API
                if "clef" in name.lower():
                    continue
                models.append(name)
        return models or DEFAULT_CLOUD_MODELS
    except Exception:
        return DEFAULT_CLOUD_MODELS


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A redirect is an extra HTTP request and can forward a bearer credential.
        return None


def open_ollama_request(request: urllib.request.Request, timeout: int):
    return urllib.request.build_opener(NoRedirectHandler()).open(request, timeout=timeout)


class OllamaStopError(RuntimeError):
    """An opt-in campaign stop with sanitized telemetry."""
    def __init__(self, reason: str, telemetry: dict):
        super().__init__(reason)
        self.reason = reason
        self.telemetry = telemetry


def usage_count(value: Any) -> int | None:
    return value if type(value) is int and value >= 0 else None


def extract_terminal_metadata(body: dict | None) -> dict:
    """Keep only bounded terminal counters; provider text and reasoning are excluded."""
    completed = isinstance(body, dict) and body.get('done') is True
    source = body if completed else {}
    reason = source.get('done_reason')
    if not isinstance(reason, str):
        reason = None
    elif reason not in {'stop', 'length', 'load', 'unload'}:
        reason = 'other'
    result = {'schema': 1, 'completed_stream': completed, 'done_reason': reason}
    for name in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration',
                 'prompt_eval_cached_count'):
        value = source.get(name)
        key = name if name.endswith('_count') else name + '_ns'
        result[key] = value if type(value) is int and 0 <= value <= 2**63 - 1 else None
    return result


def call_ollama_chat(
    model: str,
    messages: list[dict[str, str]],
    host: str = "http://localhost:11434",
    timeout: int = 600,
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = 3.0,
    seed: int = 42,
    options: dict[str, Any] | None = None,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    max_output_tokens: int | None = None,
    api_key: str | None = None,
    stop_status_codes: set[int] | None = None,
    stop_on_unknown_usage: bool = False,
    request_observer=None,
    *,
    retain_terminal_metadata: bool = False,
) -> dict[str, Any]:
    validate_cloud_model(model, host)
    if max_response_bytes <= 0:
        raise ValueError("Response size limit must be positive")
    if max_retries <= 0:
        raise RuntimeError(f"Failed after {max_retries} attempts.")
    if initial_delay < 0 or timeout <= 0:
        raise ValueError("Retries and timeout must be positive; delay must be nonnegative")
    if max_output_tokens is not None and max_output_tokens <= 0:
        raise ValueError("Output token limit must be positive")
    url = f"{host.rstrip('/')}/api/chat"
    payload_options: dict[str, Any] = {"seed": seed}
    if options:
        payload_options.update(options)
    if max_output_tokens is not None:
        payload_options["num_predict"] = max_output_tokens
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": payload_options,
    }
    data = json.dumps(payload).encode("utf-8")
    if request_observer is not None:
        request_observer(data)  # Durable evidence must exist before any request is dispatched.
    delay = initial_delay
    started = time.monotonic()
    attempts = []
    backoff = 0.0
    body = None

    def telemetry() -> dict[str, Any]:
        result = {"attempts": attempts, "attempt_count": len(attempts),
                  "retry_count": max(len(attempts) - 1, 0),
                  "backoff_seconds": backoff,
                  "total_elapsed_seconds": round(time.monotonic() - started, 4)}
        if retain_terminal_metadata:
            result['terminal'] = extract_terminal_metadata(body)
        return result

    def record_failure(err: Exception) -> None:
        attempts.append({"attempt": attempt, "status": "failed", "error": type(err).__name__ if api_key else str(err),
                         "elapsed_seconds": round(time.monotonic() - t0, 4),
                         "prompt_eval_count": usage_count(body.get("prompt_eval_count")) if body else None,
                         "eval_count": usage_count(body.get("eval_count")) if body else None})
        err.telemetry = telemetry()

    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})},
            method="POST",
        )
        t0 = time.monotonic()
        body = None
        try:
            with open_ollama_request(req, timeout=timeout) as resp:
                parts: list[str] = []
                raw_frames: list[dict[str, Any]] = []
                body = None
                received = 0
                while True:
                    line = resp.readline(max_response_bytes - received + 1)
                    if not line:
                        break
                    received += len(line)
                    if received > max_response_bytes:
                        raise ValueError(f"Ollama response exceeded size limit ({max_response_bytes} bytes)")
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except (json.JSONDecodeError, UnicodeDecodeError) as err:
                        raise ConnectionError("Ollama stream contained a malformed or truncated JSON frame") from err
                    if chunk.get("error"):
                        raise ConnectionError(f"Ollama stream error: {chunk['error']}")
                    if stop_on_unknown_usage:
                        raw_frames.append(chunk)
                    parts.append((chunk.get("message") or {}).get("content", ""))
                    if chunk.get("done") is True:
                        body = chunk
                        break
                if body is None:
                    raise ConnectionError("Ollama stream ended before the done frame")
            elapsed = round(time.monotonic() - t0, 4)
            raw_content = "".join(parts)
            content = raw_content.strip()
            if not content:
                if stop_on_unknown_usage:
                    prompt_count = usage_count(body.get("prompt_eval_count"))
                    output_count = usage_count(body.get("eval_count"))
                    attempts.append({"attempt": attempt, "status": "failed", "error": "EmptyResponse",
                                     "elapsed_seconds": elapsed, "prompt_eval_count": prompt_count,
                                     "eval_count": output_count})
                    result = {"content": content, "raw_content": raw_content, "raw_frames": raw_frames,
                              "prompt_eval_count": prompt_count, "eval_count": output_count,
                              "elapsed_seconds": elapsed, "telemetry": telemetry()}
                    if retain_terminal_metadata:
                        result['terminal'] = extract_terminal_metadata(body)
                    thinking = ((frame.get("message") or {}).get("thinking") for frame in raw_frames)
                    thinking_text = "".join(part for part in thinking if isinstance(part, str))
                    if api_key and (api_key in json.dumps(result, ensure_ascii=False) or api_key in thinking_text):
                        raise OllamaStopError("sensitive_response", telemetry())
                    reason = "unknown_usage" if prompt_count is None or output_count is None else "empty_response"
                    failure = OllamaStopError(reason, telemetry())
                    failure.response = result
                    raise failure
                raise ConnectionError("Ollama stream completed without response content")
            words = len(content.split())
            prompt_count = usage_count(body.get("prompt_eval_count"))
            output_count = usage_count(body.get("eval_count"))
            attempts.append({"attempt": attempt, "status": "success",
                             "elapsed_seconds": elapsed,
                             "prompt_eval_count": prompt_count,
                             "eval_count": output_count})
            result = {
                "content": content,
                "raw_content": raw_content,
                "words": words,
                "prompt_eval_count": prompt_count,
                "eval_count": output_count,
                "elapsed_seconds": elapsed,
                "telemetry": telemetry(),
            }
            if retain_terminal_metadata:
                result['terminal'] = extract_terminal_metadata(body)
            if stop_on_unknown_usage and (prompt_count is None or output_count is None):
                if api_key and api_key in json.dumps(result, ensure_ascii=False):
                    raise OllamaStopError("sensitive_response", telemetry())
                failure = OllamaStopError("unknown_usage", telemetry())
                failure.response = result
                raise failure
            # Polite pause to avoid bursting cloud gateways
            time.sleep(1.5)
            result['telemetry'] = telemetry()
            return result
        except urllib.error.HTTPError as err:
            record_failure(err)
            err_body = ""
            try:
                err_body = err.read(4096).decode("utf-8", errors="replace").strip()
            except Exception:
                pass
            finally:
                err.close()

            if stop_status_codes and err.code in stop_status_codes:
                raise OllamaStopError(f"http_{err.code}", telemetry()) from None
            if stop_on_unknown_usage:
                raise OllamaStopError("unknown_usage", telemetry()) from None
            # Retry transient server/gateway errors: 502, 503, 504, 500, 429, 520..527
            retryable = err.code in (502, 503, 504, 500, 429) or (520 <= err.code <= 527)
            if retryable and attempt < max_retries:
                print(
                    f"      [WARN] HTTP {err.code} ({'redacted' if api_key else err.reason}) for {model}. "
                    f"Retrying in {delay:.1f}s (attempt {attempt}/{max_retries})..."
                )
                time.sleep(delay)
                backoff += delay
                delay = min(delay * 2.0, 60.0)
                continue
            failure = RuntimeError(f"HTTP Error {err.code}" if api_key else f"HTTP Error {err.code}: {err.reason} ({err_body})")
            failure.telemetry = telemetry()
            if api_key:
                raise failure from None
            raise failure from err
        except OllamaStopError:
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionResetError, OSError, http.client.IncompleteRead) as err:
            record_failure(err)
            if stop_on_unknown_usage:
                raise OllamaStopError("unknown_usage", telemetry()) from None
            if attempt < max_retries:
                print(
                    f"      [WARN] Network error ({type(err).__name__ if api_key else err}) for {model}. "
                    f"Retrying in {delay:.1f}s (attempt {attempt}/{max_retries})..."
                )
                time.sleep(delay)
                backoff += delay
                delay = min(delay * 2.0, 60.0)
                continue
            if api_key:
                failure = RuntimeError(f"Ollama request failed: {type(err).__name__}")
                failure.telemetry = telemetry()
                raise failure from None
            raise
        except Exception as err:
            record_failure(err)
            if stop_on_unknown_usage and (not body or usage_count(body.get("prompt_eval_count")) is None or
                                          usage_count(body.get("eval_count")) is None):
                raise OllamaStopError("unknown_usage", telemetry()) from None
            if api_key:
                failure = RuntimeError(f"Ollama request failed: {type(err).__name__}")
                failure.telemetry = telemetry()
                raise failure from None
            raise

    raise RuntimeError(f"Failed after {max_retries} attempts.")


def check_preservation(raw_prompt: str, rewrite: str) -> dict[str, Any]:
    """Conservative literal-anchor audit, not a semantic preservation proof."""
    anchors = set(re.findall(r"`([^`]+)`", raw_prompt))
    anchors.update(re.findall(r"(?<![\w])\$?\d+(?:[./-]\d+)*(?:M|%|\+)?", raw_prompt))
    if "\ndef " in raw_prompt:
        code = raw_prompt[raw_prompt.index("\ndef ") + 1:]
        anchors.update(line.strip() for line in code.splitlines() if line.strip())
    normalized = " ".join(rewrite.split())
    missing = sorted(anchor for anchor in anchors if " ".join(anchor.split()) not in normalized)
    return {"method": "literal numbers, inline code, and source code lines", "missing_anchors": missing,
            "checked_anchors": len(anchors), "status": "failed" if missing else "no_literal_omissions_detected",
            "limitation": "Paraphrases can be flagged; unanchored facts and semantic constraints require review."}


def summarize_stage_usage(metrics: dict[str, Any]) -> dict[str, Any]:
    """Count each saved call once, including failed retries and invalid judges."""
    buckets: dict[str, list[dict]] = {name: [] for name in ("baseline", "optimizer", "execution", "judge", "synthesis")}
    names = {"baseline": "baseline", "optimize": "optimizer", "execute": "execution",
             "judge_1": "judge", "judge_2": "judge"}
    def collect(bucket: str, item: dict, failed: bool = False) -> None:
        response = item.get("response", {})
        telemetry = item.get("telemetry") or response.get("telemetry")
        if telemetry is None:
            telemetry = {"attempt_count": 1, "retry_count": 0,
                         "total_elapsed_seconds": response.get("elapsed_seconds"),
                         "attempts": [{"status": "failed" if failed else "success",
                                       "prompt_eval_count": response.get("prompt_eval_count"),
                                       "eval_count": response.get("eval_count")}]}
        buckets[bucket].append({**telemetry, "call_failed": failed})
    for stages in metrics.get("in_progress", {}).values():
        for name, bucket in names.items():
            if name in stages:
                collect(bucket, stages[name])
        for archive in ("failed_stage_attempts", "failed_judge_attempts"):
            for name, items in stages.get(archive, {}).items():
                for item in items:
                    collect(names[name], item, True)
    for item in metrics.get("synthesis_attempts", [metrics["final_synthesis"]] if "final_synthesis" in metrics else []):
        collect("synthesis", item)
    for item in metrics.get("failed_synthesis_attempts", []):
        collect("synthesis", item, True)
    result = {}
    for name, calls in buckets.items():
        attempts = [attempt for call in calls for attempt in call["attempts"]]
        stage = {"calls": len(calls), "failed_calls": sum(c["call_failed"] for c in calls), "attempt_count": sum(c["attempt_count"] for c in calls),
                 "retry_count": sum(c["retry_count"] for c in calls),
                 "failed_attempts": sum(a["status"] == "failed" for a in attempts)}
        for key in ("prompt_eval_count", "eval_count"):
            values = [a.get(key) for a in attempts]
            stage[key] = sum(values) if all(v is not None for v in values) else None
            stage["known_" + key] = sum(v for v in values if v is not None)
            stage["unknown_" + key + "_attempts"] = sum(v is None for v in values)
        elapsed = [c.get("total_elapsed_seconds") for c in calls]
        stage["total_elapsed_seconds"] = round(sum(elapsed), 4) if all(v is not None for v in elapsed) else None
        result[name] = stage
    return {"pricing_status": "unknown", "stages": result}


def parse_scores(eval_text: str) -> dict[str, Any]:
    dims = ["Accuracy", "Completeness", "Structure", "Actionability", "Traceability"]
    scores: dict[str, dict[str, float]] = {}
    for d in dims:
        m = re.search(rf"\|\s*\*?\*?{d}\*?\*?\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|", eval_text, re.IGNORECASE)
        if m:
            b = float(m.group(1))
            o = float(m.group(2))
            if not (1 <= b <= 5 and 1 <= o <= 5):
                raise ValueError(f"Evaluation score for {d} is outside the 1-5 rubric")
            scores[d.lower()] = {"baseline": b, "optimized": o, "delta": round(o - b, 2)}
    if len(scores) == 5:
        b_tot = sum(v["baseline"] for v in scores.values())
        o_tot = sum(v["optimized"] for v in scores.values())
    else:
        m_tot = re.search(r"\|\s*\*?\*?TOTAL\*?\*?\s*\|\s*([0-9.]+)(?:/25)?\s*\|\s*([0-9.]+)(?:/25)?\s*\|", eval_text, re.IGNORECASE)
        if not m_tot:
            raise ValueError("Evaluation did not contain five dimension scores or a total score")
        b_tot = float(m_tot.group(1))
        o_tot = float(m_tot.group(2))
        if not (5 <= b_tot <= 25 and 5 <= o_tot <= 25):
            raise ValueError("Evaluation total is outside the 5-25 rubric")
    delta_tot = round(o_tot - b_tot, 2)
    winner = "Optimized" if delta_tot > 0 else ("Baseline" if delta_tot < 0 else "Tie")
    return {
        "dimensions": scores,
        "baseline_total": b_tot,
        "optimized_total": o_tot,
        "delta_total": delta_tot,
        "winner": winner,
    }


def render_markdown_report(model: str, metrics: dict[str, Any], final_report_md: str) -> str:
    lines = [
        f"# EVALUATION RESULTS: make-prompt-better v4.0 ({model})",
        "",
        f"- **Model**: `{model}`",
        f"- **Timestamp**: `{metrics.get('updated_at', '')}`",
        f"- **Protocol**: 12-Test v4.0 Isolated Context Pipeline (Baseline -> Optimize Prompt -> Execute Optimized -> Rubric Evaluation)",
        "- **Rendering**: Dash punctuation is normalized in this report; original model output is preserved in `metrics.json`.",
        "",
    ]
    for tid_str in sorted(metrics.get("tests", {}).keys(), key=lambda x: int(x)):
        t = metrics["tests"][tid_str]
        lines.extend([
            f"## TEST {t['id']}: {t['domain']} ({t['task_type']} | {t['target_mode']})",
            "",
            "### BASELINE RESPONSE",
            "",
            t["baseline"]["content"],
            "",
            "### OPTIMIZED PROMPT",
            "",
            t["optimized_prompt"]["content"],
            "",
        ])
        executed_prompt = t.get("executed_optimized_prompt")
        if executed_prompt is not None and executed_prompt != t["optimized_prompt"]["content"].strip():
            lines.extend([
                "### EXECUTED OPTIMIZED PROMPT",
                "",
                executed_prompt,
                "",
            ])
        lines.extend([
            "### OPTIMIZED RESPONSE",
            "",
            t["optimized_response"]["content"],
            "",
            f"### EVALUATION: TEST {t['id']}",
            "",
            f"- **Word Count**: Baseline `{t['baseline']['words']}` words | Optimized `{t['optimized_response']['words']}` words | Ratio `{t['word_overhead_ratio']}x`",
            f"- **Eval Tokens**: Baseline `{t['baseline']['eval_count']}` | Optimized `{t['optimized_response']['eval_count']}`",
            "",
            t["evaluation"]["content"],
            "",
            "---",
            "",
        ])
    if final_report_md:
        lines.extend([
            "## FINAL REPORT",
            "",
            final_report_md,
            "",
        ])
    return "\n".join(lines).replace("\u2014", ";").replace("\u2013", "-")


def run_model_benchmark(
    model: str,
    skill_bundle: str,
    test_ids: list[int] | None = None,
    host: str = "http://localhost:11434",
    resume: bool = True,
    timeout: int = 600,
    judge_model: str | None = None,
    blind_eval: bool = True,
    swap_positions: bool = False,
    strip_cert_markers: bool = False,
    unprescribed_routing: bool = False,
    seed: int = 42,
    results_dir: Path | None = None,
    allow_remote_http: bool = False,
    skill_dir: Path | None = None,
    strict_preservation: bool = False,
    max_output_tokens: int | None = None,
) -> bool:
    if not model or slugify_model(model) in {"", ".", ".."}:
        raise ValueError("Invalid model identifier")
    validate_host(host, allow_remote_http)
    if timeout <= 0 or (max_output_tokens is not None and max_output_tokens <= 0):
        raise ValueError("Timeout and output token limit must be positive")
    root = results_dir if results_dir is not None else RESULTS_ROOT
    root.mkdir(parents=True, exist_ok=True)
    lock = root / f".{slugify_model(model)}.lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise RuntimeError(f"Benchmark run is locked: {lock}") from exc
    try:
        return _run_model_benchmark(model, skill_bundle, test_ids, host, resume, timeout,
                                    judge_model, blind_eval, swap_positions, strip_cert_markers,
                                    unprescribed_routing, seed, results_dir, skill_dir,
                                    strict_preservation, max_output_tokens)
    finally:
        lock.rmdir()


def _run_model_benchmark(
    model: str,
    skill_bundle: str,
    test_ids: list[int] | None,
    host: str,
    resume: bool,
    timeout: int,
    judge_model: str | None,
    blind_eval: bool,
    swap_positions: bool,
    strip_cert_markers: bool,
    unprescribed_routing: bool,
    seed: int,
    results_dir: Path | None,
    skill_dir: Path | None = None,
    strict_preservation: bool = False,
    max_output_tokens: int | None = None,
) -> bool:
    if test_ids is None:
        test_ids = [tc["id"] for tc in TEST_CASES]
    valid_ids = {tc["id"] for tc in TEST_CASES}
    if not test_ids or len(test_ids) != len(set(test_ids)) or not set(test_ids) <= valid_ids:
        raise ValueError("Requested test IDs must be unique and belong to the test suite")
    if not model or slugify_model(model) in {"", ".", ".."}:
        raise ValueError("A nonempty model identifier is required")
    if swap_positions and not blind_eval:
        raise ValueError("Position swapping requires blinded evaluation")
    manifest = build_manifest(model, skill_bundle, test_ids, host, timeout, judge_model,
                              blind_eval, swap_positions, strip_cert_markers,
                              unprescribed_routing, seed, skill_dir=skill_dir,
                              strict_preservation=strict_preservation, max_output_tokens=max_output_tokens)
    slug = slugify_model(model)
    out_dir = (results_dir if results_dir is not None else RESULTS_ROOT) / slug
    metrics_path = out_dir / "metrics.json"
    md_path = out_dir / "EVALUATION_RESULTS.md"

    if metrics_path.exists():
        if not resume:
            raise FileExistsError(f"Refusing to overwrite existing results: {metrics_path}; choose a new run")
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        if metrics.get("manifest") != manifest:
            previous = metrics.get("manifest")
            expected_old = dict(manifest, runner_sha256=PRE_FIX_RUNNER_SHA256)
            damaged = any(has_invalid_judge_response(stages) for stages in metrics.get("in_progress", {}).values())
            if previous != expected_old or not damaged or not migration_code_is_approved(manifest):
                raise ValueError(f"Experiment manifest missing or mismatched: {metrics_path}; choose a new run")
            metrics.setdefault("previous_manifests", []).append(previous)
            metrics.setdefault("manifest_migrations", []).append("Migrated audited pre-fix runner to retry invalid judge output")
            metrics["manifest"] = manifest
            atomic_write(metrics_path, json.dumps(metrics, indent=2))
    else:
        if out_dir.exists() and any(out_dir.iterdir()):
            raise FileExistsError(f"Refusing to overwrite nonempty result directory: {out_dir}")
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "model": model,
            "slug": slug,
            "version": "4.5.1",
            "source_state": "working tree; exact inputs are identified by manifest hashes",
            "manifest": manifest,
            "tests": {},
            "in_progress": {},
            "summary": {},
        }
        atomic_write(metrics_path, json.dumps(metrics, indent=2))
    metrics.setdefault("in_progress", {})
    metrics["judge_model"] = judge_model or model
    metrics["self_judged"] = ((judge_model or model) == model)
    metrics["unprescribed_routing"] = unprescribed_routing
    chat_options = {}
    if max_output_tokens is not None:
        chat_options["max_output_tokens"] = max_output_tokens
    if os.environ.get("OLLAMA_API_KEY"):
        chat_options["api_key"] = os.environ["OLLAMA_API_KEY"]

    print(f"\n============================================================")
    print(f"Running Benchmark for Model: {model} -> {out_dir}")
    print(f"============================================================")

    if (resume and metrics.get("final_report_md") and md_path.exists()
            and "Synthesis analysis generation encountered error:" not in metrics["final_report_md"]
            and metrics.get("summary", {}).get("completed_tests") == len(metrics["tests"])
            and all(str(tid) in metrics["tests"] for tid in test_ids)):
        print("  [SKIP] Requested tests and final report already exist.")
        return True

    for tc in TEST_CASES:
        tid = tc["id"]
        if tid not in test_ids:
            continue
        if resume and str(tid) in metrics["tests"]:
            print(f"  [Test {tid:02d}] Skipping (already completed in metrics.json)")
            continue

        print(f"  [Test {tid:02d}/{len(TEST_CASES)}] {tc['domain']} ({tc['target_mode']})...")

        try:
            stages = metrics["in_progress"].setdefault(str(tid), {})

            def stage_call(name: str, stage_model: str, messages: list[dict[str, str]],
                           validate_judge: bool = False) -> dict[str, Any]:
                request = {"model": stage_model, "messages": messages, "seed": seed}
                if name in stages:
                    if stages[name]["request"] != request:
                        raise ValueError(f"Saved stage request differs: test {tid}, {name}")
                    if not validate_judge:
                        return stages[name]["response"]
                    try:
                        parse_scores(stages[name]["response"]["content"])
                    except (ValueError, KeyError, TypeError) as exc:
                        failed = stages.pop(name)
                        failed["error"] = str(exc)
                        stages.setdefault("failed_judge_attempts", {}).setdefault(name, []).append(failed)
                        atomic_write(metrics_path, json.dumps(metrics, indent=2))
                    else:
                        return stages[name]["response"]
                try:
                    result = call_ollama_chat(model=stage_model, messages=messages, host=host,
                                              timeout=timeout, seed=seed, **chat_options)
                except Exception as exc:
                    failed = {"request": request, "error": str(exc),
                              "telemetry": getattr(exc, "telemetry", None)}
                    stages.setdefault("failed_stage_attempts", {}).setdefault(name, []).append(failed)
                    raise
                stages[name] = {"request": request, "response": result}
                atomic_write(metrics_path, json.dumps(metrics, indent=2))
                if validate_judge:
                    try:
                        parse_scores(result["content"])
                    except (ValueError, KeyError, TypeError) as exc:
                        failed = stages.pop(name)
                        failed["error"] = str(exc)
                        stages.setdefault("failed_judge_attempts", {}).setdefault(name, []).append(failed)
                        atomic_write(metrics_path, json.dumps(metrics, indent=2))
                        raise
                return result

            # Step A: Baseline Response (isolated context)
            print(f"    -> Step A: Generating Baseline response...")
            base_res = stage_call("baseline", model, [{"role": "user", "content": tc["raw_prompt"]}])

            # Step B: Optimize Prompt using make-prompt-better
            print(
                f"    -> Step B: Applying make-prompt-better "
                f"({'unprescribed router' if unprescribed_routing else tc['target_mode']})..."
            )
            routing_line = (
                "- Mode & Template Selection: Classify the task and select the optimal Mode (1..4) and Template (1..12) from the skill instructions.\n"
                if unprescribed_routing
                else f"- Required Mode & Template: {tc['target_mode']}\n"
            )
            opt_prompt_instruction = (
                "You are applying the `make-prompt-better` prompt optimization skill.\n\n"
                f"{skill_bundle}\n\n"
                "---\n"
                f"TASK: Rewrite the following raw prompt using `make-prompt-better`.\n"
                f"- Domain: {tc['domain']}\n"
                f"{routing_line}\n"
                "RAW PROMPT TO OPTIMIZE:\n"
                f"```\n{tc['raw_prompt']}\n```\n\n"
                "CRITICAL INSTRUCTIONS FOR THE OPTIMIZED PROMPT:\n"
                "1. Preserve every requested deliverable, sub-question, ordering requirement, and operational constraint from the RAW PROMPT.\n"
                "2. The rewritten prompt MUST BE 100% SELF-CONTAINED (Portable Mode). It will be sent to a separate fresh LLM with no memory.\n"
                "3. You MUST embed all code, data, numbers, requirements, and facts from the RAW PROMPT directly inside the rewritten prompt (e.g. inside the premises, input section, or code fence). Never leave placeholders like '[insert code here]' or refer to external context.\n"
                "4. Output ONLY the rewritten, ready-to-execute Optimized Prompt. Do not answer the prompt yet, and do not wrap in conversational chatter."
            )
            opt_prompt_res = stage_call("optimize", model, [{"role": "user", "content": opt_prompt_instruction}])

            # Step C: Execute Optimized Prompt (isolated context)
            print(f"    -> Step C: Generating Optimized response...")
            opt_prompt_to_send = opt_prompt_res["content"].strip()
            preservation = check_preservation(tc["raw_prompt"], opt_prompt_to_send)
            stages["preservation"] = preservation
            atomic_write(metrics_path, json.dumps(metrics, indent=2))
            if not strict_preservation:
                # Guardrail: Ensure input data / code is never starved if the model emitted an abstract outline
                if tc["id"] == 1 and "def calculate_discount" not in opt_prompt_to_send:
                    opt_prompt_to_send += f"\n\n### CODE UNDER REVIEW:\n```python\n{tc['raw_prompt']}\n```"
                elif tc["id"] == 2 and "$50M" not in opt_prompt_to_send:
                    opt_prompt_to_send += f"\n\n### FINANCIAL DATA:\n{tc['raw_prompt']}"
                elif tc["id"] == 3 and "58-year-old" not in opt_prompt_to_send:
                    opt_prompt_to_send += f"\n\n### PATIENT CLINICAL DATA:\n{tc['raw_prompt']}"
                elif tc["id"] == 4 and "200-mile" not in opt_prompt_to_send:
                    opt_prompt_to_send += f"\n\n### CONTRACT & CASE FACTS:\n{tc['raw_prompt']}"
                elif tc["id"] == 7 and "NIST" not in opt_prompt_to_send:
                    opt_prompt_to_send += f"\n\n### POLICY UNDER REVIEW:\n{tc['raw_prompt']}"
                elif tc["id"] == 8 and "60%" not in opt_prompt_to_send:
                    opt_prompt_to_send += f"\n\n### PROPOSAL TEXT:\n{tc['raw_prompt']}"
            opt_exec_res = stage_call("execute", model, [{"role": "user", "content": opt_prompt_to_send}])

            # Step D: Evaluate Baseline vs. Optimized
            effective_judge = judge_model or model
            print(
                f"    -> Step D: Scoring Baseline vs. Optimized on 5 dimensions "
                f"(judge={effective_judge}, blind={blind_eval}, swap={swap_positions})..."
            )

            if blind_eval:
                mapping_p1 = deterministic_ab_assignment(seed, model, tc["id"])
                resp_a_p1 = base_res["content"] if mapping_p1["A"] == "baseline" else opt_exec_res["content"]
                resp_b_p1 = opt_exec_res["content"] if mapping_p1["B"] == "optimized" else base_res["content"]

                eval_instruction_p1 = build_blind_eval_instruction(
                    tc, resp_a_p1, resp_b_p1, strip_markers=strip_cert_markers
                )
                eval_res = stage_call("judge_1", effective_judge, [{"role": "user", "content": eval_instruction_p1}], validate_judge=True)
                parsed_p1 = unblind_parsed_scores(parse_scores(eval_res["content"]), mapping_p1)

                if swap_positions:
                    mapping_p2 = {"A": mapping_p1["B"], "B": mapping_p1["A"]}
                    eval_instruction_p2 = build_blind_eval_instruction(
                        tc, resp_b_p1, resp_a_p1, strip_markers=strip_cert_markers
                    )
                    eval_res_p2 = stage_call("judge_2", effective_judge, [{"role": "user", "content": eval_instruction_p2}], validate_judge=True)
                    parsed_p2 = unblind_parsed_scores(parse_scores(eval_res_p2["content"]), mapping_p2)
                    parsed = merge_position_swapped_scores(parsed_p1, parsed_p2)
                else:
                    parsed = parsed_p1
            else:
                eval_instruction = (
                    "You are an independent, rigorous evaluator scoring two responses (Baseline vs. Optimized) to the same task.\n\n"
                    f"ORIGINAL TASK ({tc['domain']} - {tc['task_type']}):\n{tc['raw_prompt']}\n\n"
                    f"TARGET v4.0 MODE TESTED: {tc['target_mode']}\n\n"
                    f"=== BASELINE RESPONSE ({base_res['words']} words) ===\n{base_res['content']}\n\n"
                    f"=== OPTIMIZED PROMPT ===\n{opt_prompt_res['content']}\n\n"
                    f"=== OPTIMIZED RESPONSE ({opt_exec_res['words']} words) ===\n{opt_exec_res['content']}\n\n"
                    "Score BOTH responses honestly on a 1-5 scale (integers or .5 increments) across Accuracy, Completeness, Structure, Actionability, and Traceability.\n"
                    "If both are equal, score them equal. If certificate structure added unhelpful bloat, penalize Structure.\n\n"
                    "Return this exact markdown table followed by a 2-3 sentence explanation of what specifically improved, stayed the same, or got worse:\n\n"
                    "| Dimension     | Baseline | Optimized | Delta |\n"
                    "|---------------|----------|-----------|-------|\n"
                    "| Accuracy      | X        | Y         | +Z    |\n"
                    "| Completeness  | X        | Y         | +Z    |\n"
                    "| Structure     | X        | Y         | +Z    |\n"
                    "| Actionability | X        | Y         | +Z    |\n"
                    "| Traceability  | X        | Y         | +Z    |\n"
                    "| TOTAL         | XX/25    | YY/25     | +ZZ   |\n"
                )
                eval_res = stage_call("judge_1", effective_judge, [{"role": "user", "content": eval_instruction}], validate_judge=True)
                parsed = parse_scores(eval_res["content"])

            b_tokens = base_res.get("eval_count")
            o_tokens = opt_exec_res.get("eval_count")
            extra_tokens = o_tokens - b_tokens if b_tokens is not None and o_tokens is not None else None
            lift_per_1k_tokens = (round(parsed["delta_total"] / extra_tokens * 1000, 2)
                                  if extra_tokens is not None and extra_tokens > 0 else None)
            b_words = max(base_res["words"], 1)
            o_words = opt_exec_res["words"]
            ratio = round(o_words / b_words, 2)

            metrics["tests"][str(tid)] = {
                "id": tid,
                "domain": tc["domain"],
                "task_type": tc["task_type"],
                "target_mode": ("Unprescribed (model selection unverified)" if unprescribed_routing else tc["target_mode"]),
                "raw_prompt": tc["raw_prompt"],
                "judge_model": effective_judge,
                "self_judged": (effective_judge == model),
                "lift_per_1k_tokens": lift_per_1k_tokens,
                "baseline": base_res,
                "optimized_prompt": opt_prompt_res,
                "executed_optimized_prompt": opt_prompt_to_send,
                "preservation": preservation,
                "optimized_response": opt_exec_res,
                "evaluation": {
                    "content": eval_res["content"],
                    "parsed": parsed,
                    "passes": ([{"content": eval_res["content"], "mapping": mapping_p1}] +
                               ([{"content": eval_res_p2["content"], "mapping": mapping_p2}] if swap_positions else [])
                               if blind_eval else [{"content": eval_res["content"], "mapping": None}]),
                },
                "word_overhead_ratio": ratio,
            }
            metrics["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            metrics["telemetry"] = summarize_stage_usage(metrics)
            # Save incremental progress after every test
            atomic_write(metrics_path, json.dumps(metrics, indent=2))
            atomic_write(md_path, render_markdown_report(model, metrics, metrics.get("final_report_md", "")))
            print(
                f"    -> Saved Test {tid:02d}: Baseline={parsed['baseline_total']}/25, "
                f"Optimized={parsed['optimized_total']}/25 (Delta={parsed['delta_total']:+g}, Overhead={ratio}x)"
            )
        except Exception as test_err:
            metrics.setdefault("failures", []).append({"test_id": tid, "error": str(test_err)})
            metrics["telemetry"] = summarize_stage_usage(metrics)
            atomic_write(metrics_path, json.dumps(metrics, indent=2))
            print(f"    [ERROR] Test {tid:02d} failed for {model}: {test_err}. Continuing with remaining tests...")

    # Compute aggregate summary stats
    completed = [metrics["tests"][k] for k in sorted(metrics["tests"].keys(), key=lambda x: int(x))]
    if not completed:
        return False

    avg_b = round(sum(t["evaluation"]["parsed"]["baseline_total"] for t in completed) / len(completed), 2)
    avg_o = round(sum(t["evaluation"]["parsed"]["optimized_total"] for t in completed) / len(completed), 2)
    avg_d = round(avg_o - avg_b, 2)
    avg_ratio = round(sum(t["word_overhead_ratio"] for t in completed) / len(completed), 2)
    wins = sum(1 for t in completed if t["evaluation"]["parsed"]["winner"] == "Optimized")
    ties = sum(1 for t in completed if t["evaluation"]["parsed"]["winner"] == "Tie")
    losses = sum(1 for t in completed if t["evaluation"]["parsed"]["winner"] == "Baseline")

    summary_rows = [
        "| Test | Domain | Task Type | Mode | Baseline /25 | Optimized /25 | Delta | Words (B/O/Ratio) | Winner |",
        "|------|--------|-----------|------|--------------|---------------|-------|-------------------|--------|",
    ]
    for t in completed:
        p = t["evaluation"]["parsed"]
        mode_short = t["target_mode"].split("(")[0].strip()
        words_col = f"{t['baseline']['words']}/{t['optimized_response']['words']} ({t['word_overhead_ratio']}x)"
        summary_rows.append(
            f"| {t['id']} | {t['domain']} | {t['task_type']} | {mode_short} | "
            f"{p['baseline_total']}/25 | {p['optimized_total']}/25 | {p['delta_total']:+g} | {words_col} | {p['winner']} |"
        )
    summary_rows.append(
        f"| **AVG** | **ALL ({len(completed)} tests)** | - | - | **{avg_b}/25** | **{avg_o}/25** | "
        f"**{avg_d:+g}** | **Avg {avg_ratio}x** | **{wins}W-{ties}T-{losses}L** |"
    )
    summary_table_md = "\n".join(summary_rows)

    print(f"  [Final Report] Generating 9-section synthesis for {model}...")
    final_prompt = (
        f"You have completed {len(completed)} of the 12 configured tests using model `{model}`. Exact input and protocol hashes are in the saved manifest.\n\n"
        f"Here is the Summary Table of your results:\n\n{summary_table_md}\n\n"
        "Write the 9 Analysis Sections for this descriptive run:\n"
        "1. Overall Verdict\n"
        "2. Where It Helped Most\n"
        "3. Where It Helped Least (or Hurt)\n"
        "4. Mode and routing observations, distinguishing prescribed targets from unverified model choices\n"
        "5. Accuracy vs. Mixed vs. Creative vs. Harness\n"
        "6. Traceability Specifically\n"
        "7. Token Cost vs. Value\n"
        "8. Failure Modes Observed\n"
        "9. Recommendations and limitations for future evaluation\n\n"
        "Do not use em dashes or en dashes; use commas, colons, or semicolons."
    )
    final_content = ""
    report_ok = True
    try:
        final_res = call_ollama_chat(
            model=model,
            messages=[{"role": "user", "content": final_prompt}],
            host=host,
            timeout=timeout,
            seed=seed,
            **chat_options,
        )
        final_content = final_res["content"]
        if "synthesis_attempts" not in metrics:
            metrics["synthesis_attempts"] = [metrics["final_synthesis"]] if "final_synthesis" in metrics else []
        metrics["final_synthesis"] = {"request": final_prompt, "response": final_res}
        metrics["synthesis_attempts"].append(metrics["final_synthesis"])
    except Exception as exc:
        metrics.setdefault("failed_synthesis_attempts", []).append({"error": str(exc),
            "telemetry": getattr(exc, "telemetry", None)})
        print(f"  [WARN] Final synthesis generation failed for {model}: {exc}. Preserving summary metrics.")
        final_content = f"Synthesis analysis generation encountered error: {exc}"
        report_ok = False

    final_report_md = f"### Summary Table\n\n{summary_table_md}\n\n### Analysis Sections\n\n{final_content}"

    measured_lifts = [t["lift_per_1k_tokens"] for t in completed if t.get("lift_per_1k_tokens") is not None]
    avg_lift_per_1k = round(sum(measured_lifts) / len(measured_lifts), 2) if measured_lifts else None
    metrics["summary"] = {
        "completed_tests": len(completed),
        "avg_baseline": avg_b,
        "avg_optimized": avg_o,
        "avg_delta": avg_d,
        "avg_word_overhead_ratio": avg_ratio,
        "avg_lift_per_1k_tokens": avg_lift_per_1k,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "judge_model": judge_model or model,
        "self_judged": ((judge_model or model) == model),
    }
    metrics["telemetry"] = summarize_stage_usage(metrics)
    metrics["final_report_md"] = final_report_md
    atomic_write(metrics_path, json.dumps(metrics, indent=2))
    atomic_write(md_path, render_markdown_report(model, metrics, final_report_md))
    requested_complete = all(str(tid) in metrics["tests"] for tid in test_ids)
    status = "DONE" if requested_complete and report_ok else "PARTIAL"
    print(f"  [{status}] {model}: {len(completed)}/12 tests, Avg {avg_b}/25 -> {avg_o}/25 ({avg_d:+g}), Overhead {avg_ratio}x ({wins}W-{ties}T-{losses}L)")
    return requested_complete and report_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Run make-prompt-better v4.0 benchmarks across Ollama Cloud models.")
    parser.add_argument(
        "--models",
        type=str,
        default="",
        help="Comma-separated model IDs. Required for direct ollama.com; use exact catalog API IDs there, not local :cloud aliases.",
    )
    parser.add_argument(
        "--tier",
        choices=["fast", "flagship", "all-cloud", "installed-cloud"],
        default="installed-cloud",
        help="Preset model group to run if --models is not passed (default: installed-cloud).",
    )
    parser.add_argument(
        "--tests",
        type=str,
        default="1,2,3,4,5,6,7,8,9,10,11,12",
        help="Comma-separated test IDs to run (default: 1..12).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        help="Ollama HTTP API host (default: http://localhost:11434).",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start from scratch; refuses to overwrite a populated run directory.",
    )
    parser.add_argument("--skill-dir", type=Path, default=None, help="Alternate skill directory containing SKILL.md and references.")
    parser.add_argument("--strict-preservation", action="store_true", help="Execute the rewrite unchanged without source repairs.")
    parser.add_argument("--max-output-tokens", type=int, default=None, help="Positive output limit for every generation stage.")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_ROOT,
                        help="Parent directory for new runs (default: .private/research/benchmark/v4/runs).")
    parser.add_argument("--run-id", default=None,
                        help="Run identifier; provide the same identifier to resume. Defaults to a new unique ID.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show result path and call estimate without requests or file writes.")
    parser.add_argument("--max-requests", type=int, default=None,
                        help="Reject runs whose worst-case HTTP request count exceeds this limit.")
    parser.add_argument("--allow-remote-http", action="store_true",
                        help="Explicitly permit unencrypted HTTP to a non-loopback host.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Per-request HTTP timeout in seconds (default: 600).",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default=None,
        help="Independent model to act as evaluator in Step D (prevents self-preference bias).",
    )
    parser.add_argument(
        "--unblinded",
        action="store_true",
        help="Disable blinded A/B response anonymization and revert to legacy labeled headers.",
    )
    parser.add_argument(
        "--swap-positions",
        action="store_true",
        help="Run two evaluation passes with swapped (A, B) and (B, A) order to investigate position effects.",
    )
    parser.add_argument(
        "--strip-cert-markers",
        action="store_true",
        help="Strip [P1], [T1], [V1], and certificate mode tags before judging.",
    )
    parser.add_argument(
        "--unprescribed-routing",
        action="store_true",
        help="Do not prescribe target_mode in Step B; evaluate the skill's native mode routing.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic seed for generation and blind A/B assignment (default: 42).",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List local cloud aliases, or show the direct Ollama Cloud catalog URL, and exit.",
    )
    args = parser.parse_args()

    try:
        validate_host(args.host, args.allow_remote_http)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.list_models and is_direct_ollama_cloud(args.host):
        print("Choose exact API model identifiers from https://ollama.com/search?c=cloud "
              "and pass --models explicitly. Local discovery and presets do not apply.")
        return 0

    if is_direct_ollama_cloud(args.host):
        if not args.models.strip():
            print("Error: direct Ollama Cloud requires explicit --models from the catalog; "
                  "local discovery and tier presets do not apply", file=sys.stderr)
            return 1
        try:
            for model in args.models.split(","):
                validate_cloud_model(model.strip(), args.host)
            if args.judge_model is not None:
                validate_cloud_model(args.judge_model, args.host)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if args.list_models:
        discovered = discover_ollama_cloud_models()
        print("Discovered Ollama Cloud models:")
        for m in discovered:
            print(f"  - {m} (slug: {slugify_model(m)})")
        return 0

    if args.models.strip():
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.tier == "fast":
        models = FAST_TIER_MODELS
    elif args.tier == "flagship":
        models = FLAGSHIP_TIER_MODELS
    elif args.tier == "all-cloud":
        models = DEFAULT_CLOUD_MODELS
    else:
        models = discover_ollama_cloud_models()

    try:
        test_ids = [int(x.strip()) for x in args.tests.split(",") if x.strip()]
    except ValueError:
        print("Error: --tests must be comma-separated integers", file=sys.stderr)
        return 1
    valid_ids = {tc["id"] for tc in TEST_CASES}
    if not models or not test_ids or len(test_ids) != len(set(test_ids)) or not set(test_ids) <= valid_ids:
        print("Error: specify at least one model and unique valid test IDs", file=sys.stderr)
        return 1
    if len({slugify_model(model) for model in models}) != len(models):
        print("Error: model identifiers have colliding result paths", file=sys.stderr)
        return 1
    if args.timeout <= 0 or (args.max_output_tokens is not None and args.max_output_tokens <= 0) or (args.swap_positions and args.unblinded):
        print("Error: timeout must be positive and swapping requires blind evaluation", file=sys.stderr)
        return 1
    run_id = args.run_id or f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", run_id) or run_id in {".", ".."}:
        print("Error: invalid --run-id", file=sys.stderr)
        return 1
    run_dir = args.results_dir / run_id
    stages = len(models) * (len(test_ids) * (4 + int(args.swap_positions)) + 1)
    worst_requests = stages * DEFAULT_MAX_RETRIES
    if args.max_requests is not None and (args.max_requests < 0 or worst_requests > args.max_requests):
        print(f"Error: up to {worst_requests} HTTP requests exceed --max-requests", file=sys.stderr)
        return 1
    skill_bundle = load_skill_bundle(args.skill_dir) if args.skill_dir is not None else load_skill_bundle()

    print(f"Loaded make-prompt-better skill bundle ({len(skill_bundle.splitlines())} lines).")
    print(f"Target models ({len(models)}): {', '.join(models)}")
    print(f"Target tests ({len(test_ids)}): {test_ids}")
    print(f"Run ID: {run_id}; result directory: {run_dir}")
    print(f"Planned generation stages: {stages}; maximum HTTP requests with retries: {worst_requests}")
    if args.dry_run:
        return 0

    failures: list[tuple[str, str]] = []
    for model in models:
        try:
            complete = run_model_benchmark(
                model=model,
                skill_bundle=skill_bundle,
                test_ids=test_ids,
                host=args.host,
                resume=not args.no_resume,
                timeout=args.timeout,
                judge_model=args.judge_model,
                blind_eval=not args.unblinded,
                swap_positions=args.swap_positions,
                strip_cert_markers=args.strip_cert_markers,
                unprescribed_routing=args.unprescribed_routing,
                seed=args.seed,
                results_dir=run_dir,
                allow_remote_http=args.allow_remote_http,
                skill_dir=args.skill_dir,
                strict_preservation=args.strict_preservation,
                max_output_tokens=args.max_output_tokens,
            )
            if not complete:
                failures.append((model, "requested tests or final report are incomplete"))
        except Exception as exc:
            print(f"  [ERROR] Model {model} failed: {exc}", file=sys.stderr)
            failures.append((model, str(exc)))

    if failures:
        print("\nSome models encountered errors:")
        for m, err in failures:
            print(f"  - {m}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
