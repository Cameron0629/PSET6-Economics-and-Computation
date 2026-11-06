#!/usr/bin/env python3

# Ad slot auction simulator
# CSCI336901: Economics and Computation, Boston College

# All math is done using integers to avoid dealing with floating point:
#  - bids and budgets are specified in integer cents
#  - clicks / slot is rounded to the nearest click

from optparse import OptionParser
import importlib
import inspect
import itertools
import logging
import math
import random
import sys

from gsp import GSP
from vcg import VCG
from history import History
from stats import Stats

from util import shuffled, mean, stddev

# Infinite stream of zeros
zeros = itertools.repeat(0)

def iround(x):
    """Round x and return an int"""
    return int(round(x))

def agent_slot(occupants, a_id, t):
    """Return the slot agent with id a_id occupied in round t,
    or -1 if a_id wasn't present in round t"""
    agents = occupants[t]
    if a_id in agents:
        return agents.index(a_id)
    else:
        return -1


def sim(config):
    agents = init_agents(config)
    # Uncomment to print agents.
    #for a in agents:
    #    logging.info(a)

    n = len(agents)
    by_id = dict((a.id, a) for a in agents)
    agent_ids = [a.id for a in agents]

    if (config.mechanism.lower() == 'gsp' or
        config.mechanism.lower() == 'switch'):
        mechanism = GSP
    elif config.mechanism.lower() == 'vcg':
        mechanism = VCG
    else:
        raise ValueError("mechanism must be one of 'gsp', 'vcg', or 'switch'")

    reserve = config.reserve

    # Dictionaries : round # -> per_slot_list_of_whatever
    slot_occupants = {}
    slot_clicks = {}
    per_click_payments = {}
    slot_payments = {}
    values = {}
    bids = {}

    history = History(bids, slot_occupants, slot_clicks,
                      per_click_payments, slot_payments, n)

    def total_spent(agent_id, end):
        """
        Compute total amount spent by agent_id through (not including)
        round end.
        """
        s = 0
        for t in range(end):
            slot = agent_slot(slot_occupants, agent_id, t)
            if slot != -1:
                s += slot_payments[t][slot]
        return s

    def run_round(top_slot_clicks, t):
        """ top_slot_clicks is the expected number of clicks in the top slot
            k is the round number
        """
        if t == 0:
            bids[t] = [(a.id, a.initial_bid(reserve)) for a in agents]
        else:
            # Bids from agents with no money get reduced to zero.
            current_bids = []
            for a in agents:
                b = a.bid(t, history, reserve)
                if total_spent(a.id, t) < config.budget:
                    current_bids.append( (a.id, b))
                else:
                    # Out of money: make bid zero.
                    current_bids.append( (a.id, 0))
            bids[t] = current_bids

        # The classroom simulator uses one fewer slot than agents.
        num_slots = max(1, n - 1)

        ##   1b.  Calculate clicks/slot
        slot_clicks[t] = [iround(top_slot_clicks * pow(config.dropoff, i))
                          for i in range(num_slots)]

        ##  2. Run mechanism and allocate slots
        (slot_occupants[t], per_click_payments[t]) = (
            mechanism.compute(slot_clicks[t],
                              reserve, bids[t]))

        ##  3. Define payments
        slot_payments[t] = [x_y[0]*x_y[1] for x_y in zip(slot_clicks[t], per_click_payments[t])]

        ##  4.  Save utility (misnamed as values)
        values[t] = dict(list(zip(agent_ids, zeros)))

        def agent_value(agent_id, clicks, payment):
            if agent_id is not None:
                values[t][agent_id] = by_id[agent_id].value * clicks - payment
            return None

        list(map(agent_value, slot_occupants[t], slot_clicks[t], slot_payments[t]))

        # Detailed round output is available only with --loglevel debug.
        logging.debug("\t=== Round %d ===", t)
        logging.debug("\tnum_slots: %d", num_slots)
        logging.debug("\tbids: %s", bids[t])
        logging.debug("\tslot occupants: %s", slot_occupants[t])
        logging.debug("\tslot_clicks: %s", slot_clicks[t])
        logging.debug("\tper_click_payments: %s", per_click_payments[t])
        logging.debug("\tslot_payments: %s", slot_payments[t])
        logging.debug("\tUtility: %s", values[t])
        logging.debug(
            "\ttotals spent: %s",
            [total_spent(a.id, t + 1) for a in agents],
        )

    for t in range(0, config.num_rounds):
        # Over 48 rounds, go from 80 to 20 and back to 80.  Mean 50.
        # Makes sense when 48 rounds, to simulate a day
        top_slot_clicks = iround(30*math.cos(math.pi*t/24) + 50)

        if t == config.num_rounds // 2 and config.mechanism.lower() == 'switch':
            mechanism = VCG
        ##   0.  Runs one round
        run_round(top_slot_clicks, t)
        for a in agents:
            history.set_agent_spent(a.id, total_spent(a.id, t + 1))

    for a in agents:
        history.set_agent_spent(a.id, total_spent(a.id, config.num_rounds))

    return history

class Params:
    def __init__(self):
        self._init_keys = set(self.__dict__.keys())

    def add(self, k, v):
        self.__dict__[k] = v

    def __repr__(self):
        return "; ".join("%s=%s" % (k, str(self.__dict__[k]))
                         for k in list(self.__dict__.keys()) if k not in self._init_keys)


def load_modules(agent_classes):
    """Load agent classes from modules with matching lowercase names.

    Class-name matching is case-insensitive, so both ``Abxybb`` and
    ``abxybb`` work on the command line when ``abxybb.py`` defines
    ``class Abxybb``.
    """

    def load(class_name):
        module_name = class_name.lower()
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name:
                raise ModuleNotFoundError(
                    f"Could not find agent module {module_name}.py for {class_name!r}."
                ) from exc
            raise

        matches = [
            obj
            for name, obj in vars(module).items()
            if inspect.isclass(obj)
            and obj.__module__ == module.__name__
            and name.lower() == class_name.lower()
        ]
        if len(matches) != 1:
            expected = module_name[0].upper() + module_name[1:]
            raise AttributeError(
                f"{module_name}.py must define one class named {expected} "
                f"(capitalization on the command line is ignored)."
            )
        return class_name, matches[0]

    return dict(load(class_name) for class_name in set(agent_classes))


def init_agents(conf):
    """Each agent class must be already loaded, and have a
    constructor that takes an id, a value, and a budget, in that order."""
#    params = [(0, 10, conf.budget), (1, 20, conf.budget), (2, 30, conf.budget)]
    n = len(conf.agent_class_names)
    params = list(zip(list(range(n)), conf.agent_values, itertools.repeat(conf.budget)))
    def load(class_name, params):
        agent_class = conf.agent_classes[class_name]
        return agent_class(*params)

    return list(map(load, conf.agent_class_names, params))

def get_utils(n, options):
    m = options.min_val
    M = options.max_val
    return [random.randint(m, M) for i in range(n)]

def configure_logging(loglevel):
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate output if main() is invoked more than once in a process.
    for handler in list(root_logger.handlers):
        if getattr(handler, '_econcs_auction_handler', False):
            root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler._econcs_auction_handler = True
    stream_handler.setFormatter(logging.Formatter('%(message)s'))
    root_logger.addHandler(stream_handler)

def parse_agents(args):
    """
    Each element is a class name like "Peer", with an optional
    count appended after a comma.  So either "Peer", or "Peer,3".
    Returns an array with a list of class names, each repeated the
    specified number of times.
    """
    ans = []
    for c in args:
        s = c.split(',')
        if len(s) == 1:
            ans.extend(s)
        elif len(s) == 2:
            name, count = s
            ans.extend([name]*int(count))
        else:
            raise ValueError("Bad argument: %s\n" % c)
    return ans

def main(args):

    usage_msg = "Usage:  %prog [options] PeerClass1[,cnt] PeerClass2[,cnt2] ..."
    parser = OptionParser(usage=usage_msg)

    def usage(msg):
        print("Error: %s\n" % msg)
        parser.print_help()
        sys.exit()

    parser.add_option("--loglevel",
                      dest="loglevel", default="info",
                      help="Set the logging level: 'debug' or 'info'")

    parser.add_option("--mech",
                      dest="mechanism", default="gsp",
                      help="Set the mechanism: 'gsp', 'vcg', or 'switch'")

    parser.add_option("--num-rounds",
                      dest="num_rounds", default=48, type="int",
                      help="Set number of rounds")

    parser.add_option("--min-val",
                      dest="min_val", default=25, type="int",
                      help="Min per-click value, in cents")

    parser.add_option("--max-val",
                      dest="max_val", default=175, type="int",
                      help="Max per-click value, in cents")

    parser.add_option("--budget",
                      dest="budget", default=500000, type="int",
                      help="Total budget, in cents")

    parser.add_option("--reserve",
                      dest="reserve", default=0, type="int",
                      help="Reserve price, in cents")

    parser.add_option("--perms",
                      dest="max_perms", default=120, type="int",
                      help="Max number of value permutations to run.  Set to 1 for debugging.")

    parser.add_option("--iters",
                      dest="iters", default=1, type="int",
                      help="Number of different value draws to sample. Set to 1 for debugging.")

    parser.add_option("--seed",
                      dest="seed", default=None, type="int",
                      help="seed for random numbers")


    (options, args) = parser.parse_args()

    # leftover args are class names:
    # e.g. "Truthful BBAgent CleverBidder Fred"

    if len(args) == 0:
        # default
        agents_to_run = ['Truthful', 'Truthful', 'Truthful']
    else:
        agents_to_run = parse_agents(args)

    configure_logging(options.loglevel)

    if options.seed is not None:
        random.seed(options.seed)

    # Add some more config options
    options.agent_class_names = agents_to_run
    options.agent_classes = load_modules(options.agent_class_names)
    options.dropoff = 0.75

    logging.info("Starting simulation...")
    n = len(agents_to_run)

    totals = dict((id, 0) for id in range(n))
    total_revenues = []

    approx = math.factorial(n) > options.max_perms
    if approx:
        num_perms = options.max_perms
        logging.warning(
            "Running approximation: taking %d samples of value permutations"
            % options.max_perms)
    else:
        num_perms = math.factorial(n)

    total_spent = [0 for i in range(n)]

    ##  iters = no. of samples to take
    for i in range(options.iters):
        values = get_utils(n, options)
        logging.debug("==== Iteration %d / %d. Values %s ====", i + 1, options.iters, values)
        ## Create permutations (permutes the random values, and assigns them to agents)
        if approx:
            perms = [shuffled(values) for i in range(options.max_perms)]
        else:
            perms = itertools.permutations(values)

        total_rev = 0
        ## Iterate over permutations
        for vals in perms:
            options.agent_values = list(vals)
            values = dict(list(zip(list(range(n)), list(vals))))
            ##   Runs simulation  ###
            history = sim(options)
            ###  simulation ends.
            stats = Stats(history, values)
            # Print stats in console?
            # logging.info(stats)

            for id in range(n):
                totals[id] += stats.total_utility(id)
                total_spent[id] += history.agents_spent[id]
            total_rev += stats.total_revenue()
        total_revenues.append(total_rev / float(num_perms))

    ## total_spent = total amount of money spent by agents, for all iterations, all permutations, all rounds


    # Averages are over all the value permutations considered
    N = float(num_perms) * options.iters
    logging.info("%s\t\t%s\t\t%s" % ("#" * 15, "RESULTS", "#" * 15))
    logging.info("")
    for a in range(n):
        logging.info("Stats for Agent %d, %s" % (a, agents_to_run[a]) )
        logging.info("Average spend $%.2f (daily)" % (0.01 *total_spent[a]/N)  )
        logging.info("Average  utility  $%.2f (daily)" % (0.01 * totals[a]/N))
        logging.info("-" * 40)
        logging.info("\n")
    m = mean(total_revenues)
    std = stddev(total_revenues)
    logging.warning("Average daily revenue (stddev): $%.2f ($%.2f)" % (0.01 * m, 0.01*std))

#print "config", config.budget


    #for t in range(47, 48):
    #for a in agents:
        #print a,"'s added values is", av_value[a.id]



if __name__ == "__main__":
    main(sys.argv)
