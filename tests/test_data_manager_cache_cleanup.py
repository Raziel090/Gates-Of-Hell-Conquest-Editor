import tempfile
import unittest
import zipfile
from pathlib import Path

from src.data_manager import DataManager


class _DummyLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)


class DataManagerCacheCleanupTests(unittest.TestCase):
    def test_extract_campaign_files_removes_stale_files_before_extract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            campaign_cache_dir = root / "data" / "campaign"
            campaign_cache_dir.mkdir(parents=True)
            stale_file = campaign_cache_dir / "stale_only_from_old_save.txt"
            stale_file.write_text("old", encoding="utf-8")

            save_path = root / "new_save.sav"
            with zipfile.ZipFile(save_path, "w") as save_archive:
                save_archive.writestr("campaign.scn", "campaign content")
                save_archive.writestr("status", "status content")

            data_manager = DataManager.__new__(DataManager)
            data_manager.campaign_data_dir_path = campaign_cache_dir
            data_manager.campaign_save_file_path = save_path
            data_manager.logger = _DummyLogger()

            data_manager.extract_campaign_files()

            self.assertFalse(stale_file.exists())
            self.assertTrue((campaign_cache_dir / "campaign.scn").exists())
            self.assertTrue((campaign_cache_dir / "status").exists())


if __name__ == "__main__":
    unittest.main()
