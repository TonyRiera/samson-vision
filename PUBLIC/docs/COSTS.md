# Usage Costs

> Estimated costs for using Samson Vision with various LLM providers.
> Prices are per query (1,700 input + 400 output tokens ≈ one SVP interpretation).

## Per-query costs by model

| Model | Provider | Input/1M | Output/1M | **Cost/query** |
|-------|----------|:--------:|:---------:|:--------------:|
| **MiniMax-M2.1** 🏆 | MiniMax API | $0.04 | $0.16 | **$0.0008** |
| **minimax-m2.5** | OpenCode Go | $0.30 | $1.20 | **$0.0009** |
| **minimax-m3** | OpenCode Go | $0.30 | $1.20 | **$0.0009** |
| **qwen3.5-plus** | OpenCode Go | $0.40 | $1.60 | **$0.0012** |
| **kimi-k2.7-code** | OpenCode Go | $0.95 | $4.00 | **$0.0030** |
| **mimo-v2.5-pro** | OpenCode Go | $1.74 | $3.48 | **$0.0040** |
| **GPT-4o-mini** | OpenAI API | $0.15 | $0.60 | **$0.0005** |
| **GPT-4o** | OpenAI API | $2.50 | $10.00 | **$0.008** |
| **GPT-5.4-mini** | Codex CLI / OpenAI API | $0.15 | $0.60 | **~$0.0005** |
| **GPT-5.5** | Codex CLI / OpenAI API | $2.50 | $10.00 | **~$0.002** |

*Prices as of June 2026. Subject to change. Codex CLI may bill via subscription on some accounts; benchmark tables show **API per-token** equivalents (~1,700 in + 400 out tokens per query), not $20/mes plans.*

## Monthly estimates

| Daily queries | Model | Monthly cost |
|:------------:|-------|:------------:|
| 50/day | MiniMax-M2.1 | ~$1.20 |
| 100/day | MiniMax-M2.1 | ~$2.40 |
| 500/day | MiniMax-M2.1 | ~$12.00 |
| 100/day | minimax-m2.5 | ~$2.70 (OpenCode) |
| 100/day | GPT-4o-mini | ~$1.50 (OpenAI API) |

## Direct vision comparison

For context, here's how Samson SVP costs compare to using native vision models directly:

| Approach | Example | Cost/query | Quality for text |
|----------|---------|:----------:|:----------------:|
| **Samson SVP + MiniMax-M2.1** | Our stack | **$0.0008** | 90% |
| Direct vision (MiniMax-M3) | mmx vision describe | ~$0.003 | 100% (sees photos) |
| Direct vision (GPT-4o) | OpenAI vision | ~$0.008 | 100% |

**Samson SVP is 4-10x cheaper** than direct vision calls while achieving ~90% of the quality for text-heavy content.

## Saving strategies

1. **Batch processing**: Generate SVP once, interpret with multiple models
2. **Cache SVP files**: The SVP generation is deterministic (no AI cost)
3. **Tiered model selection**: Use cheaper models for simple images, premium for complex ones
4. **OpenCode Go subscription**: If you use OpenCode Go models, the $10/month subscription includes $60 in credits

## Models to avoid

These models return empty content when interpreting SVP:

| Model | Cost/query | Issue |
|-------|:----------:|-------|
| DeepSeek Flash v4 | $0.0003 | Empty response |
| GLM-5.2 | $0.0039 | Empty response |
