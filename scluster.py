import hashlib
import json
import os
import sys

from argparse import ArgumentParser
from collections import defaultdict
from glob import glob
from shutil import copy2
from timeit import default_timer as timer

import ssdeep


class Clusters(object):
    def __init__(self, input_paths, threshold):
        self.threshold = threshold
        self.samples = {}
        self.clusters = defaultdict(list)
        self.paths = get_input(input_paths)
        self.populate()

    def populate(self):
        self.populate_samples()
        self.populate_clusters()

    def populate_samples(self):
        print_info('[*] Loading samples...')
        for path in self.paths:
            sample = Sample(path)
            self.samples[sample.md5] = {'path': sample.path, 'ssdeep': ssdeep.hash(open(sample.path, 'rb').read())}

    def populate_clusters(self):
        i = 0
        print_info('[*] Starting to cluster...')
        for md5_outer, metadata_outer in self.samples.iteritems():
            for md5_inner, metadata_inner in self.samples.iteritems():
                if md5_inner == md5_outer:
                    continue
                score = ssdeep.compare(metadata_inner['ssdeep'], metadata_outer['ssdeep'])
                if score > self.threshold:
                    print_info('[*] %s and %s are similar:     %s' % (md5_outer, md5_inner, score))
                    all_md5s = [md5 for md5_sublist in self.clusters.itervalues() for md5 in md5_sublist]
                    if not md5_inner in all_md5s and not md5_outer in all_md5s:
                        self.clusters[i] = [md5_inner, md5_outer]
                        i += 1
                        continue
                    for cluster, md5s in self.clusters.iteritems():
                        if md5_inner in md5s and md5_outer in md5s:
                            break
                        if md5_inner in md5s and not md5_outer in md5s:
                            self.clusters[cluster].append(md5_outer)
                            break
                        if md5_outer in md5s and not md5_inner in md5s:
                            self.clusters[cluster].append(md5_inner)
                            break

    def group_on_disk(self, output):
        for cluster, md5s in self.clusters.iteritems():
            self.write_to_disk(cluster, md5s, self.samples, output)

    @staticmethod
    def write_to_disk(cluster, md5s, samples_metadata, output):
        output_dir = '%s/%s' % (os.path.abspath(output), cluster)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except os.error:
                print_info('[*] Encountered an error creating directory %s' % output_dir)
                return
        for md5 in md5s:
            try:
                copy2(samples_metadata[md5]['path'], output_dir)
            except (IOError, os.error):
                print_info('[*] Encountered an error copying %s to %s' % (samples_metadata[md5]['path'], output_dir))
                return


class Sample(object):
    def __init__(self, path):
        self.path = path

    @property
    def md5(self):
        hash_md5 = hashlib.md5()
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
            return hash_md5.hexdigest()


def print_info(info):
    if 'args' in globals() and args.verbose:
        print info

def get_input(input_paths):
    if len(input_paths) == 1 and os.path.isdir(input_paths[0]):
        return glob('%s/*' % input_paths[0])
    return input_paths


if __name__ == '__main__':
    start = timer()
    parser = ArgumentParser(prog=__file__, description='simple file clustering using ssdeep')
    parser.add_argument('input', nargs='+', type=str, help='input path')
    parser.add_argument('-o', '--output', nargs='?', type=str, help='output path')
    parser.add_argument('-v', '--verbose', action='count', help='increase output verbosity')
    parser.add_argument('-t', '--threshold', nargs='?', type=int, help='specify minimum ssdeep distance threshold in range 0 to 100. Default 60')
    args = parser.parse_args()

    if not os.path.exists(args.input[0]):
        print '[*] Unable to open input path'
        sys.exit(1)

    if not args.threshold or args.threshold > 100:
        args.threshold = 60

    paths = get_input(args.input)

    c = Clusters(paths, args.threshold)

    if args.output:
        c.group_on_disk(args.output)

    print json.dumps(dict(c.clusters), sort_keys=True, indent=4)
    print_info('[*] Completed in %s s' % (timer() - start))
