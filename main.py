import logging
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from rich.live import Live
from scraper import GoogleDorkScraper
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class ScraperUI:
    def __init__(self):
        self.console = Console()
        self.stats = {
            'total_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'api_calls': 0
        }
        self.latest_results = []
        self.max_results_display = 8

    def load_custom_dorks(self, filename='custom_dorks.txt'):
        """Load custom dorks from a file"""
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write('site:.za "contact us" "phone" "ceo" "director" "president"\n')
                f.write('site:.za "about us" "management team" "contact"\n')
                f.write('site:.za "board of directors" "contact details"\n')
            logging.info(f"Created default {filename}")

        with open(filename, 'r') as f:
            dorks = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(dorks)} custom dorks from {filename}")
        return dorks

    def create_stats_table(self):
        """Create statistics table"""
        table = Table(title="Scraping Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="left")
        
        for metric, value in self.stats.items():
            table.add_row(
                metric.replace('_', ' ').title(),
                str(value)
            )
        
        return Panel(table, title="Statistics", border_style="blue")

    def create_results_table(self):
        """Create results preview table"""
        table = Table(box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Position", style="green")
        table.add_column("Company", style="yellow")
        table.add_column("Contact", style="blue")

        # Display the most recent results, limited to max_results_display
        for result in self.latest_results[-self.max_results_display:]:
            table.add_row(
                result.get('name', ''),
                result.get('position', ''),
                result.get('company', ''),
                result.get('contact', '')
            )

        # Fill remaining rows with empty space if needed
        remaining_rows = self.max_results_display - len(self.latest_results)
        for _ in range(remaining_rows):
            table.add_row('', '', '', '')

        return Panel(table, title="Latest Results", border_style="blue")

    def update_display(self, live):
        """Update the live display"""
        layout = Layout()
        layout.split_column(
            Layout(name="upper", size=10),
            Layout(name="lower", size=10)
        )
        
        layout["upper"].update(self.create_stats_table())
        layout["lower"].update(self.create_results_table())
        
        live.update(Panel(layout, title="Live Preview", border_style="cyan"))

    def run_scraper(self):
        """Run the scraper with live updates"""
        dorks = self.load_custom_dorks()
        scraper = GoogleDorkScraper(dorks, pages_to_scrape=10)

        with Live(auto_refresh=False) as live:
            for dork in dorks:
                logging.info(f"Searching with dork: {dork}")
                try:
                    results = scraper.search(dork)
                    self.stats['api_calls'] += 1
                    
                    if results and 'items' in results:
                        for item in results['items']:
                            self.stats['total_processed'] += 1
                            try:
                                contact_info = scraper.process_contact_page(item.get('link', ''))
                                if contact_info:
                                    self.stats['successful_extractions'] += 1
                                    self.latest_results.append({
                                        'name': contact_info.get('contact_person', ''),
                                        'position': contact_info.get('position', ''),
                                        'company': contact_info.get('company_name', ''),
                                        'contact': contact_info.get('email', '') or contact_info.get('phone', '')
                                    })
                                else:
                                    self.stats['failed_extractions'] += 1
                            except Exception as e:
                                self.stats['failed_extractions'] += 1
                                logging.error(f"Error processing result: {str(e)}")
                    
                    self.update_display(live)
                    live.refresh()
                    
                except Exception as e:
                    logging.error(f"Error with dork '{dork}': {str(e)}")
                    continue

def main():
    try:
        ui = ScraperUI()
        ui.run_scraper()
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        logging.info("Scraping completed")

if __name__ == "__main__":
    main()