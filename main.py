from db.db_connect import init_db
from collectors.stock_collector import fetch_and_store_stocks
from collectors.realestate_collector import fetch_and_store_realestate
from analysis.stock_analysis import analyze_stocks
from analysis.realestate_analysis import analyze_realestate
from db.queries import run_all_queries
from visualize.plots import (
    plot_stock_trends,
    plot_realestate_comparison,
    plot_volatility
)

def run_pipeline():
    print("\n========================================")
    print("   Market Trend Analyzer — Full Run")
    print("========================================\n")

    print("[1/6] Initializing database...")
    init_db()

    print("[2/6] Collecting stock data...")
    fetch_and_store_stocks()

    print("[3/6] Collecting real estate data...")
    fetch_and_store_realestate()

    print("[4/6] Analyzing stock trends...")
    analyze_stocks()

    print("[5/6] Analyzing real estate trends...")
    analyze_realestate()

    print("[6/6] Running SQL queries...")
    run_all_queries()

    print("\nGenerating charts...")
    plot_stock_trends()
    plot_realestate_comparison()
    plot_volatility()

    print("\nPipeline complete! Charts saved to data/")

if __name__ == "__main__":
    run_pipeline()
