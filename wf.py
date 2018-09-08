#!/usr/bin/env python3

from urllib.request import Request, urlopen
import json
import os.path
import argparse

DB_FILENAME = "db.json"


def _update_database():
    """
    This function downloads the drop rates from Warframe's API and stores them
    to a local file. The stored file uses the item name as the key and the
    dictionary entry from the API as the value.
    """

    # Set user agent to something else otherwise we'll get a 403 forbidden
    # error because they don't want us scraping it.
    req = Request('https://api.warframestat.us/drops',
                  headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as dropsURL:
        # Load in the data from the URL to a json object.
        data = json.loads(dropsURL.read().decode())
        result = {}
        # Iterate through the entries and enter them into our result
        # dictionary.
        for item_dict in data:
            item_name = item_dict['item'].upper()
            if item_name not in result:
                result[item_name] = []
            # We key on the item name in all upper case so that it's easier for
            # users to search (we will uppercase their query too).
            result[item_name].append(item_dict)
        # Write the file
        with open(DB_FILENAME, "w+") as outfile:
            outfile.truncate(0)
            json.dump(result, outfile)
            outfile.close()


def _lookup_item(item_name):
    """
    This function opens the existing DB file and looks up a given item name.
    It then sorts the results based on descending chance and prints out the
    location of the drop and the % chance.
    """

    # Load the local DB.
    with open(DB_FILENAME) as db_file:
        db_dict = json.load(db_file)
        uppercased_name = item_name.upper()

        # Look for all results that contain the query string.
        filtered_dict = {k:v for (k,v) in db_dict.items() if uppercased_name in k}
        # If the item isn't found, tell the user and return.
        if len(filtered_dict) == 0:
            print("{} not found.".format(item_name))
            return
        for (result_name, results) in filtered_dict.items():
            # Sort the results in descending 'chance' order.
            result_locations = sorted(results,
                                      key=lambda k: float(k['chance']),
                                      reverse=True)
            # Print the results.
            print("===== {} =====".format(result_name))
            for r in result_locations:
                print("Chance: {}%, Location: {}".format(r['chance'], r['place']))


def main():
    parser = argparse.ArgumentParser(
        description='Script to query drop rates for items in Warframe.')
    parser.add_argument('--force-refresh',
                        action='store_true',
                        required=False,
                        help='Pass this to force update the DB in '
                             'the local cache.')
    parser.add_argument('item',
                        help='Name of the item to query.')
    args = parser.parse_args()
    if args.force_refresh or not os.path.isfile(DB_FILENAME):
        _update_database()
    _lookup_item(args.item)

if __name__ == "__main__":
    main()
