#!/usr/bin/env bash
# Monta o .zip da entrega da Fase 7 na pasta acima do repositório.
# Uso: ./gerar_zip_entrega.sh [nome_do_arquivo.zip]
set -euo pipefail
cd "$(dirname "$0")"
REPO=$(basename "$PWD")
NOME=${1:-sarahribeirodasilva_rm97747_4esoa_fase7_atividade.zip}
cd ..
rm -f "$NOME"
zip -rq "$NOME" "$REPO" \
  -x "$REPO/.venv/*" "$REPO/.git/*" "$REPO/.idea/*" "$REPO/.serena/*" "$REPO/.junie/*" \
     "*/__pycache__/*" "*.pyc" "*.DS_Store" "$REPO/logs/*" "$REPO/.pytest_cache/*" "$REPO/.ruff_cache/*" "$REPO/.coverage"
case "$NOME" in /*) CAMINHO=$NOME ;; *) CAMINHO=$(pwd)/$NOME ;; esac
echo "Gerado: $CAMINHO ($(du -h "$NOME" | cut -f1))"
unzip -l "$NOME" | tail -1
grep -q "cole aqui" "$REPO/docs/link_video_fase7.txt" && echo "ATENÇÃO: docs/link_video_fase7.txt ainda sem os links dos vídeos"
exit 0
