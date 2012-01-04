import sys
import argparse
import copy

import candidate
import raters


def main():
    rater_instances = []
    for rater_name in args.raters:
        rater_module = getattr(raters, rater_name)
        rater_instances.append(rater_module.Rater())
    for pfdfn in args.infiles:
        cand = candidate.read_pfd_file(pfdfn)
        for rater in rater_instances:
            ratval = rater.rate(cand)
            cand.add_rating(ratval)
        cand.write_ratings_to_file()


class RemoveAllRatersAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [])


class AddAllRatersAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ratlist = copy.deepcopy(raters.registered_raters)
        setattr(namespace, self.dest, ratlist)


class RemoveOneRaterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        rater_name = values[0]
        if rater_name not in raters.registered_raters:
            sys.stderr.write("Unrecognized rater: %s\nThe following " \
                             "raters are registered:\n    %s\n" % \
                             (rater_name, "\n    ".join(raters.registered_raters)))
            sys.exit(1)
        curr_raters = getattr(namespace, self.dest)
        # Remove any instances of 'values' from curr_raters
        while rater_name in curr_raters:
            curr_raters.remove(rater_name)
        setattr(namespace, self.dest, curr_raters)


class AddOneRaterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        rater_name = values[0]
        if rater_name not in raters.registered_raters:
            sys.stderr.write("Unrecognized rater: %s\nThe following " \
                             "raters are registered:\n    %s\n" % \
                             (rater_name, "\n    ".join(raters.registered_raters)))
            sys.exit(1)
        curr_raters = getattr(namespace, self.dest)
        # Add 'rater_name' to curr_raters
        if rater_name not in curr_raters:
            curr_raters.append(rater_name)
        setattr(namespace, self.dest, curr_raters)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rate PFD files.")
    parser.add_argument('infiles', metavar="INFILES", \
                         nargs='+', type=str, \
                         help="PRESTO *.pfd files to rate.")
    parser.add_argument('-x', '--exclude',  dest='raters', \
                         type=str, default=[], nargs=1, \
                         action=RemoveOneRaterAction, \
                         help="Remove rater from list of ratings to apply.")
    parser.add_argument('--exclude-all', dest='raters', \
                         default=[], nargs=0, \
                         action=RemoveAllRatersAction, \
                         help="Clear list of ratings to apply.")
    parser.add_argument('-i', '--include',  dest='raters', \
                         type=str, default=[], nargs=1, \
                         action=AddOneRaterAction, \
                         help="Include rater from list of ratings to apply.")
    parser.add_argument('--include-all', dest='raters', \
                         default=[], nargs=0, \
                         action=AddAllRatersAction, \
                         help="Include all registered ratings in list " \
                                "of ratings to apply.")
    args = parser.parse_args()
    main()
