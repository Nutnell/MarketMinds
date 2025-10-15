#!/usr/bin/env python
from marketminds.crew import MarketmindsCrew

def run():
    """
    Run the crew.
    """
    inputs = {
        'company': 'Tesla'
    }
    MarketmindsCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()