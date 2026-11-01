#!/usr/bin/env bash
#
# Sequential Ollama Cloud Benchmark Runner for make-prompt-better v4.2.0
# Runs one model at a time, ordered from cheapest / smallest to flagship tier.
# Automatically updates AGGREGATED_METRICS after each model completes.
#

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

LOG_FILE="${REPO_ROOT}/research/benchmark/v4/BENCHMARK_QUEUE.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "================================================================================"
echo " Starting Ollama Cloud Sequential Benchmark Suite"
echo " Time: $(date)"
echo " Log file: ${LOG_FILE}"
echo " Repository: ${REPO_ROOT}"
echo "================================================================================"

# Models ordered from cheapest / smallest parameter to flagship tier:
# Tier 1 (Cheapest / Smallest):
#   1. gpt-oss:20b-cloud (20.9B parameter, lowest compute footprint)
#   2. gemma4:31b-cloud (31B parameter open weights)
# Tier 2 (Flash Tier - economical, fast MoE):
#   3. glm-5.3-flash:cloud (321B MoE flash)
#   4. deepseek-v4.1-flash:cloud (763B MoE flash)
#   5. deepseek-v4.1-flash:1017-cloud (763B snapshot)
#   6. minimax-m3.1-flash:cloud (428B MoE flash)
# Tier 3 (Specialized Cloud Models):
#   7. beam:cloud (501B)
#   8. muse-spark-open:cloud (822B)
# Tier 4 (Flagship Tier - large / high compute):
#   9. glm-5.3:cloud (753B flagship)
#   10. mistral-large-4:cloud (1.05T flagship)
#   11. kimi-k3:cloud (2.81T flagship)
MODELS=(
  "gpt-oss:20b-cloud"
  "gemma4:31b-cloud"
  "glm-5.3-flash:cloud"
  "deepseek-v4.1-flash:cloud"
  "deepseek-v4.1-flash:1017-cloud"
  "minimax-m3.1-flash:cloud"
  "beam:cloud"
  "muse-spark-open:cloud"
  "glm-5.3:cloud"
  "mistral-large-4:cloud"
  "kimi-k3:cloud"
)

TOTAL_MODELS=${#MODELS[@]}
SUCCESS_COUNT=0
FAILURE_COUNT=0
FAILED_MODELS=()

echo "Total models queued: ${TOTAL_MODELS}"
for idx in "${!MODELS[@]}"; do
  echo "  $((idx + 1)). ${MODELS[idx]}"
done
echo "================================================================================"

START_TOTAL=$(date +%s)

for idx in "${!MODELS[@]}"; do
  MODEL="${MODELS[idx]}"
  NUM=$((idx + 1))
  
  echo ""
  echo "################################################################################"
  echo " [${NUM}/${TOTAL_MODELS}] Starting Benchmark: ${MODEL}"
  echo " Started at: $(date)"
  echo "################################################################################"
  
  START_MODEL=$(date +%s)
  
  # Execute benchmark for this single model across all 12 tests with --no-resume
  if python3 "${REPO_ROOT}/research/benchmark/v4/run_ollama_benchmarks.py" \
      --models "${MODEL}" \
      --tests "1,2,3,4,5,6,7,8,9,10,11,12" \
      --no-resume; then
    
    ELAPSED_MODEL=$(( $(date +%s) - START_MODEL ))
    echo ">>> SUCCESS: Completed ${MODEL} in $((ELAPSED_MODEL / 60))m $((ELAPSED_MODEL % 60))s"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    ELAPSED_MODEL=$(( $(date +%s) - START_MODEL ))
    echo ">>> FAILURE: ${MODEL} exited with error after $((ELAPSED_MODEL / 60))m $((ELAPSED_MODEL % 60))s"
    FAILURE_COUNT=$((FAILURE_COUNT + 1))
    FAILED_MODELS+=("${MODEL}")
  fi
  
  # Incrementally re-aggregate overall metrics matrix so progress is immediately updated
  echo "--- Refreshing AGGREGATED_METRICS.md and AGGREGATED_METRICS.json ---"
  python3 "${REPO_ROOT}/research/benchmark/v4/aggregate_results.py" || true
  
  # 5-second polite cooldown between models to allow cloud connections to reset cleanly
  sleep 5
done

END_TOTAL=$(date +%s)
ELAPSED_TOTAL=$(( END_TOTAL - START_TOTAL ))

echo ""
echo "================================================================================"
echo " Sequential Benchmark Suite Completed"
echo " Finished at: $(date)"
echo " Total elapsed time: $((ELAPSED_TOTAL / 3600))h $(( (ELAPSED_TOTAL % 3600) / 60 ))m $((ELAPSED_TOTAL % 60))s"
echo " Successful models: ${SUCCESS_COUNT}/${TOTAL_MODELS}"
if [ ${FAILURE_COUNT} -gt 0 ]; then
  echo " Failed models: ${FAILED_MODELS[*]}"
fi
echo "================================================================================"
