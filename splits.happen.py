#!/usr/bin/python

# depends: requests

import json
import requests
import sys


def frames_string_to_list(frames_string):
    '''
    This function converts an input string in the expected input format:

        XXXXXXXXXXXX
        9-9-9-9-9-9-9-9-9-9-
        5/5/5/5/5/5/5/5/5/5/5
        X7/9-X-88/-6XXX81

    to the list format expected by the `Randock Bowling API <https://api.randock.com/docs#post--bowling-score.{_format}>`:

        [[10], [10], [10], [10], [10], [10], [10], [10], [10], [10, 10, 10]]
        [['9', 0], ['9', 0], ['9', 0], ['9', 0], ['9', 0], ['9', 0], ['9', 0], ['9', 0], ['9', 0], ['9', 0]]
        [['5', 5], ['5', 5], ['5', 5], ['5', 5], ['5', 5], ['5', 5], ['5', 5], ['5', 5], ['5', 5], ['5', 5, '5']]
        [[10], ['7', 3], ['9', 0], [10], [0, '8'], ['8', 2], [0, '6'], [10], [10], [10, '8', '1']]

    '''
    frames = []
    current = []
    
    for idx, roll in enumerate(frames_string):
        if roll == 'X':
            result = 10
        elif roll == '/':
            prev_roll = int(frames_string[idx - 1])
            result = (10 - prev_roll)
        elif roll == '-':
            result = 0
        else:
            result = roll
    
        current.append(result)
    
        if (result == 10 or len(current) == 2) and len(frames) != 9:
            frames.append(current)
            current = []
        elif idx == len(frames_string) - 1 and len(frames) == 9:
            frames.append(current)
            current = []

    return frames


def request_score(verb='POST', server='https://api.randock.com/bowling/score.json', auth=None, verify=True, data=None):
    '''
    This function uses the `Randock Bowling API <https://api.randock.com/docs#post--bowling-score.{_format}>` to
    calculate a given bowling score.

    The reasons I did this:
      * I'm not a developer. I'm an integrator. I won't reinvent the wheel if there's something out there I can use.
      * I didn't see any rule precluding me from this solution.
      * Math.
    '''
    try:
        r = requests.request(verb.upper(), server, auth=auth, verify=verify, data=data)

        if r.status_code != 200:
            print('ERROR: Request to "{0}" returned HTTP {1}.'.format(server, r.status_code))
            sys.exit(1)

        return json.loads(r.text)['score']
    except requests.exceptions.ConnectionError:
        print('ERROR: Unable to contact bowling API at "{0}"!'.format(server))
        sys.exit(1)
    except (KeyError, ValueError):
        print('ERROR: Invalid score JSON returned!'.format(server))
        sys.exit(1)


# MAIN
if __name__ == '__main__':
    # Accept frames string via command line argument or standard input.
    if len(sys.argv) == 1:
        frames_string = raw_input('Please enter the frames to score: ')
    else:
        frames_string = sys.argv[1]

    # Convert the frames string to a list (total frames) of lists (rolls in a frame).
    frames_list = frames_string_to_list(frames_string)

    # Return the score from the API
    score = request_score(data=json.dumps({'frames': frames_list}))

    # Print the score.
    print('The bowling score is: {0}'.format(score))
