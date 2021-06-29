#! python3  # noqa: E265

"""
    Development script to try QFileDialog abilities and scenarii.
"""

from pathlib import Path
from sys import exit

from qgis.PyQt.QtWidgets import QFileDialog

# HERE = Path(__file__).parent
HERE = "/home/jmo/Git/Oslandia/Projects/Gendarmerie/redLayer/"

options = QFileDialog.Options()
options |= QFileDialog.DontUseNativeDialog
sketch_filepath, sketch_suffix_filter = QFileDialog().getSaveFileName(
    parent=None,
    caption="Save RedLayer sketches",
    directory=HERE,
    filter="All Files (*);;Annotations (*.sketch)",
    initialFilter="Annotations (*.sketch)",
    options=options,
)

if sketch_filepath:
    out_sketch_path = Path(sketch_filepath)
    if out_sketch_path.suffix != ".sketch":
        out_sketch_path = Path(str(out_sketch_path) + ".sketch")
    print("Saving sketches to {}".format(out_sketch_path.resolve()))
else:
    exit("No file selected")

if sketch_suffix_filter:
    print(sketch_suffix_filter)

with out_sketch_path.open(mode="w", encoding="UTF8") as f:
    f.write("toto")
