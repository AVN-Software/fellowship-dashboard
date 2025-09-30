
```
fellowship-dashboard
├─ .devcontainer
│  └─ devcontainer.json
├─ .streamlit
├─ app.py
├─ charts.py
├─ components
│  ├─ filters.py
│  ├─ tab_bar.py
│  └─ __init__.py
├─ config
│  ├─ config.json
│  ├─ config.py
│  └─ __init__.py
├─ data
│  ├─ observations.json
│  ├─ schema
│  │  └─ academic-results.json
│  ├─ term-comparison.json
│  └─ wellbeing.json
├─ pages
│  ├─ 1_Classroom_Observations
│  │  ├─ analysis
│  │  │  ├─ movement.py
│  │  │  ├─ summaries.py
│  │  │  ├─ tier_mix_analysis.py
│  │  │  ├─ trends.py
│  │  │  └─ __init__.py
│  │  ├─ charts
│  │  │  ├─ 1_classroom_observations_chart.py
│  │  │  ├─ comparative.py
│  │  │  ├─ create_tier_distribution_chart.py
│  │  │  ├─ performance.py
│  │  │  ├─ strategic.py
│  │  │  └─ tier_mix_charts.py
│  │  ├─ enhanced_tier_analysis
│  │  │  ├─ charts
│  │  │  │  └─ __init__.py
│  │  │  ├─ config.py
│  │  │  ├─ integration.py
│  │  │  ├─ page.py
│  │  │  ├─ tables
│  │  │  │  └─ __init__.py
│  │  │  └─ __init__.py
│  │  ├─ page.py
│  │  ├─ sections.py
│  │  ├─ tables
│  │  │  ├─ 1_classroom_observations_table.py
│  │  │  └─ tier_mix_tables.py
│  │  ├─ tier_progression.py
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
│  │  │  └─ data_explorer.py
│  │  └─ __init__.py
│  ├─ 3_Teacher_Wellbeing.py
│  └─ 4_Scale.py
├─ README.md
├─ requirements.txt
└─ utils
   ├─ data
   │  ├─ loader.py
   │  ├─ schema_loader.py
   │  └─ __init__.py
   ├─ database
   │  ├─ connection.py
   │  ├─ crud_utils.py
   │  └─ __init__.py
   ├─ supabase
   │  ├─ database_manager.py
   │  ├─ supabase (14).ts
   │  ├─ supabase_connection.py
   │  ├─ test_connection.py
   │  └─ __init__.py
   ├─ supabase.py
   └─ __init__.py

```