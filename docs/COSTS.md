# 💰 Costes Reales — Samson Vision

> Precios oficiales verificados a Junio 2026. Todos los precios en USD salvo indicación contraria.

## Proveedores y Planes

| Proveedor | Plan | Coste fijo | Modelos accesibles |
|-----------|------|:----------:|--------------------|
| **OpenCode Go** | Suscripción mensual | **$10/mes** | Todos los modelos vía API unificada |
| **MiniMax** | Token Plan | **~$50/mes** | M3, M2.7, M2.5, M2.1 (mmx CLI) |
| **ChatGPT Plus** | Suscripción | **$20/mes** | gpt-5.5, gpt-5.4-mini (Codex) |

OpenCode Go tiene un límite de **$60/mes en crédito interno**. Eso significa que con $10 de suscripción tienes $60 de uso incluido. Si lo superas, pagas las tarifas por token.

## Precios por modelo (por 1M tokens)

### OpenCode Go — Tarifas internas (se descuentan del saldo de $60/mes)

| Modelo | Input/1M | Output/1M | Caché/1M |
|--------|:--------:|:---------:|:--------:|
| **DeepSeek V4 Flash** | $0.14 | $0.28 | $0.0028 |
| **MiMo V2.5** | $0.14 | $0.28 | $0.0028 |
| **MiniMax M3 / M2.7 / M2.5** | **$0.30** | **$1.20** | $0.06 |
| **Qwen3.7 Plus** (≤256K) | $0.40 | $1.60 | $0.04 |
| **Kimi K2.7 Code** | $0.95 | $4.00 | $0.19 |
| **Kimi K2.6** | $0.95 | $4.00 | $0.16 |
| **GLM-5.2 / 5.1** | $1.40 | $4.40 | $0.26 |
| **MiMo V2.5 Pro** | $1.74 | $3.48 | $0.0145 |
| **DeepSeek V4 Pro** | $1.74 | $3.48 | $0.0145 |
| **Qwen3.6 Plus** (>256K) | $2.00 | $6.00 | $0.20 |
| **Qwen3.7 Max** | $2.50 | $7.50 | $0.50 |

### MiniMax API directa (vía mmx CLI) — Precios oficiales en ¥

| Modelo | Input ¥/1M | Output ¥/1M | Cache Read ¥/1M |
|--------|:---------:|:----------:|:--------------:|
| **M3** (≤512K, 50% off) | ¥2.10 | ¥8.40 | ¥0.42 |
| **M3** (>512K, 50% off) | ¥4.20 | ¥16.80 | ¥0.84 |
| **M2.7** | ¥2.10 | ¥8.40 | ¥0.42 |
| **M2.7-highspeed** | ¥4.20 | ¥16.80 | ¥0.42 |
| **M2.5** | ¥2.10 | ¥8.40 | ¥0.21 |
| **M2.1** | ¥2.10 | ¥8.40 | ¥0.21 |

*Tipo de cambio: ~1 USD = 7.2 CNY*

### ChatGPT Plus (Codex) — $20/mes fijo

Sin coste por token. Sin coste por llamada. Límites de tasa (rate limits) de OpenAI a cuentas Plus.

## Coste por consulta Samson VBP

Una consulta típica: **1.700 tokens input + 400 tokens output** = 2.100 tokens.

| Modelo | Via | Input | Output | **Coste/query** |
|--------|-----|:-----:|:------:|:--------------:|
| **MiniMax-M2.1** 🏆 | mmx CLI | ¥0.0036 | ¥0.0034 | **~$0.0008** |
| **minimax-m2.5** | OpenCode | $0.0005 | $0.0005 | **$0.0009** |
| **minimax-m3** | OpenCode | $0.0005 | $0.0005 | **$0.0009** |
| **qwen3.5-plus** | OpenCode | $0.0007 | $0.0006 | **$0.0012** |
| **MiniMax-M2.7-highspeed** | mmx CLI | ¥0.0071 | ¥0.0067 | **~$0.0016** |
| **mimo-v2-omni** | OpenCode | $0.0017 | $0.0012 | **$0.0029** |
| **kimi-k2.7-code** | OpenCode | $0.0016 | $0.0016 | **$0.0030** |
| **mimo-v2.5-pro** | OpenCode | $0.0030 | $0.0014 | **$0.0040** |
| **gpt-5.5 / 5.4-mini** | Codex | $0 | $0 | **$20/mes** |

## Costes mensuales estimados

| Uso diario | Modelo | Queries/mes | Coste OpenCode | Coste mmx |
|:----------:|--------|:-----------:|:--------------:|:---------:|
| **10** | MiniMax-M2.1 | 300 | — | **~$0.24** |
| **50** | minimax-m2.5 | 1.500 | **$1.35** | — |
| **100** | MiniMax-M2.1 | 3.000 | — | **~$2.40** |
| **100** | minimax-m2.5 | 3.000 | **$2.70** | — |
| **500** | minimax-m2.5 | 15.000 | **$13.50** | — |
| **100** | kimi-k2.7-code | 3.000 | **$9.00** | — |
| **1.000** | minimax-m2.5 | 30.000 | **$27.00** | — |

## Stack 80/20 recomendado

| Prioridad | Modelo | Coste/query | Tiempo | Calidad |
|:---------:|--------|:----------:|:------:|:-------:|
| 🥇 Primario | MiniMax-M2.1 (mmx) | $0.0008 | **5s** | 100% |
| 🥈 Fallback | minimax-m2.5 (OpenCode) | $0.0009 | 11s | 83% |
| 🎯 Precisión | kimi-k2.7-code (OpenCode) | $0.0030 | 8s | 100% |

**Coste con 500 queries/mes (80% M2.1 + 20% M2.5):**
- MiniMax-M2.1: 400 queries × $0.0008 = **$0.32** (mmx Token Plan)
- minimax-m2.5: 100 queries × $0.0009 = **$0.09** (OpenCode)
- **Total: ~$0.41/mes**

## Modelos que NO funcionan con Samson VBP

| Modelo | Coste/query | Problema |
|--------|:----------:|----------|
| deepseek-v4-flash | $0.0003 | Devuelve contenido vacío |
| deepseek-v4-pro | $0.0035 | Devuelve contenido vacío |
| glm-5.2 | $0.0039 | Devuelve contenido vacío |
| glm-5.1 | $0.0039 | Devuelve contenido vacío |
| glm-5 | — | Devuelve contenido vacío |
| qwen3.7-max | — | Formato no soportado |
| kimi-k2.6 | — | No responde |
| hy3-preview | — | No responde |

## Notas

- Los precios de OpenCode Go son **créditos internos** que se descuentan del saldo de $60/mes incluido en la suscripción de $10/mes
- Los precios de MiniMax en ¥ se convierten a USD a tasa ~7.2 CNY/USD
- El Token Plan de MiniMax (~$50/mes) incluye una cantidad de tokens que se renueva cada mes. El coste marginal por query dentro del plan es menor que el pay-as-you-go
- ChatGPT Plus no tiene coste por token, pero hay rate limits que pueden afectar a alto volumen
