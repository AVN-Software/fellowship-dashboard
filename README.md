# Fellowship Dashboard

Streamlit-based multipage dashboard for:
- Classroom Observations
- Academic Results
- Teacher Wellbeing

## Quickstart
```bash
cd fellowship-dashboard
pip install -r requirements.txt
streamlit run app.py
```

```
fellowship-dashboard
├─ app.py
├─ data
│  ├─ observations.json
│  ├─ term-comparison.json
│  └─ wellbeing.json
├─ pages
│  ├─ 1_Classroom_Observations
│  │  ├─ charts
│  │  │  └─ 1_classroom_observations_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 1_classroom_observations_table.py
│  │  └─ __init__.py
│  ├─ 1_Classroom_Observations.py
│  ├─ 2_Academic_Results
│  │  ├─ charts
│  │  │  └─ 2_academic_results_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 2_academic_results_table.py
│  │  └─ __init__.py
│  ├─ 2_Academic_Results.py
│  ├─ 3_Teacher_Wellbeing
│  │  ├─ charts
│  │  │  └─ 3_teacher_wellbeing_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 3_teacher_wellbeing_table.py
│  │  └─ __init__.py
│  └─ 3_Teacher_Wellbeing.py
├─ README.md
├─ requirements.txt
├─ secrets.toml
└─ utils
   ├─ data
   │  ├─ loader.py
   │  ├─ schema_loader.py
   │  └─ __init__.py
   ├─ supabase
   └─ supabase.py

```
```
fellowship-dashboard
├─ app.py
├─ data
│  ├─ observations.json
│  ├─ schema
│  │  └─ academic-results.json
│  ├─ term-comparison.json
│  └─ wellbeing.json
├─ enhanced_tier_analysis
│  ├─ analysis
│  │  ├─ movement.py
│  │  ├─ summaries.py
│  │  ├─ tier_mix_analysis.py
│  │  ├─ trends.py
│  │  └─ __init__.py
│  ├─ charts
│  │  ├─ comparative.py
│  │  ├─ create_tier_distribution_chart.py
│  │  ├─ performance.py
│  │  ├─ strategic.py
│  │  ├─ tier_mix_charts.py
│  │  └─ __init__.py
│  ├─ config.py
│  ├─ integration.py
│  ├─ page.py
│  ├─ sections
│  │  ├─ comparative_section.py
│  │  ├─ performance_section.py
│  │  ├─ strategic_section.py
│  │  └─ tier_mix_section.py
│  ├─ tables
│  │  ├─ tier_mix_tables.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ pages
│  ├─ 1_Classroom_Observations
│  │  ├─ charts
│  │  │  └─ 1_classroom_observations_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 1_classroom_observations_table.py
│  │  └─ __init__.py
│  ├─ 1_Classroom_Observations.py
│  ├─ 2_Academic_Results
│  │  ├─ charts
│  │  │  └─ 2_academic_results_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 2_academic_results_table.py
│  │  └─ __init__.py
│  ├─ 2_Academic_Results.py
│  ├─ 3_Teacher_Wellbeing
│  │  ├─ charts
│  │  │  └─ 3_teacher_wellbeing_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 3_teacher_wellbeing_table.py
│  │  └─ __init__.py
│  ├─ 3_Teacher_Wellbeing.py
│  └─ 4_Scale.py
├─ README.md
├─ requirements.txt
├─ secrets.toml
└─ utils
   ├─ data
   │  ├─ loader.py
   │  ├─ schema_loader.py
   │  └─ __init__.py
   ├─ supabase
   └─ supabase.py

```
```
fellowship-dashboard
├─ app.py
├─ data
│  ├─ exports
│  │  ├─ columns.json
│  │  ├─ domain_performance.json
│  │  ├─ fellow_summary.json
│  │  ├─ lesson_observations.json
│  │  ├─ lesson_observations.json.backup_20250912_065140
│  │  ├─ lesson_observations.json.backup_20250912_070820
│  │  ├─ observation_scores.json
│  │  ├─ pre-norm.json
│  │  ├─ tables.json
│  │  ├─ table_schemas.json
│  │  ├─ table_schemas.json.bak
│  │  └─ term_progression.json
│  ├─ observations.json
│  ├─ schema
│  │  └─ academic-results.json
│  ├─ term-comparison.json
│  └─ wellbeing.json
├─ enhanced_tier_analysis
│  ├─ analysis
│  │  ├─ movement.py
│  │  ├─ summaries.py
│  │  ├─ tier_mix_analysis.py
│  │  ├─ trends.py
│  │  └─ __init__.py
│  ├─ charts
│  │  ├─ comparative.py
│  │  ├─ create_tier_distribution_chart.py
│  │  ├─ performance.py
│  │  ├─ strategic.py
│  │  ├─ tier_mix_charts.py
│  │  └─ __init__.py
│  ├─ config.py
│  ├─ integration.py
│  ├─ page.py
│  ├─ sections
│  │  ├─ comparative_section.py
│  │  ├─ performance_section.py
│  │  ├─ strategic_section.py
│  │  └─ tier_mix_section.py
│  ├─ tables
│  │  ├─ tier_mix_tables.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ old
│  ├─ analysis
│  │  ├─ hits_analyzer.py
│  │  ├─ questions.py
│  │  └─ __init__.py
│  ├─ config
│  │  ├─ config.json
│  │  ├─ config.py
│  │  └─ __init__.py
│  ├─ convert.py
│  ├─ data
│  │  └─ exports
│  │     ├─ columns.json
│  │     ├─ domain_performance.json
│  │     ├─ fellow_summary.json
│  │     ├─ lesson_observations.json
│  │     ├─ lesson_observations.json.backup_20250912_065140
│  │     ├─ lesson_observations.json.backup_20250912_070820
│  │     ├─ observation_scores.json
│  │     ├─ pre-norm.json
│  │     ├─ tables.json
│  │     ├─ table_schemas.json
│  │     ├─ table_schemas.json.bak
│  │     └─ term_progression.json
│  ├─ enhanced_tier_analysis
│  │  ├─ analysis
│  │  │  ├─ movement.py
│  │  │  ├─ summaries.py
│  │  │  ├─ tier_mix_analysis.py
│  │  │  ├─ trends.py
│  │  │  └─ __init__.py
│  │  ├─ charts
│  │  │  ├─ comparative.py
│  │  │  ├─ create_tier_distribution_chart.py
│  │  │  ├─ performance.py
│  │  │  ├─ strategic.py
│  │  │  ├─ tier_mix_charts.py
│  │  │  └─ __init__.py
│  │  ├─ config.py
│  │  ├─ integration.py
│  │  ├─ page.py
│  │  ├─ sections
│  │  │  ├─ comparative_section.py
│  │  │  ├─ performance_section.py
│  │  │  ├─ strategic_section.py
│  │  │  └─ tier_mix_section.py
│  │  ├─ tables
│  │  │  ├─ tier_mix_tables.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ narrative_feedback.json
│  ├─ narrative_feedback_with_counts.json
│  ├─ narritive_feedback
│  │  ├─ json_io.py
│  │  ├─ page.py
│  │  ├─ utils
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ notebooks
│  ├─ reports
│  ├─ requirements.txt
│  ├─ run_dashboard.py
│  ├─ src
│  │  ├─ components
│  │  │  ├─ render_normalizer.py
│  │  │  └─ __init__.py
│  │  ├─ database
│  │  │  ├─ connection.py
│  │  │  ├─ crud_utils.py
│  │  │  ├─ database_manager.py
│  │  │  ├─ supabase_connection.py
│  │  │  └─ __init__.py
│  │  ├─ services
│  │  │  ├─ column_registry.py
│  │  │  ├─ column_schema.py
│  │  │  ├─ loaders.py
│  │  │  ├─ schema_manager.py
│  │  │  ├─ schema_validator.py
│  │  │  ├─ score_normalizer.py
│  │  │  ├─ table_schema.py
│  │  │  └─ __init__.py
│  │  ├─ ui
│  │  │  ├─ main.py
│  │  │  └─ pages
│  │  │     ├─ coach_effectiveness.py
│  │  │     ├─ context_analysis.py
│  │  │     ├─ dashboard.py
│  │  │     ├─ data_manager.py
│  │  │     ├─ domain_analysis.py
│  │  │     ├─ enhanced_tier_progression.py
│  │  │     ├─ hits_normalizer_config.py
│  │  │     ├─ overview.py
│  │  │     ├─ raw_data.py
│  │  │     ├─ risk_assessment.py
│  │  │     ├─ schema_admin.py
│  │  │     ├─ tier_progression.py
│  │  │     └─ __init__.py
│  │  └─ __init__.py
│  ├─ tests
│  │  ├─ test_analyzer.py
│  │  ├─ test_connection.py
│  │  └─ __init__.py
│  └─ visualization
│     ├─ charts.py
│     ├─ dashboard.py
│     └─ __init__.py
├─ pages
│  ├─ 1_Classroom_Observations
│  │  ├─ charts
│  │  │  └─ 1_classroom_observations_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 1_classroom_observations_table.py
│  │  └─ __init__.py
│  ├─ 1_Classroom_Observations.py
│  ├─ 2_Academic_Results
│  │  ├─ charts
│  │  │  └─ 2_academic_results_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 2_academic_results_table.py
│  │  └─ __init__.py
│  ├─ 2_Academic_Results.py
│  ├─ 3_Teacher_Wellbeing
│  │  ├─ charts
│  │  │  └─ 3_teacher_wellbeing_chart.py
│  │  ├─ page.py
│  │  ├─ tables
│  │  │  └─ 3_teacher_wellbeing_table.py
│  │  └─ __init__.py
│  ├─ 3_Teacher_Wellbeing.py
│  └─ 4_Scale.py
├─ README.md
├─ requirements.txt
├─ secrets.toml
└─ utils
   ├─ data
   │  ├─ loader.py
   │  ├─ schema_loader.py
   │  └─ __init__.py
   ├─ supabase
   └─ supabase.py

```