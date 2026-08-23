"""Provenza AI - JSON/CSV Exporter

Exports product records to commerce-ready formats.
"""

import csv
import json
import logging
from io import StringIO
from pathlib import Path
from typing import Optional

from app.models.product import ProductRecord
from app.config import EXPORTS_DIR

logger = logging.getLogger(__name__)


def export_to_json(product: ProductRecord, file_path: Optional[str] = None) -> str:
    """Export product record to JSON string. Optionally save to file."""
    data = product.to_commerce_dict()
    json_str = json.dumps(data, indent=2, default=str)

    if file_path:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_text(json_str, encoding="utf-8")
        logger.info(f"Exported JSON to {file_path}")

    return json_str


def export_to_csv(product: ProductRecord, file_path: Optional[str] = None) -> str:
    """Export product record to CSV string. Optionally save to file."""
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Product ID", "Product Name", "Brand", "Category", "Model Number",
        "Attribute", "Value", "Unit", "Source", "Confidence", "Status",
        "Evidence", "Reasoning"
    ])

    # Rows
    for attr_name, attr in product.attributes.items():
        writer.writerow([
            product.product_id,
            product.product_name,
            product.brand,
            product.category,
            product.model_number,
            attr.display_name or attr.attribute,
            attr.value or "",
            attr.unit or "",
            attr.source,
            f"{attr.confidence:.2f}",
            attr.status,
            attr.evidence,
            attr.reasoning,
        ])

    csv_str = output.getvalue()

    if file_path:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_text(csv_str, encoding="utf-8")
        logger.info(f"Exported CSV to {file_path}")

    return csv_str


def get_export_path(product_id: str, format: str) -> str:
    """Generate export file path."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return str(EXPORTS_DIR / f"{product_id}.{format}")
