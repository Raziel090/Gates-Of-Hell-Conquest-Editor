import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from src
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from src.gui.campaign_editor_gui import CampaignEditorGUI

if __name__ == "__main__":
    campaign_editor_gui = CampaignEditorGUI()
    campaign_editor_gui.run()
