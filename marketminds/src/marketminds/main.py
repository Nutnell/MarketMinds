#!/usr/bin/env python
from marketminds.crew import MarketmindsCrew

def run():
    """
    Run the crew.
    """
    inputs = {
        'company': 'Microsoft',
        'company_ticker': 'MSFT'
    }
    MarketmindsCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()