#!/usr/bin/env bash
# Uploads every program file in a folder to VirusTotal, waits for the verdicts and writes one table row per file.
# Usage: virustotal-scan.sh <folder with the release files> <rows file>      (needs VT_API_KEY, curl, jq)
# Documents (.pdf, .md) are skipped. Free VirusTotal keys allow 4 requests a minute, so this is slow on purpose.
set -u
DIR="$1"; ROWS="$2"; : > "$ROWS"
API="${VT_API:-https://www.virustotal.com/api/v3}"
POLL="${VT_POLL_SECONDS:-15}"; GAP="${VT_GAP_SECONDS:-16}"; RETRY_WAIT="${VT_RETRY_SECONDS:-60}"
upload_url() { curl -sS -H "x-apikey: $VT_API_KEY" "$API/files/upload_url" | jq -r '.data // empty'; }
cd "$DIR" || exit 1
for f in *; do
  [ -f "$f" ] || continue
  case "$f" in *.pdf|*.md) continue;; esac
  SHA=$(sha256sum "$f" | cut -d' ' -f1); SIZE=$(stat -c %s "$f")
  ID=""
  for try in 1 2 3; do
    URL="$API/files"; [ "$SIZE" -gt 30000000 ] && URL=$(upload_url)
    OUT=$(curl -sS -H "x-apikey: $VT_API_KEY" -F "file=@$f" "$URL" || true)
    ID=$(echo "$OUT" | jq -r '.data.id // empty' 2>/dev/null || true)
    [ -n "$ID" ] && break
    echo "Upload of $f failed (try $try): $(echo "$OUT" | head -c 300)"
    sleep "$RETRY_WAIT"
  done
  RES="not scanned"
  if [ -n "$ID" ]; then
    for i in $(seq 1 60); do
      sleep "$POLL"
      J=$(curl -sS -H "x-apikey: $VT_API_KEY" "$API/analyses/$ID" || true)
      if [ "$(echo "$J" | jq -r '.data.attributes.status // empty' 2>/dev/null)" = "completed" ]; then
        BAD=$(echo "$J" | jq -r '(.data.attributes.stats.malicious // 0) + (.data.attributes.stats.suspicious // 0)')
        TOT=$(echo "$J" | jq -r '.data.attributes.stats | to_entries | map(select(.key != "type-unsupported" and .key != "timeout") | .value) | add // 0')
        RES="$BAD / $TOT engines flag it"; break
      fi
    done
    [ "$RES" = "not scanned" ] && RES="scan still running"
  fi
  echo "$f: $RES"
  printf '| %s | [%s](https://www.virustotal.com/gui/file/%s) | `%s` |\n' "$f" "$RES" "$SHA" "$SHA" >> "$ROWS"
  sleep "$GAP"
done
