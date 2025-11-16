# split-json.py

import json
import argparse


def filterData (entry, Month, Day, Year, Interface, Direction):
    # Filter the data based on the Month, Year, and Interface
    if (Interface != 'any') and (entry['interface'] != Interface):
        return False

    if (Direction != 'any') and (entry['direction'] != Direction):
        return False

    if entry['type'] != 'iperf':
        return False

    #  print('Checking the timestamp')
    #  print('  Entry: ', entry['timestamp'])
    #  print('  Month: ', Month, ' vs. ', entry['timestamp'].split('-')[1])

    split_timestamp = entry['timestamp'].split('-')
    #print(split_timestamp)

    if (Month != 0) and (int(split_timestamp[1]) != Month):
        # print('Filtering on month')
        return False

    # First two values of third section are the day
    if (Day != 0) and (int(split_timestamp[2][0:2]) != Day):
        return False

    if (Year != 0) and (split_timestamp[0] != str(Year)):
        return False

    #  print('Do not filter')
    return True


# Are we being executed directly?
if __name__ == "__main__":
    # Define the various arguments via argparse
    parser = argparse.ArgumentParser(description='Split up the JSON')
    parser.add_argument('InputJSON', type=str, help='Filename as an input')
    parser.add_argument('Month', type=int, help='Month to include')
    parser.add_argument('Day', type=int, help='Day to include')
    parser.add_argument('Year', type=int, help='Year to include')
    parser.add_argument('Interface', type=str, help='Interface to include. Put "any" for all interfaces')
    parser.add_argument('Direction', type=str, help='Direction to include (uplink/downlink). Put "any" for all directions')
    parser.add_argument('OutputFile', type=str, help='Filename as an output')

    args = parser.parse_args()

    theData = json.loads(open(args.InputJSON).read())
    print('Detected ', len(theData), ' entries in the JSON file')
    # print(theData)

    NumEntries = len(theData)

    filteredData = list(filter(lambda entry: filterData(entry, args.Month, args.Day, args.Year,
                                                        args.Interface, args.Direction), theData))

    filteredData.sort(key=lambda entry: entry['timestamp'])

    print('Post Filtering: ', len(filteredData), ' entries in the JSON file')

    with open(args.OutputFile, 'w') as f:
        # Write the JSON to the file
        f.write(json.dumps(filteredData, indent=4))
        # Is this really needed?
        f.close()