"""The VBA module and the translation brief for the grid/vba-to-macro demo.

No imports from crafts or recipes: both of them import this file.
"""

from __future__ import annotations

import json

from .grid_macros import GRID_MACRO

VBA_SOURCE = """Sub FormatHeader()
    With Range("A1:C1")
        .Interior.Color = RGB(245, 158, 11)
        .Font.Bold = True
    End With
End Sub

Sub AddTotals()
    Dim lastRow As Long
    lastRow = Cells(Rows.Count, 1).End(xlUp).Row
    Cells(lastRow + 1, 1).Value = "Total"
    Cells(lastRow + 1, 2).Formula = "=SUM(B2:B" & lastRow & ")"
    Cells(lastRow + 1, 3).Formula = "=SUM(C2:C" & lastRow & ")"
End Sub

Sub HighlightBigMonths()
    Dim r As Long
    For r = 2 To 4
        If Cells(r, 3).Value > 300 Then Rows(r).Font.Bold = True
    Next r
End Sub

Sub ExportBackup()
    Shell "cmd /c copy report.xlsx \\\\server\\backup\\", vbHide
End Sub
"""

TABLE_NOTE = (
    "The macro runs on a table in A1:C4: header row 1 (Month, Visitors, Tickets) and "
    "data rows 2-4. Month is text, Visitors and Tickets are numbers, so colTypes must be "
    '["text","number","number"].'
)

PROCEDURES = ("FormatHeader", "AddTotals", "HighlightBigMonths", "ExportBackup")


def split_procedures() -> dict[str, str]:
    """name -> source text of each Sub in the module."""
    out: dict[str, str] = {}
    for block in VBA_SOURCE.split("End Sub"):
        block = block.strip()
        if block.startswith("Sub "):
            out[block[4 : block.index("(")]] = block + "\nEnd Sub"
    return out


def brief(name: str, retry: bool = False) -> str:
    """Prompt for ONE procedure: small answers stay valid JSON on a small local model."""
    example = json.dumps(GRID_MACRO, separators=(",", ":"))
    text = (
        "Translate this VBA procedure into one GridCraft typed macro. A macro is JSON with "
        "name, description, inputs (named ranges), output (anchor), steps and permissions. "
        "Steps are {type:command,id,params}, {type:repeat,over,of,max,body} and "
        "{type:if,cell,op,value,then}. Allowed command ids: home.fillColor, home.bold, cell.set. "
        "Ranges use tokens such as Table.row(1), Table.data.col(2), Row.cell(1,3), Output, "
        "Output.offset(0,1) and {{Table.data.col(2)}} inside formulas. Never hard-code A1 "
        "addresses. One valid macro, as the grammar reference: " + example + "\n"
        "If the procedure needs something a macro cannot do (running programs, files, "
        'network), answer {"macro":null,"reason":"..."}. Otherwise answer '
        '{"macro":{...},"reason":""}. Minified JSON, no code fence, no prose.\n\n'
        + TABLE_NOTE
        + "\n\nVBA:\n"
        + split_procedures()[name]
    )
    if retry:
        text = (
            "Your previous answer was not valid JSON. Answer with exactly one valid JSON object.\n"
            + text
        )
    return text
