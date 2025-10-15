#!/usr/bin/env python
from marketminds.crew import MarketmindsCrewService

def run():
    """
    Run the crew.
    """
    inputs = {
        'company': 'APPLE',
        'company_ticker': 'AAPL'
    }
    MarketmindsCrewService().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()