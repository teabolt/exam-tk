#!/usr/bin/env python3

"""Tests for the PDF page slicer"""


import unittest
import sys
import os
import os.path
import datetime

sys.path.append('../src')
import slicer

from _io import BufferedReader
import PyPDF2 as pypdf


# modify this to alter the path where test data is read from / saved to
tests_data = {
    'input': '../../tests_data/input',
    'output': '../../tests_data/output',
}


class TestPageSlicer(unittest.TestCase):

    def setUp(self):
        global tests_data
        # common variables reused across functions
        self.pathin = tests_data['input']
        self.pathout = tests_data['output']

    def test_load_files(self):
        # set-up
        pdf_no = len([filename for filename in os.listdir(self.pathin) if os.path.splitext(filename)[1] == '.pdf'])
        pdfsin = slicer.load_files(self.pathin, loud=False)
        # test
        self.assertIsInstance(pdfsin, list) # right output type
        [self.assertIsInstance(f, BufferedReader) for f in pdfsin] # it's files
        [self.assertEqual(f.mode, 'rb') for f in pdfsin] # right modes (read and write)
        self.assertEqual(len(pdfsin), pdf_no) # all counted PDF's open
        [self.assertEqual(os.path.splitext(f.name)[1], '.pdf') for f in pdfsin] # only PDF's open
        # tear-down
        [f.close() for f in pdfsin]

    def test_page_repr(self):
        self.assertIsInstance(slicer.page_repr('1'), pypdf.PageRange) # correct return typr
        self.assertEqual(slicer.page_repr('1:-2:2').indices(10), (1, 8, 2)) # underlying PageObject works

    def test_merge(self):
        # assuming 'test_load' is correct and has populated 'self.pdfsin'
        # set-up
        pdfsin = [open(os.path.join(self.pathin, filename), 'rb') for filename in os.listdir(self.pathin)]
        mergers = [slicer.merge(pdfsin, pypdf.PageRange(pg), loud=False) for pg in ['1', '3', '20']]
        # test
        self.assertIsInstance(mergers[0], pypdf.PdfFileMerger)
        # (based on specific test data)
        self.assertEqual(len(mergers[0].pages), len(pdfsin)) # all pages gotten
        self.assertEqual(len(mergers[1].pages), 5) # PDF's with not enough pages ignored
        self.assertEqual(len(mergers[2].pages), 0) # none have enough pages
        # tear-down
        [f.close() for f in pdfsin]
        [merger.close() for merger in mergers]

    def test_save(self):
        # set-up (same as 'test_merge'???)
        pdfsin = [open(os.path.join(self.pathin, filename), 'rb') for filename in os.listdir(self.pathin)]
        merger = slicer.merge(pdfsin, pypdf.PageRange('1'), loud=False)
        path = os.path.join(self.pathout, 'test_save_{}.pdf'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        # test
        save = slicer.save(merger, path, loud=False)
        self.assertIsInstance(save, type(None)) # returns None
        self.assertTrue(os.path.isfile(path)) # created file
        with open(path, 'rb') as f:
            # (assuming single page slices)
            self.assertEqual(pypdf.PdfFileReader(f).getNumPages(), len(pdfsin)) # correct number of pages
        # tear-down
        [f.close() for f in pdfsin]
        merger.close()

    def test_cli_engine(self):
        pgs = pypdf.PageRange('1')
        pathout = os.path.join(self.pathout, 'test_cli_engine_{}.pdf'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
        result = slicer.cli_engine([self.pathin, pgs, pathout])
        self.assertIsInstance(result, type(None))

    def test_watermark(self):
        pass


if __name__ == '__main__':
    unittest.main()