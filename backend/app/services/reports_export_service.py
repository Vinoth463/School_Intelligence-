
from io import BytesIO
from datetime import date, datetime
from typing import Any
from html import escape
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ==========================================================
# COMMON HELPERS
# ==========================================================

def _display_name(value: str) -> str:
    return str(value).replace("_", " ").replace(".", " ").title()


def _safe_sheet_name(name: str, existing: set[str]) -> str:
    name = re.sub(r'[\\/*?:\[\]]', "_", name)
    name = name[:31] or "Report"

    candidate = name
    counter = 1

    while candidate.lower() in existing:
        suffix = f"_{counter}"
        candidate = name[:31 - len(suffix)] + suffix
        counter += 1

    existing.add(candidate.lower())
    return candidate


def _is_nested(value: Any) -> bool:
    return isinstance(value, (dict, list, tuple))


def _scalar_value(value: Any) -> Any:
    if value is None:
        return ""

    if isinstance(value, (dict, list, tuple)):
        return ""

    return value


def _format_number(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 2)
    return value


def _get_scalar_fields(record: dict) -> dict:
    return {
        key: value
        for key, value in record.items()
        if not _is_nested(value)
    }


def _get_nested_fields(record: dict) -> dict:
    return {
        key: value
        for key, value in record.items()
        if _is_nested(value) and value
    }


# ==========================================================
# EXCEL EXPORT
# ==========================================================

def _style_excel_sheet(sheet) -> None:
    header_fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78",
    )

    header_font = Font(
        bold=True,
        color="FFFFFF",
        size=10,
    )

    thin_border = Border(
        bottom=Side(style="thin", color="D9E2F3")
    )

    for cell in sheet[1]:
        cell.font = Font(
            bold=True,
            size=15,
            color="1F4E78",
        )

    if sheet.max_row >= 3:
        for cell in sheet[3]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        for row in sheet.iter_rows(min_row=4):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

                if isinstance(cell.value, float):
                    cell.number_format = "0.00"

                if (
                    isinstance(cell.value, (int, float))
                    and "percentage" in str(
                        sheet.cell(row=3, column=cell.column).value
                    ).lower()
                ):
                    cell.number_format = '0.00"%"'

    sheet.freeze_panes = "A4"

    if sheet.max_row >= 3 and sheet.max_column >= 1:
        sheet.auto_filter.ref = (
            f"A3:{get_column_letter(sheet.max_column)}{sheet.max_row}"
        )

    for column_cells in sheet.columns:
        column_letter = get_column_letter(
            column_cells[0].column
        )

        max_length = 0

        for cell in column_cells:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value)),
                )

        sheet.column_dimensions[column_letter].width = min(
            max(max_length + 3, 14),
            35,
        )

    sheet.sheet_view.showGridLines = False


def _write_excel_metrics(
    workbook: Workbook,
    section_name: str,
    data: dict,
    existing_names: set[str],
) -> None:
    scalar_fields = _get_scalar_fields(data)

    if not scalar_fields:
        return

    sheet_name = _safe_sheet_name(
        section_name,
        existing_names,
    )

    sheet = workbook.create_sheet(sheet_name)

    sheet.append([_display_name(section_name)])
    sheet.append([])

    sheet.append(["Metric", "Value"])

    for key, value in scalar_fields.items():
        sheet.append([
            _display_name(key),
            _format_number(_scalar_value(value)),
        ])

    _style_excel_sheet(sheet)


def _write_excel_records(
    workbook: Workbook,
    section_name: str,
    records: list,
    existing_names: set[str],
    parent_context: dict | None = None,
) -> None:
    if not records:
        return

    if not all(isinstance(item, dict) for item in records):
        records = [{"value": item} for item in records]

    parent_context = parent_context or {}

    headers = list(parent_context.keys())

    for record in records:
        for key in _get_scalar_fields(record):
            if key not in headers:
                headers.append(key)

    if not headers:
        return

    sheet_name = _safe_sheet_name(
        section_name,
        existing_names,
    )

    sheet = workbook.create_sheet(sheet_name)

    sheet.append([_display_name(section_name)])
    sheet.append([])

    sheet.append([
        _display_name(header)
        for header in headers
    ])

    for record in records:
        row = []

        for header in headers:
            if header in parent_context:
                value = parent_context[header]
            else:
                value = record.get(header)

            row.append(_format_number(_scalar_value(value)))

        sheet.append(row)

    _style_excel_sheet(sheet)

    # Export nested lists and dictionaries into separate sheets.
    for index, record in enumerate(records, start=1):
        context = dict(parent_context)
        context.update(_get_scalar_fields(record))

        for key, nested_data in _get_nested_fields(record).items():
            nested_name = (
                f"{section_name}_{key}"
            )

            if isinstance(nested_data, dict):
                _write_excel_metrics(
                    workbook,
                    nested_name,
                    nested_data,
                    existing_names,
                )

            elif isinstance(nested_data, (list, tuple)):
                _write_excel_records(
                    workbook,
                    nested_name,
                    list(nested_data),
                    existing_names,
                    context,
                )


def generate_excel_report(
    report_data: dict,
    report_title: str = "School Academic Report",
) -> BytesIO:

    workbook = Workbook()
    summary = workbook.active
    summary.title = "Report Summary"

    existing_names = {"report summary"}

    summary["A1"] = report_title
    summary["A1"].font = Font(
        bold=True,
        size=18,
        color="1F4E78",
    )

    summary["A2"] = "Generated On"
    summary["B2"] = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    summary["A4"] = "Report Contents"
    summary["A4"].font = Font(
        bold=True,
        size=12,
    )

    summary["A5"] = "The detailed report sections are available in the worksheets."

    summary.column_dimensions["A"].width = 35
    summary.column_dimensions["B"].width = 35
    summary.sheet_view.showGridLines = False

    if isinstance(report_data, dict):
        _write_excel_metrics(
            workbook,
            "Report Details",
            report_data,
            existing_names,
        )

        for section_name, section_data in report_data.items():
            if isinstance(section_data, dict):
                _write_excel_metrics(
                    workbook,
                    section_name,
                    section_data,
                    existing_names,
                )

                for nested_name, nested_data in _get_nested_fields(
                    section_data
                ).items():
                    full_name = f"{section_name}_{nested_name}"

                    if isinstance(nested_data, dict):
                        _write_excel_metrics(
                            workbook,
                            full_name,
                            nested_data,
                            existing_names,
                        )
                    elif isinstance(nested_data, (list, tuple)):
                        _write_excel_records(
                            workbook,
                            full_name,
                            list(nested_data),
                            existing_names,
                            _get_scalar_fields(section_data),
                        )

            elif isinstance(section_data, (list, tuple)):
                _write_excel_records(
                    workbook,
                    section_name,
                    list(section_data),
                    existing_names,
                )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


# ==========================================================
# PDF EXPORT
# ==========================================================

def _pdf_text(value: Any) -> str:
    if value is None:
        return "-"

    if isinstance(value, (date, datetime)):
        return value.strftime("%d %b %Y")

    if isinstance(value, float):
        return f"{value:.2f}"

    return escape(str(value))


def _build_pdf_table(
    headers: list,
    rows: list,
    available_width: float,
    styles: dict,
) -> Table:

    header_style = styles["table_header"]
    cell_style = styles["table_cell"]

    table_data = [
        [
            Paragraph(
                _pdf_text(_display_name(header)),
                header_style,
            )
            for header in headers
        ]
    ]

    for row in rows:
        table_data.append([
            Paragraph(
                _pdf_text(value),
                cell_style,
            )
            for value in row
        ])

    column_count = max(len(headers), 1)
    column_width = available_width / column_count

    table = Table(
        table_data,
        colWidths=[column_width] * column_count,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F4E78"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#D9E2F3"),
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F2F5F9"),
                ],
            ),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    return table


def _append_pdf_section(
    elements: list,
    section_name: str,
    section_data: Any,
    styles: dict,
    available_width: float,
    parent_context: dict | None = None,
) -> None:

    parent_context = parent_context or {}

    elements.append(
        Paragraph(
            escape(_display_name(section_name)),
            styles["section"],
        )
    )

    elements.append(Spacer(1, 5))

    if isinstance(section_data, dict):
        scalar_fields = _get_scalar_fields(section_data)

        if scalar_fields:
            headers = ["Metric", "Value"]

            rows = [
                [
                    _display_name(key),
                    _pdf_text(value),
                ]
                for key, value in scalar_fields.items()
            ]

            elements.append(
                _build_pdf_table(
                    headers,
                    rows,
                    available_width,
                    styles,
                )
            )

        for key, nested_data in _get_nested_fields(section_data).items():
            _append_pdf_section(
                elements,
                key,
                nested_data,
                styles,
                available_width,
                scalar_fields,
            )

    elif isinstance(section_data, (list, tuple)):
        records = list(section_data)

        if not records:
            elements.append(
                Paragraph(
                    "No records available.",
                    styles["body"],
                )
            )
        else:
            if not all(isinstance(item, dict) for item in records):
                records = [{"value": item} for item in records]

            headers = list(parent_context.keys())

            for record in records:
                for key in _get_scalar_fields(record):
                    if key not in headers:
                        headers.append(key)

            rows = []

            for record in records:
                row = []

                for header in headers:
                    if header in parent_context:
                        value = parent_context[header]
                    else:
                        value = record.get(header)

                    row.append(_pdf_text(value))

                rows.append(row)

            if headers:
                elements.append(
                    _build_pdf_table(
                        headers,
                        rows,
                        available_width,
                        styles,
                    )
                )

            for record in records:
                context = dict(parent_context)
                context.update(_get_scalar_fields(record))

                for key, nested_data in _get_nested_fields(record).items():
                    _append_pdf_section(
                        elements,
                        key,
                        nested_data,
                        styles,
                        available_width,
                        context,
                    )

    else:
        elements.append(
            Paragraph(
                _pdf_text(section_data),
                styles["body"],
            )
        )

    elements.append(Spacer(1, 12))


def _add_pdf_page_number(canvas, document) -> None:
    canvas.saveState()

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))

    canvas.drawString(
        15 * mm,
        9 * mm,
        "School Intelligence | Academic Report",
    )

    canvas.drawRightString(
        document.pagesize[0] - 15 * mm,
        9 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


def generate_pdf_report(
    report_data: dict,
    report_title: str = "School Academic Report",
) -> BytesIO:

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
        title=report_title,
        author="School Intelligence",
    )

    sample_styles = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=sample_styles["Title"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1F4E78"),
            fontSize=19,
            leading=24,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=sample_styles["Normal"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            fontSize=9,
            spaceAfter=15,
        ),
        "section": ParagraphStyle(
            "ReportSection",
            parent=sample_styles["Heading2"],
            textColor=colors.HexColor("#1F4E78"),
            fontSize=12,
            leading=16,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "body": sample_styles["BodyText"],
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=sample_styles["Normal"],
            textColor=colors.white,
            fontSize=8,
            leading=10,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=sample_styles["Normal"],
            fontSize=7.5,
            leading=10,
        ),
    }

    elements = [
        Paragraph(
            escape(report_title),
            styles["title"],
        ),
        Paragraph(
            "Generated on "
            + datetime.now().strftime("%d %B %Y, %I:%M %p"),
            styles["subtitle"],
        ),
    ]

    available_width = (
        landscape(A4)[0] - 30 * mm
    )

    if isinstance(report_data, dict):
        for section_name, section_data in report_data.items():
            _append_pdf_section(
                elements,
                section_name,
                section_data,
                styles,
                available_width,
            )
    else:
        _append_pdf_section(
            elements,
            "Report Details",
            report_data,
            styles,
            available_width,
        )

    document.build(
        elements,
        onFirstPage=_add_pdf_page_number,
        onLaterPages=_add_pdf_page_number,
    )

    output.seek(0)

    return output
