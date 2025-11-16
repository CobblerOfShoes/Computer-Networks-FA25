import requests
import time
import argparse

parser = argparse.ArgumentParser(description='Measure request times to specified endpoints.')
parser.add_argument('--ip', type=str, default='localhost', help='Base URL of the server')
parser.add_argument('--port', type=int, default=54011, help='Port number of the server')
parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

args = parser.parse_args()
URL = f"http://{args.ip}:{args.port}"

def time_request(url):
    if args.verbose:
        print(f'Making request to: {url}')
    start_time = time.time()
    response = requests.get(f"{url}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    return response.status_code, elapsed_time

def endpoint_statistics(url):
    timings = []
    for i in range(15):
        if args.verbose:
            print(f'Request #{i + 1}')
        status_code, elapsed_time = time_request(url)
        if args.verbose:
            print(f'Completed in {elapsed_time:.4f}s')
        timings.append(elapsed_time)
    average_time = sum(timings) / len(timings)
    median_time = sorted(timings)[len(timings) // 2]
    stdev_time = (sum((x - average_time) ** 2 for x in timings) / len(timings)) ** 0.5
    return average_time, min(timings), max(timings), median_time, stdev_time

if __name__ == "__main__":
    endpoints = ['/data',
                 '/dl/stat/mean?y=2024&m=5&if=wlan0&dir=downlink',
                 '/dl/stat/peak?y=2024&m=5&if=wlan0&dir=downlink']
    for endpoint in endpoints:
        url = URL + endpoint
        avg, min_time, max_time, median, stdev = endpoint_statistics(url)
        print(f"Endpoint: {endpoint}")
        print(f"  Average Time: {avg:.4f} seconds")
        print(f"  Min Time: {min_time:.4f} seconds")
        print(f"  Max Time: {max_time:.4f} seconds")
        print(f"  Median Time: {median:.4f} seconds")
        print(f"  Standard Deviation: {stdev:.4f} seconds\n")
        print("-" * 40)