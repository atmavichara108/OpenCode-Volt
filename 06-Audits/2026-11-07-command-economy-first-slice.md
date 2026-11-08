---
type: Audit
title: "Первый срез экономии команд (ступень 0-1)"
timestamp: 2026-11-07
---

# Первый срез экономии команд (ступень 0-1, канон Р-115)

- Журнал: 20345 команд, 33 сессий (наполнено из следов сессий).
- Топ нормализованных форм — верх экономики без модели:

ЖУРНАЛ: 20345 команд, 18599 форм
x144 rc[0:144]  LAST=<N> DEADLINE=$(( $(date +%s) + <N> )) while [ $(date +%s) -lt $DEADLINE ]; do NEW=$(python3 <PATH> --topic 33 --since-id $LAS
      пример: LAST=142
DEADLINE=$(( $(date +%s) + 3600 ))
while [ $(date +%s) -lt $DEADLINE ]; do
  NEW=$(python3 /home/rudra/dotfiles/scripts/.
x105 rc[0:105]  <PATH> inbox <SID>
      пример: ~/.local/bin/ship-mail.sh inbox ses_ea02cc0d8ffeFXUsAX9UeQWs2D
x91  rc[0:91]  bash <PATH> inbox <SID> 2>&1
      пример: bash ~/.local/bin/ship-mail.sh inbox ses_ecaf0b603ffezygMvp7QG3Iq8h 2>&1
x70  rc[0:70]  <PATH> inbox <SID>; echo "---status---"; <PATH> status <SID>
      пример: ~/.local/bin/ship-mail.sh inbox ses_eQRHoixARq3RNJnKLFTS4IW; echo "---status---"; ~/.local/bin/ship-mail.sh status ses_eQRHoixARq3
x63  rc[0:63]  cd <PATH> bash tools/ship-mail/ship-mail.sh inbox <SID>
      пример: cd /home/rudra/dotfiles
bash tools/ship-mail/ship-mail.sh inbox ses_ece7b76c8ffeOkYZqZe38QbTVx
x52  rc[0:52]  cd <PATH> && ./scripts/ship-mail.sh inbox <SID> && python3 -c " import glob for f in sorted(glob.glob('<PATH><SID>/*.md')): if 're
      пример: cd /home/rudra/Projects/dv-hub && ./scripts/ship-mail.sh inbox ses_eceb23a71ffeJO9QnFou8VngZC && python3 -c "
import glob
for f in
x47  rc[0:47]  cat "<PATH><SID>/"*<REF>*.md
      пример: cat "/home/rudra/.local/share/ship-mail/inbox/ses_eQRHoixARq3RNJnKLFTS4IW/"*36031883cc66*.md
x42  rc[0:42]  cd <PATH> bash tools/ship-mail/ship-mail.sh ack <SID> all
      пример: cd /home/rudra/dotfiles
bash tools/ship-mail/ship-mail.sh ack ses_ece7b76c8ffeOkYZqZe38QbTVx all
x39  rc[0:39]  bash <PATH> ack <SID> all 2>&1
      пример: bash ~/.local/bin/ship-mail.sh ack ses_e9884e4aeffe7okjn4f7RtavmG all 2>&1
x36  rc[0:36]  cd <PATH> && ./scripts/ship-mail.sh inbox <SID> && python3 -c " import glob for f in sorted(glob.glob('<PATH><SID>/*.md')): if 're
      пример: cd /home/rudra/Projects/dv-hub && ./scripts/ship-mail.sh inbox ses_eceb23a71ffeJO9QnFou8VngZC && python3 -c "
import glob
for f in

## Что видно уже сейчас

1. Одна операция «прочесть ящик» повторена ~400 раз в десяти текстовых формах — это и есть переплата, о которой говорил владелец.
2. Верхняя форма — цикл ожидания ответа (x144): кандидат в шаблоны с параметрами темы и времени.
3. Следующие формы — служебные (статус, снятие писем, чтение письма по имени).
4. Все формы верхней десятки безопасны (чтение/почта) — допустимы к шаблонам на ступени 1.
5. Форм много (18599 на 20345 команд): тексты пишутся заново каждый раз — это подтверждение идеи, не опровержение.
