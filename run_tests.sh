#!/usr/bin/env bash
set -euo pipefail

PORT=${1:-5000}
BASE_URL="http://127.0.0.1:$PORT"

HAVE_JQ=0
if command -v jq >/dev/null 2>&1; then
  HAVE_JQ=1
fi

print_json () {
  local body="$1"
  if [ "$HAVE_JQ" -eq 1 ]; then
    # si ce n'est pas du JSON valide, on affiche brut
    echo "$body" | jq . 2>/dev/null || echo "$body"
  else
    echo "$body"
  fi
}

call () {
  # usage: call "TITRE" curl_args...
  local title="$1"; shift
  echo
  echo "▶ $title"
  echo "------------------------------------------"
  # on récupère le code HTTP proprement
  local resp
  resp=$(curl -sS -w "\nHTTP_STATUS:%{http_code}" "$@") || true
  local body="${resp%HTTP_STATUS:*}"
  local status="${resp##*HTTP_STATUS:}"
  print_json "$body"
  if [ "$status" != "200" ]; then
    echo "(HTTP $status)"
  fi
}

echo "🔍 Tests de l'API Atelier Algo (port $PORT)"
echo "------------------------------------------"

# # A: Recherche texte
# call "A - Recherche texte" \
#   -X POST "$BASE_URL/text/search" \
#   -H "Content-Type: application/json" \
#   -d '{
#         "query": "boss final",
#         "corpus": ["le boss final est au niveau 10", "tutoriel", "mode final secret"],
#         "top_k": 2
#       }'

# # B: Sélection
# call "B - Sélection par score" \
#   -X POST "$BASE_URL/selection" \
#   -H "Content-Type: application/json" \
#   -d '{
#         "items": [{"id":1,"value":10},{"id":2,"value":4},{"id":3,"value":7}],
#         "k": 2
#       }'

# C1: Pathfinding
call "C1 - Pathfinding (A*)" \
  -X POST "$BASE_URL/pathfinding" \
  -H "Content-Type: application/json" \
  -d '{"grid": [[1,1,1],[1,2,1],[1,1,1]], "start":[0,0], "goal":[2,2], "algorithm":"astar"}'

# C2: Cycle
call "C2 - Détection de cycle (DSU)" \
  -X POST "$BASE_URL/guilds/cycle" \
  -H "Content-Type: application/json" \
  -d '{"n":5,"edges":[[0,1],[1,2],[2,3],[3,4],[4,0]]}'

# D1: Reservoir
call "D1 - Reservoir Sampling" \
  -X POST "$BASE_URL/reservoir" \
  -H "Content-Type: application/json" \
  -d '{"stream":[1,2,3,4,5,6,7,8,9], "k":4, "seed":42}'

# D2: Count-Min Sketch
call "D2 - Count-Min Sketch" \
  -X POST "$BASE_URL/cms" \
  -H "Content-Type: application/json" \
  -d '{"depth":5,"width":128,"adds":[["pikachu",3],["bulbasaur",1],["pikachu",2]],"queries":["pikachu","mew"]}'

# E1: SHA256 texte
call "E1 - SHA256 texte" \
  -X POST "$BASE_URL/sha256" \
  -H "Content-Type: application/json" \
  -d '{"text":"bonjour","salt":"pepper"}'

# E2: Bloom add
call "E2 - Bloom add" \
  -X POST "$BASE_URL/bloom/add" \
  -H "Content-Type: application/json" \
  -d '{"items":["pikachu","bulbasaur"], "reset": true, "m": 4096, "k": 5}'

# E2: Bloom check
call "E2 - Bloom check" \
  -X POST "$BASE_URL/bloom/check" \
  -H "Content-Type: application/json" \
  -d '{"items":["pikachu","mew"]}'

echo
echo "✅ Tests terminés."
