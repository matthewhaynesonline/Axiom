#!/usr/bin/env bash
cd "$(dirname "$0")"

cp pipeline/export/judgement_categories_mapping.json data_explorer/src/pipeline_export/judgement_categories_mapping.json
cp pipeline/data/definitions.json data_explorer/src/pipeline_export/definitions.json

cp pipeline/export/enabled_models.csv data_explorer/public/enabled_models.csv
cp pipeline/export/axiom_term_sentiment.arrow data_explorer/public/axiom_term_sentiment.arrow
cp pipeline/export/value_systems/value_system_rankings.arrow data_explorer/public/value_system_rankings.arrow