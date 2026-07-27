"""Shared CSS injected once at app startup for a more polished demo UI."""

CUSTOM_CSS = """
<style>
.main-header {
    background: linear-gradient(135deg, #1f2b6c 0%, #2f6fed 100%);
    padding: 1.6rem 1.8rem;
    border-radius: 14px;
    color: white;
    margin-bottom: 1.4rem;
}
.main-header h1 {
    margin: 0;
    font-size: 1.6rem;
}
.main-header p {
    margin: 0.2rem 0 0 0;
    opacity: 0.85;
    font-size: 0.95rem;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #ececec;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi-value {
    font-size: 1.7rem;
    font-weight: 700;
    color: #1f2b6c;
}
.kpi-label {
    font-size: 0.85rem;
    color: #666;
}
.step-chip {
    display: inline-block;
    background: #eaf3ea;
    color: #1e6b33;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    margin: 0.15rem;
    font-size: 0.85rem;
}
.warning-banner {
    background: #fff4e5;
    border-left: 4px solid #ff9800;
    padding: 0.7rem 1rem;
    border-radius: 6px;
    color: #7a4a00;
}
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 1.2rem;
    margin-bottom: 0.4rem;
    color: #1f2b6c;
}
</style>
"""
