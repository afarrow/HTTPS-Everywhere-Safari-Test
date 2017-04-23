"""
A simple Python script that generates JSON compatible with Safari's Content
Blocker from HTTPS Everywhere rulesets (XML files). The script avoids trying
to parse rulesets that have exclusions or more than one rewrite rule
"""
import argparse
import json
import os
import re
from bs4 import BeautifulSoup


def get_targets(file, single_file):
    """
    Finds all target domains and subdomains in a ruleset file
    from HTTPS Everywhere. Function doesn't try to parse files with
    exclusions or more than one rewrite rule

    Args:
        file: The file to search for targets
        single_file: A Boolean value, True if get_targets() is only being called on
            a single file (instead of being called through parse_dir())

    Returns:
        A list of the targets in the file
    """
    # Make sure it's an XML file
    if os.path.splitext(file)[1].lower() != '.xml':
        if single_file:
            print('%s is not an xml file' % file)
        return

    with open(file, 'r') as file_obj:
        soup = BeautifulSoup(file_obj.read(), 'xml')

        # Don't continue if the file contains an exclusion
        # or if it contains multiple rewrite rules
        if soup.find('exclusion') is not None or len(soup.find_all('rule')) != 1:
            return

        arr = []
        for target in soup.find_all('target'):
            arr.append(target['host'])

    return arr


def parse_dir(dirpath, output, limit):
    """
    Loops through all the files in a directory and calls get_targets() on
    each one. It bundles all the results together and calls generate_json()

    Args:
        dirpath: The directory to loop through
        output: Where the user wants the results to be output
        limit: The maximum number of files the user wants to parse,
            if limit == -1, there is no maximum
    """
    targets = []
    skipped_files = []
    good_files = 0
    count = 1
    for root, dirs, files in os.walk(dirpath):
        for file in files:
            new_targets = get_targets(os.path.join(root, file), False)
            # Returned None or empty array
            if not new_targets:
                skipped_files.append(file)
            else:
                targets.extend(new_targets)
                good_files += 1
            # Show progress
            print('%d/%d files parsed' % (count, len(files)), end='\r')
            count += 1
            if limit != -1 and good_files >= limit:
                break

    generate_json(targets, output, skipped_files, good_files)


def generate_json(targets, output, skipped_files=None, good_files=0):
    """
    Loops through all the targets given and generates objects which are then
    fed to json.dumps() to create a JSON and outputted the way the user requested
    Also prints all the files that were skipped (if relevant)

    Args:
        targets: A list of all the targets found
        output: Where the user wants the results to be output
        skipped_files: An optional variable, a list of the files that were
            skipped over by get_targets()
        good_files: An optional variable, the number of files that
            get_targets() successfully returned targets from
    """
    # targets == None or targets == []
    if not targets:
        print('ERROR: There were no targets found')
        print('This may have happened because you chose file(s) that '
              + 'contained exclusions and/or multiple rewrite rules. '
              + 'For simplicity\'s sake the script skips over those files '
              + 'for now')
        return

    objs = []
    for target in targets:
        # Here is where the JSON object is generated. Edit the lines below to
        # output different JSON
        objs.append({'trigger':
                        {'url-filter': 'http://' + re.escape(target)},
                     'action':
                        {'type': 'make-https'}
                    })
    json_output = json.dumps(objs, indent=2, separators=(',', ': '))

    # Send to stdout or write to a file
    if output is None:
        print('JSON Generated:')
        print(json_output)
    else:
        with open(output, 'w') as file_obj:
            file_obj.write(json_output)
        print('JSON written to %s' % output)

    if good_files != 0 and skipped_files:
        print('Files skipped: ')
        for file in skipped_files:
            print('   ' + file)
        num_skipped = len(skipped_files)
        print('%d files skipped (%d%%)' % (len(skipped_files),
                                           (100*(num_skipped/(num_skipped+good_files)))))

def is_xml_file(file):
    return os.path.splitext(file)[1].lower() == '.xml'

def is_json_file(file):
    return os.path.splitext(file)[1].lower() == '.json'

def is_int(value):
    """
    Tests to see whether a value can be cast to an int
    Args:
        value: The value to be tested
    Returns:
        True if it can be cast, False if it can't
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description='Generates a JSON file for '
                                     + 'a Safari content blocker from HTTPS '
                                     + 'Everywhere XML files. Running without args '
                                     + 'runs it on the current dir and outputs '
                                     + 'the results to stdout')
    parser.add_argument('-f', '--file',
                        help='Optionally designate an individual XML file you want to parse')
    parser.add_argument('-d', '--dir', default='./',
                        help='Optionally designate the directory that contains the XML files '
                        + 'you want to parse, defaults to the current directory')
    parser.add_argument('-o', '--output',
                        help='Optionally designate the file you want to write the JSON to, '
                        + 'if not used the script outputs to stdout')
    parser.add_argument('-l', '--limit',
                        help='Optionally designate the maximum number of files to parse')

    args = parser.parse_args()

    # Make sure args passed in are legal
    if args.dir is not None and not os.path.isdir(args.dir):
        msg = '%s is not a directory' % args.dir \
              + '. You need to escape spaces if they are in the dirpath'
        raise argparse.ArgumentTypeError(msg)

    if args.file is not None and not is_xml_file(args.file):
        msg = '%s is not an XML file' % args.file \
              + '. You need to escape spaces if they are in the filepath'
        raise argparse.ArgumentTypeError(msg)

    if args.output is not None and not is_json_file(args.output):
        msg = 'The output file %s is not a JSON file' % args.output
        raise argparse.ArgumentTypeError(msg)

    # Generate json for a single file or for a folder based on input
    if args.file is None:
        args.limit = -1 if args.limit is None or not is_int(args.limit) else int(args.limit)
        parse_dir(args.dir, args.output, args.limit)
    else:
        generate_json(get_targets(args.file, True), args.output)


main()
