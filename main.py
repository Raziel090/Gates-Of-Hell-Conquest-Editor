"""Main entry point for the Gates of Hell Conquest Editor."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.gui.campaign_editor_gui import CampaignEditorGUI


def main() -> None:
    """Start the campaign editor GUI."""
    campaign_editor_gui = CampaignEditorGUI()
    campaign_editor_gui.run()


if __name__ == "__main__":
    main()
