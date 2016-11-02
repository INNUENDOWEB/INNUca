#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
getSeqENA.py - Get fastq files from ENA using Run IDs
<https://github.com/miguelpmachado/manipulateFasta/>

Copyright (C) 2016 Miguel Machado <mpmachado@medicina.ulisboa.pt>

Last modified: July 22, 2016

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details at <http://www.gnu.org/licenses/>.
"""

import argparse
import os
import sys
import time

version = '0.1'


def combine_reports(args):
	innucaOut = os.path.abspath(args.innucaOut)
	outdir = os.path.abspath(args.outdir)
	check_create_directory(outdir)

	files = [f for f in os.listdir(innucaOut) if not f.startswith('.') and os.path.isfile(os.path.join(innucaOut, f))]
	samples_report = []
	for file_found in files:
		file_found = os.path.join(innucaOut, file_found)
		if os.path.basename(file_found).startswith('samples_report'):
			samples_report.append(file_found)
	if len(samples_report) == 0:
		samples_report = None
	elif len(samples_report) == 1:
		samples_report = samples_report[0]
	else:
		samples_report = sorted(samples_report, reverse=True)[0]

	directories = [d for d in os.listdir(innucaOut) if not d.startswith('.') and os.path.isdir(os.path.join(innucaOut, d, ''))]

	results = {}

	if len(directories) == 0:
		sys.exit('No samples found')

	# files_to_search = ['coverage_report.txt', 'spades_report.txt', 'pilon_report.txt', 'assembly_coverage_report.txt', 'assembly_mapping_report.txt', 'mlst_report.txt']

	fields = ['#samples', 'first_coverage', 'second_Coverage', 'SPAdes_number_contigs', 'SPAdes_number_bp', 'SPAdes_filtered_contigs', 'SPAdes_filtered_bp', 'Pilon_changes', 'Pilon_contigs_changed', 'assembly_coverage', 'mapped_reads_percentage', 'mapping_filtered_contigs', 'mapping_filtered_bp', 'MLST_scheme', 'MLST_ST', 'final_assembly']

	for directory in directories:
		sample = directory
		print '\n' + sample
		directory = os.path.join(os.path.join(innucaOut, directory, ''))

		files = [f for f in os.listdir(directory) if not f.startswith('.') and os.path.isfile(os.path.join(directory, f))]
		if len(files) == 0:
			print 'No files found! Continue to the next sample'
		else:
			# results[sample] = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']
			results[sample] = {}
			for field in fields:
				results[sample][field] = 'NA'

			results[sample]['#samples'] = sample

			for file_found in files:
				name_file_found = file_found
				file_found = os.path.join(directory, file_found)

				if name_file_found == 'coverage_report.txt':
					data = []
					with open(file_found, 'rtU') as reader:
						for line in reader:
							if len(line) > 0:
								line = line.splitlines()[0].rsplit('x')[0]
								data.append(line)
					if len(data) == 2:
						results[sample]['first_coverage'] = data[0]
						results[sample]['second_Coverage'] = data[1]
					elif len(data) == 1:
						if samples_report is not None:
							with open(samples_report, 'rtU') as reader:
								header = None
								for line in reader:
									line = line.splitlines()[0]
									if len(line) > 0:
										line = line.split('\t')

										if line[0].startswith('#'):
											header = line

										if line[0] in sample:
											if line[header.index("first_Coverage_runSuccessfully")] == 'True':
												results[sample]['first_coverage'] = data[0]
											elif line[header.index("second_Coverage_runSuccessfully")] == 'True':
												results[sample]['second_Coverage'] = data[0]
				elif name_file_found.startswith('spades_report.original.'):
					general = False

					contigs = False
					bp = False
					with open(file_found, 'rtU') as reader:
						for line in reader:
							if len(line) > 0:
								line = line.splitlines()[0].split(' ')[0]
								if line.startswith('#'):
									if line.startswith('general', 1):
										general = True
									else:
										general = False
								elif line.startswith('>') and general:
									if line.startswith('contigs', 1):
										contigs = True
									elif line.startswith('bp', 1):
										bp = True
								else:
									if contigs:
										results[sample]['SPAdes_number_contigs'] = line
										contigs = False
									if bp:
										results[sample]['SPAdes_number_bp'] = line
										bp = False
				elif name_file_found.startswith('spades_report.filtered.'):
					general = False

					contigs = False
					bp = False
					with open(file_found, 'rtU') as reader:
						for line in reader:
							if len(line) > 0:
								line = line.splitlines()[0].split(' ')[0]
								if line.startswith('#'):
									if line.startswith('general', 1):
										general = True
									else:
										general = False
								elif line.startswith('>') and general:
									if line.startswith('contigs', 1):
										contigs = True
									elif line.startswith('bp', 1):
										bp = True
								else:
									if contigs:
										results[sample]['SPAdes_filtered_contigs'] = line
										contigs = False
									if bp:
										results[sample]['SPAdes_filtered_bp'] = line
										bp = False
				elif name_file_found == 'pilon_report.txt':
					general = False

					changes = False
					contigs = False
					with open(file_found, 'rtU') as reader:
						for line in reader:
							if len(line) > 0:
								line = line.splitlines()[0]
								if line != '#by_contigs':
									if line.startswith('#'):
										if line.startswith('general', 1):
											general = True
										else:
											general = False
									elif line.startswith('>') and general:
										if line.startswith('changes', 1):
											changes = True
										elif line.startswith('contigs', 1):
											contigs = True
									else:
										if changes:
											results[sample]['Pilon_changes'] = line
											changes = False
										if contigs:
											results[sample]['Pilon_contigs_changed'] = line
											contigs = False
								else:
									break
				elif name_file_found == 'assembly_mapping_report.coverage.txt':
					coverage = False
					with open(file_found, 'rtU') as reader:
						for line in reader:
							line = line.splitlines()[0]
							if len(line) > 0:
								if line.startswith('#general'):
									coverage = True
								else:
									if coverage:
										results[sample]['assembly_coverage'] = line
										coverage = False
				elif name_file_found == 'assembly_mapping_report.mapping.txt':
					total = False
					total_reads = 0
					mapped = False
					mapped_reads = 0
					with open(file_found, 'rtU') as reader:
						for line in reader:
							line = line.splitlines()[0].split(' ')[0]
							if len(line) > 0:
								if line.startswith('#'):
									total = False
									mapped = False
									if line.startswith('in_total', 1):
										total = True
									elif line.startswith('mapped', 1):
										mapped = True
								elif line.startswith('>'):
									continue
								else:
									if total:
										total_reads = int(line)
										total = False
									elif mapped:
										mapped_reads = int(line)
										mapped = False
					results[sample]['mapped_reads_percentage'] = str(round((float(mapped_reads) / float(total_reads)), 2) * 100)
				elif name_file_found.startswith('assembly_mapping_report.sequences_filtered.'):
					general = False

					contigs = False
					bp = False
					with open(file_found, 'rtU') as reader:
						for line in reader:
							line = line.splitlines()[0]
							if len(line) > 0:
								if line.startswith('#'):
									if line.startswith('general', 1):
										general = True
									else:
										general = False
								elif line.startswith('>') and general:
									if line.startswith('contigs', 1):
										contigs = True
									elif line.startswith('bp', 1):
										bp = True
								else:
									if contigs:
										results[sample]['mapping_filtered_contigs'] = line
										contigs = False
									if bp:
										results[sample]['mapping_filtered_bp'] = line
										bp = False
				elif name_file_found == 'mlst_report.txt':
					species = False
					st = False
					with open(file_found, 'rtU') as reader:
						for line in reader:
							line = line.splitlines()[0]
							if len(line) > 0:
								if line.startswith('#'):
									if line.startswith('scheme', 1):
										species = True
									elif line.startswith('ST', 1):
										st = True
								else:
									if species:
										results[sample]['MLST_scheme'] = line
										species = False
									if st:
										results[sample]['MLST_ST'] = line
										st = False
				elif name_file_found == 'final_assembly.txt':
					with open(file_found, 'rtU') as reader:
						for line in reader:
							line = line.splitlines()[0]
							if len(line) > 0:
								results[sample]['final_assembly'] = line

	if len(results) == 0:
		sys.exit('No results were found')

	print '\n' + 'Writing results...'
	with open(os.path.join(outdir, str('combine_samples_report.' + time.strftime("%Y%m%d-%H%M%S") + '.tab')), 'wt') as report:
		report.write('\t'.join(fields) + '\n')
		for sample in results:
			sample_data = [results[sample][field] for field in fields]
			report.write('\t'.join(sample_data) + '\n')

	print '\n' + 'DONE: ' + str(len(results)) + ' samples analysed.'


def check_create_directory(directory):
	if not os.path.isdir(directory):
		os.makedirs(directory)


def main():

	parser = argparse.ArgumentParser(prog='python combine_reports.py', description="Combine INNUca reports (Coverage, SPAdes, Pilon, MLST)", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--version', help='Version information', action='version', version=str('%(prog)s v' + version))

	parser_required = parser.add_argument_group('Required options')
	parser_required.add_argument('-i', '--innucaOut', type=str, metavar='/path/to/INNUca/output/directory/', help='Path to INNUca output directory', required=True)

	parser_optional = parser.add_argument_group('Facultative options')
	parser_optional.add_argument('-o', '--outdir', type=str, metavar='/path/to/output/directory/', help='Path to where to store the outputs', required=False, default='.')

	parser.set_defaults(func=combine_reports)

	args = parser.parse_args()

	args.func(args)


if __name__ == "__main__":
	main()
