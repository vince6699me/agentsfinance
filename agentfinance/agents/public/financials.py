#!/usr/bin/env python3
"""
Financials Agent (Agent 04)

Provides financial statement data including income statement, balance sheet, cash flow, and health metrics.
"""

import argparse
import json
import sys
from typing import Any, Dict


def handle_income(args: argparse.Namespace) -> Dict[str, Any]:
    """Get income statement data."""
    return {
        "status": "success",
        "command": "income",
        "ticker": args.ticker,
        "period": args.period,
        "data": {
            "revenue": 0,
            "cost_of_goods_sold": 0,
            "gross_profit": 0,
            "operating_expenses": 0,
            "operating_income": 0,
            "net_income": 0,
            "earnings_per_share": 0.0,
        },
        "message": "Income statement not yet implemented",
    }


def handle_balance(args: argparse.Namespace) -> Dict[str, Any]:
    """Get balance sheet data."""
    return {
        "status": "success",
        "command": "balance",
        "ticker": args.ticker,
        "period": args.period,
        "data": {
            "total_assets": 0,
            "total_liabilities": 0,
            "total_equity": 0,
            "current_assets": 0,
            "current_liabilities": 0,
            "cash": 0,
            "debt": 0,
        },
        "message": "Balance sheet not yet implemented",
    }


def handle_cashflow(args: argparse.Namespace) -> Dict[str, Any]:
    """Get cash flow statement data."""
    return {
        "status": "success",
        "command": "cashflow",
        "ticker": args.ticker,
        "period": args.period,
        "data": {
            "operating_cash_flow": 0,
            "investing_cash_flow": 0,
            "financing_cash_flow": 0,
            "free_cash_flow": 0,
            "capex": 0,
        },
        "message": "Cash flow statement not yet implemented",
    }


def handle_health(args: argparse.Namespace) -> Dict[str, Any]:
    """Calculate financial health metrics."""
    return {
        "status": "success",
        "command": "health",
        "ticker": args.ticker,
        "metrics": {
            "current_ratio": 0.0,
            "debt_to_equity": 0.0,
            "profit_margin": 0.0,
            "roe": 0.0,
            "roa": 0.0,
            "interest_coverage": 0.0,
        },
        "message": "Financial health metrics not yet implemented",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Financials Agent - Financial statement data and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    income_parser = subparsers.add_parser("income", help="Get income statement")
    income_parser.add_argument("ticker", help="Stock ticker symbol")
    income_parser.add_argument("period", default="TTM", help="Reporting period")

    balance_parser = subparsers.add_parser("balance", help="Get balance sheet")
    balance_parser.add_argument("ticker", help="Stock ticker symbol")
    balance_parser.add_argument("period", default="TTM", help="Reporting period")

    cashflow_parser = subparsers.add_parser("cashflow", help="Get cash flow statement")
    cashflow_parser.add_argument("ticker", help="Stock ticker symbol")
    cashflow_parser.add_argument("period", default="TTM", help="Reporting period")

    health_parser = subparsers.add_parser(
        "health", help="Calculate financial health metrics"
    )
    health_parser.add_argument("ticker", help="Stock ticker symbol")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "income": handle_income,
        "balance": handle_balance,
        "cashflow": handle_cashflow,
        "health": handle_health,
    }

    result = handlers[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
