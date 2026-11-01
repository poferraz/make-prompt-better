#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
exec ./scripts/run_benchmarks_queue.sh
