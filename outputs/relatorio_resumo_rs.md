# Resumo – Municípios afetados por Linhas de Transmissão no RS

Atualizado em: 2025-10-26

Este resumo apresenta contagens e links de acesso rápido aos mapas interativos do Rio Grande do Sul (RS), com municípios afetados separados por voltagem.

## Navegação rápida

- Dashboard (entrada principal): https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/dashboard.html
- Mapas Interativos (todas as camadas): https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/
- Relatório Acessível: https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/relatorio_acessivel.html
- Relatório Técnico: https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/relatorio_tecnico.html

## Contagem por voltagem (municípios afetados)

- 230 kV: 226 municípios
- 525 kV: 154 municípios
- Outros: 500 kV (1 município), 132 kV (1 município)

Fonte: RS/Linha_trans_RS.gpkg (linhas) + RS/RS_Municipios_2024.zip (municípios). As voltagens por município foram inferidas via interseção espacial e registradas em `RS/Municipios_afetas_linhas_por_voltagem.csv`.

## Mapas interativos

- RS – 230 kV: https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/mapa_230kV_RS.html
- RS – 525 kV: https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/mapa_525kV_RS.html

Observações:
- Os mapas exibem municípios afetados por voltagem (camada principal), além de um fundo com municípios não afetados para contexto visual.
- As geometrias foram simplificadas para melhorar o desempenho em navegação Web.
- A faixa de servidão (buffer) é exibida para referência de proximidade.

---

Elaborado automaticamente a partir do repositório: caetanoronan/linhas-transmissao-foz-iguacu.