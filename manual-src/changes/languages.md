# Seven more UI languages

Callum asked for more languages (2026-11-14, "Add all of them" to the coordinator's list). The UI now speaks English,
Spanish, Portuguese (Brazil), German, French, Italian, Dutch, Simplified Chinese, Japanese and Korean.

- TR rows now hold nine strings, in the order of LIX: es, pt-BR, de, fr, zh-CN, ja, ko, it, nl. A row with fewer
  shows the English for the missing languages, so a parallel PR that adds a two-string row still works.
- LANGS and the Info > Preferences Language picker list all ten, each named in its own language. A first visit picks
  the browser language (zh-* goes to zh-CN, pt-* to pt-BR).
- Industry terms: German Panel / Wand / Stromkreis / Verteiler / Traverse / Kettenzug (du); French dalle / mur /
  distrib / disjoncteur / pont / palan (vous); Chinese 箱体 / 屏体 / 网口 / 回路 / 配电箱 / 桁架 / 电动葫芦; Japanese
  パネル / ウォール / 分電盤 / 回路 / トラス / ホイスト; Korean 캐비닛 / 월 / 분전반 / 회로 / 트러스 / 호이스트;
  Italian pannello / ledwall / quadro / americana / paranco (tu); Dutch panel / ledwall / groep / verdeler / takel (je).
- Fonts: html:lang(zh-CN / ja / ko) adds the system CJK fonts (PingFang, Microsoft YaHei, Hiragino, Yu Gothic, Apple SD
  Gothic Neo, Malgun Gothic, Noto CJK) after the UI font, so Latin text keeps JetBrains Mono.
- PDF and binder exports stay in English: they use the built-in Helvetica, which has no CJK glyphs.
- Plural placeholders such as tile{1} are dropped where the language has no plural "s".
- Test: tests/i18n_test.py (table completeness and placeholders, picker, every language switch, CJK fonts, binder PDF
  in Japanese). Not yet checked by Callum or a native speaker: the translations are first drafts.
