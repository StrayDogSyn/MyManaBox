"""
Daily Sync Automation
Automatically sync collection from ManaBox exports
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from cardforge.importers import ManaBoxImporter
from cardforge.services import CollectionService, PricingService
from cardforge.api_clients import ScryfallClient


logger = logging.getLogger(__name__)


class DailySync:
    """
    Daily collection synchronization automation.
    
    Workflow:
    1. Check for new ManaBox CSV exports
    2. Import new cards
    3. Enrich with Scryfall data
    4. Update prices
    5. Generate report
    6. Send notification
    """
    
    def __init__(
        self,
        watch_directory: Path,
        collection_id: int = 1,
        backup: bool = True,
    ):
        """
        Initialize daily sync.
        
        Args:
            watch_directory: Directory to watch for CSV exports
            collection_id: Target collection ID
            backup: Create backup before sync
        """
        self.watch_directory = Path(watch_directory)
        self.collection_id = collection_id
        self.backup = backup
        
        # Services
        self.importer = ManaBoxImporter()
        self.collection_service = CollectionService()
        self.pricing_service = PricingService()
        self.scryfall_client = ScryfallClient()
        
        # Stats
        self.last_sync: Optional[datetime] = None
        self.sync_count = 0
    
    async def run(self) -> dict:
        """
        Run daily sync process.
        
        Returns:
            Sync statistics and results
        """
        logger.info("Starting daily sync...")
        start_time = datetime.now()
        
        results = {
            "started_at": start_time.isoformat(),
            "status": "success",
            "steps": {},
            "errors": [],
        }
        
        try:
            # Step 1: Find new CSV files
            logger.info("Step 1: Checking for new CSV exports...")
            csv_files = await self._find_new_csv_files()
            results["steps"]["csv_discovery"] = {
                "files_found": len(csv_files),
                "files": [str(f) for f in csv_files],
            }
            
            if not csv_files:
                logger.info("No new CSV files found")
                results["status"] = "no_changes"
                return results
            
            # Step 2: Import CSV files
            logger.info(f"Step 2: Importing {len(csv_files)} CSV file(s)...")
            import_stats = await self._import_csv_files(csv_files)
            results["steps"]["import"] = import_stats
            
            # Step 3: Enrich with Scryfall data
            logger.info("Step 3: Enriching cards with Scryfall data...")
            enrich_stats = await self._enrich_cards()
            results["steps"]["enrichment"] = enrich_stats
            
            # Step 4: Update prices
            logger.info("Step 4: Updating card prices...")
            price_stats = await self._update_prices()
            results["steps"]["pricing"] = price_stats
            
            # Step 5: Generate report
            logger.info("Step 5: Generating sync report...")
            report = await self._generate_report(results)
            results["steps"]["report"] = report
            
            # Step 6: Send notification
            logger.info("Step 6: Sending notification...")
            await self._send_notification(results)
            
            # Update sync metadata
            self.last_sync = datetime.now()
            self.sync_count += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            results["completed_at"] = datetime.now().isoformat()
            results["duration_seconds"] = duration
            
            logger.info(f"Daily sync completed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Daily sync failed: {e}", exc_info=True)
            results["status"] = "failed"
            results["errors"].append(str(e))
        
        return results
    
    async def _find_new_csv_files(self) -> list[Path]:
        """Find new CSV files in watch directory."""
        if not self.watch_directory.exists():
            logger.warning(f"Watch directory does not exist: {self.watch_directory}")
            return []
        
        # Find all CSV files
        csv_files = list(self.watch_directory.glob("*.csv"))
        
        # Filter by modification time (last 24 hours)
        recent_files = []
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
        
        for csv_file in csv_files:
            if csv_file.stat().st_mtime > cutoff_time:
                recent_files.append(csv_file)
        
        return recent_files
    
    async def _import_csv_files(self, csv_files: list[Path]) -> dict:
        """Import multiple CSV files."""
        total_stats = {
            "files_processed": 0,
            "total_imported": 0,
            "total_errors": 0,
            "files": [],
        }
        
        for csv_file in csv_files:
            try:
                logger.info(f"Importing {csv_file.name}...")
                
                stats = await self.importer.import_manabox_csv(
                    file_path=csv_file,
                    collection_id=self.collection_id,
                    merge=True,  # Always merge for daily sync
                    backup=self.backup,
                )
                
                total_stats["files_processed"] += 1
                total_stats["total_imported"] += stats["imported"]
                total_stats["total_errors"] += stats["errors"]
                total_stats["files"].append({
                    "name": csv_file.name,
                    "imported": stats["imported"],
                    "errors": stats["errors"],
                })
                
                # Move processed file to archive
                archive_dir = self.watch_directory / "processed"
                archive_dir.mkdir(exist_ok=True)
                csv_file.rename(archive_dir / csv_file.name)
                
            except Exception as e:
                logger.error(f"Failed to import {csv_file}: {e}")
                total_stats["total_errors"] += 1
        
        return total_stats
    
    async def _enrich_cards(self) -> dict:
        """Enrich cards with Scryfall data."""
        # Get cards without Scryfall data
        collection = await self.collection_service.get_by_id(self.collection_id)
        
        if not collection:
            return {"enriched": 0, "errors": 0}
        
        # This would call Scryfall API to enrich cards
        # For now, return placeholder stats
        return {
            "enriched": 0,
            "errors": 0,
            "note": "Enrichment requires Scryfall API integration",
        }
    
    async def _update_prices(self) -> dict:
        """Update card prices."""
        try:
            # Update prices for all cards in collection
            stats = await self.pricing_service.update_collection_prices(
                self.collection_id
            )
            return stats
        except Exception as e:
            logger.error(f"Price update failed: {e}")
            return {"updated": 0, "errors": 1, "error": str(e)}
    
    async def _generate_report(self, results: dict) -> dict:
        """Generate sync report."""
        # Get collection stats
        stats = await self.collection_service.get_stats(self.collection_id)
        
        return {
            "collection_stats": {
                "unique_cards": stats.unique_cards,
                "total_cards": stats.total_cards,
                "total_value": str(stats.total_value),
            },
            "sync_summary": {
                "files_processed": results["steps"].get("import", {}).get("files_processed", 0),
                "cards_imported": results["steps"].get("import", {}).get("total_imported", 0),
                "errors": results["steps"].get("import", {}).get("total_errors", 0),
            },
        }
    
    async def _send_notification(self, results: dict) -> None:
        """Send Windows notification."""
        try:
            from winotify import Notification, audio
            
            status = results["status"]
            imported = results["steps"].get("import", {}).get("total_imported", 0)
            
            toast = Notification(
                app_id="CardForge",
                title="Daily Sync Complete",
                msg=f"Status: {status}\nCards imported: {imported}",
                duration="short",
            )
            
            if status == "success":
                toast.set_audio(audio.Default, loop=False)
            else:
                toast.set_audio(audio.LoopingAlarm, loop=False)
            
            toast.show()
            
        except ImportError:
            logger.warning("winotify not installed - skipping notification")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


async def main():
    """Run daily sync as standalone script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Default watch directory
    watch_dir = Path("data/imports")
    watch_dir.mkdir(parents=True, exist_ok=True)
    
    sync = DailySync(watch_directory=watch_dir)
    results = await sync.run()
    
    print("\n=== Daily Sync Results ===")
    print(f"Status: {results['status']}")
    print(f"Duration: {results.get('duration_seconds', 0):.2f}s")
    
    if "import" in results["steps"]:
        import_stats = results["steps"]["import"]
        print(f"Files processed: {import_stats['files_processed']}")
        print(f"Cards imported: {import_stats['total_imported']}")
        print(f"Errors: {import_stats['total_errors']}")


if __name__ == "__main__":
    asyncio.run(main())
