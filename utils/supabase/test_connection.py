# utils/supabase/test_connection.py
from __future__ import annotations
import os
import sys
import json
from typing import Optional

def _load_secrets() -> tuple[Optional[str], Optional[str]]:
    """
    Try to load Supabase credentials from Streamlit secrets.
    Falls back to environment variables if Streamlit isn't available.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    try:
        import streamlit as st  # noqa
        try:
            url = st.secrets["supabase"]["url"] or url  # type: ignore[attr-defined]
            key = st.secrets["supabase"]["anon_key"] or key  # type: ignore[attr-defined]
        except Exception:
            pass
    except Exception:
        # streamlit not installed or not running in Streamlit context → ignore
        pass

    return url, key

def main() -> int:
    url, key = _load_secrets()
    if not url or not key:
        print(
            "❌ Missing Supabase credentials.\n"
            "Provide either:\n"
            "  1) .streamlit/secrets.toml with:\n"
            "     [supabase]\n"
            "     url = \"https://<PROJECT>.supabase.co\"\n"
            "     anon_key = \"<YOUR_ANON_KEY>\"\n"
            "  2) or environment variables SUPABASE_URL / SUPABASE_ANON_KEY\n",
            file=sys.stderr,
        )
        return 2

    try:
        from supabase import create_client
    except Exception as e:
        print(f"❌ supabase package not installed: {e}\nTry: pip install supabase", file=sys.stderr)
        return 3

    print("🔌 Creating Supabase client...")
    try:
        client = create_client(url, key)
    except Exception as e:
        print(f"❌ Failed to create client: {e}", file=sys.stderr)
        return 4

    try:
        # Tables to probe
        candidates = [
            "observations",
            "domain_scores",
            "teacher_wellbeing",
            "report_academic_results",
            "v_observation_full",
        ]

        ok_table = None
        for t in candidates:
            try:
                resp = client.table(t).select("*").limit(1).execute()
                if getattr(resp, "data", None) is not None:
                    ok_table = t
                    break
            except Exception:
                continue

        print("✅ Client created.")
        print(f"📡 URL: {url}")
        if ok_table:
            print(f"🧪 Test table: {ok_table} (fetched up to 1 row successfully)")
        else:
            print("⚠️ Could not read any of the candidate tables. "
                  "This may be fine if names differ or RLS blocks anon.")

        # Row counts summary
        summary = {}
        for t in candidates:
            try:
                resp = client.table(t).select("*").execute()
                cnt = len(resp.data) if getattr(resp, "data", None) is not None else None
                summary[t] = cnt
            except Exception:
                summary[t] = None

        print("📊 Quick table visibility summary (row counts or None if blocked/missing):")
        print(json.dumps(summary, indent=2))

        if any(v is not None for v in summary.values()):
            print("✅ At least one table returned rows.")
        else:
            print("⚠️ No rows returned. Check table names or RLS policies.")

        return 0

    except Exception as e:
        print(f"❌ Test query failed: {e}", file=sys.stderr)
        return 5

if __name__ == "__main__":
    raise SystemExit(main())
