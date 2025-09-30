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