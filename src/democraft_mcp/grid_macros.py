"""The typed GridCraft macro the demos share (no imports, so crafts and recipes can both use it)."""

from __future__ import annotations

GRID_MACRO = {
    "name": "Summarise",
    "description": "Amber header, a SUM total row under the table, bold rows whose "
    "third column is above 300",
    "inputs": [
        {
            "name": "Table",
            "kind": "range",
            "header": True,
            "rows": [1, 0],
            "cols": [3, 3],
            "colTypes": ["text", "number", "number"],
            "nonEmpty": True,
        }
    ],
    "output": {"anchor": "Table.below(1).cell(1,1)", "onConflict": "fail"},
    "steps": [
        {
            "type": "command",
            "id": "home.fillColor",
            "params": {"range": "Table.row(1)", "color": "#F59E0B"},
        },
        {"type": "command", "id": "cell.set", "params": {"cell": "Output", "input": "Total"}},
        {
            "type": "command",
            "id": "cell.set",
            "params": {"cell": "Output.offset(0,1)", "input": "=SUM({{Table.data.col(2)}})"},
        },
        {
            "type": "command",
            "id": "cell.set",
            "params": {"cell": "Output.offset(0,2)", "input": "=SUM({{Table.data.col(3)}})"},
        },
        {
            "type": "repeat",
            "over": "Table.data",
            "of": "rows",
            "max": 1000,
            "body": [
                {
                    "type": "if",
                    "cell": "Row.cell(1,3)",
                    "op": "gt",
                    "value": 300,
                    "then": [{"type": "command", "id": "home.bold", "params": {"range": "Row"}}],
                },
            ],
        },
    ],
    "permissions": [],
}
