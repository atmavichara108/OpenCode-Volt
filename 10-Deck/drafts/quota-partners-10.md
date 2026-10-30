---
type: Draft
title: 10 компаний — квоты/коллаборация для open-source разработчика агентов
ssot: false
timestamp: 2026-10-23
sources: живой поиск 10-23 (тарифы/программы); письмо в NVIDIA отправлено 10-23
---

# 10 адресатов — под каждый свой канал и свой «крючок»

Письмо — та же схема, что в NVIDIA (не просить исключений, предлагать
сотрудничество/открытость). Порядок — по вероятности ответа и ценности.

## 1. Mistral AI (La Plateforme) — Experiment plan free
- Канал: hello@mistral.ai / поддержка консоли. Free: $10/мес кредитов, без карты.
- Крючок: open-weight модели (Mistral Small/Large) + наш стек публичен —
  предложим публичный кейс «мультиагентный конвейер на Mistral» + бенчмарки.
- Риск: training на free-запросах (opt-out недоступен free) — проверить.

## 2. Google AI Studio (Gemini API) — standing free tier
- Канал: Google for Developers / OSS программы Google. 
- Крючок: Gemini + наш provenance-дизайн (у Google сильная DevRel для OSS).
- Плюс: Gmail/маршрутизация уже у нас — технически просто.

## 3. Groq — 1000 req/день, 200k ток/день free
- Канал: Groq Developer Program / OSS.
- Крючок: сверхбыстрый inference идеален для нашего multi-agent loop
  (много коротких вызовов между ведомствами). Предложить кейс + метрики.

## 4. Cohere — Trial key 1000 вызовов/мес
- Канал: Cohere for Builders / OSS-программа.
- Крючок: Cohere сильна в RAG/поиске — наш индекс 993 чанка + multi-agent
  provenance = кейс для их Embed/Rerank.

## 5. SambaNova Cloud — standing free tier
- Канал: SambaNova Free tier / OSS.
- Крючок: быстрые модели для агентского loop; предложить публичный
  benchmark-отчёт (мы уже делаем median/p95 по формату Лаб).

## 6. OpenRouter — 17 моделей бесплатно
- Канал: их OSS-программа (OpenRouter активно поддерживает OSS-клиентов).
- Крючок: наш multi-provider клиент — кейс «один агент — 10 провайдеров»,
  документация для их каталога.

## 7. Cerebras — trial (wafer-scale, сверхскорость)
- Канал: Cerebras for Startups/OSS.
- Крючок: для нашего multi-agent loop скорость inference = главный кайф.
  Предложить паблик-бенчмарк против Groq.

## 8. Together AI — $25-50 старт + $50K для стартапов
- Канал: Together Startup Program.
- Крючок: 100+ open-source моделей — наш стек прямо их профиль.
  Заявка в стартап-программу с метриками Корабля.

## 9. Cloudflare Workers AI — free tier
- Канал: Cloudflare for Builders / OSS.
- Крючок: KV/Workers/D1 рядом с моделью — вебхуки mail-hub + инференс
  в одном крае. Кейс «агентский хаб на edge».

## 10. Hugging Face Inference Providers — ежемесячные кредиты
- Канал: HF OSS-программа (мы — OSS с публичными репо).
- Крючок: HF любит кейсы «агенты поверх их Inference Providers» +
  публикация наших ADR в их хабе.

## Универсальный шаблон письма (адаптируется под каждого)
- Кто мы: 2 OSS-репо, экосистема агентов с provenance (ссылка).
- Что уже: 610 писем почты, 25 canvas-карт, линт 7/7, 136 цитат provenance.
- Что просим: не исключения — «правильный канал» (программа/квота/кредиты)
  для OSS-проекта нашего профиля.
- Что даём взамен: публичный кейс/бенчмарк/документацию с упоминанием
  компании, ADR-отчёты, метрики (median/p95) — честные, не маркетинг.
