#!/usr/bin/env python3

"""Operations on batches of PDF's that return a single 'sliced' PDF
Examples of operations include taking a certain page from each PDF, etc"""


import sys
import os.path
import datetime
import tempfile

import PyPDF2 as pypdf


def load_files(directory, loud=True):
    """Return a list of open file objects"""
    if loud:
        print('Loading...')
    orig = os.getcwd()
    os.chdir(directory)
    pdfs = []
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1] != '.pdf':
            print('{} from its extension appears not to be a PDF file... skipping'.format(filename))
            continue
        else:
            pdfs.append(open(filename, 'rb'))
    os.chdir(orig)
    return pdfs


def load_paths(directory, loud=True):
    """Return a list of absolute paths to files"""
    if loud:
        print('Loading...')
    directory = os.path.abspath(directory)
    return [os.path.join(directory, filename) for filename in os.listdir(directory) if os.path.splitext(filename)[1] == '.pdf']


def parse_cyear(path):
    return int(os.path.basename(path)[:2])


def sort_cyear(paths, most_recent=True):
    """Sort a list of paths (strings) that contain two digit years without century, eg: 18, 99, 58,
    , extractable by 'parse_cyear' function.
    The years greater than the current year are assumed to be of the 20th century, eg: 99 -> 1999
    and years lesser than the current year are assumed to be of 21st century, eg: 15 -> 2015"""
    paths_set = set(paths)
    this_year = int(str(datetime.datetime.now().year)[-2:]) # eg: 18
    last_century = set([path for path in paths if this_year < parse_cyear(path)]) # eg: 18 < 99
    this_century = paths_set - last_century # set difference
    if most_recent:
        print('here1')
        return sorted(list(this_century), reverse=True) + sorted(list(last_century), reverse=True)
    else:
        print('here2')
        return sorted(list(last_century)) + sorted(list(this_century))


def page_repr(pages):
    return pypdf.PageRange(pages)


def merge(pdfs, page_nrs, loud=True):
    if loud:
        print('Processing...')
    merger = pypdf.PdfFileMerger()
    for (i, pdf) in enumerate(pdfs):
        if loud:
            print('Processing {}: {}...'.format(i+1, pdf))
        try:
            merger.append(pdf, pages=page_nrs)
        except Exception as exc:
            if loud:
                print('Exception: {}'.format(exc))
                print('skipping...')
    return merger
    

##  Alternate solutions down below


def get_batch(a, n):
    """Split a list into multiple sub-lists"""
    return [a[i:i+n] for i in range(0, len(a), n)]


def merge_tmp(pdfs, page_nrs, batch_size=10):
    print('Processing...')
    """Merge with temporary stops in-between"""
    # traverse indices in steps of batch_size, chunking the list of pdfs
    pdf_batches = get_batch(pdfs, batch_size)
    # print([[os.path.basename(pdf) for pdf in batch] for batch in pdf_batches])
    # 1st batch
    merger = merge(pdf_batches[0], page_nrs)
    tmp = tempfile.TemporaryFile()
    merger.write(tmp)
    for batch in pdf_batches[1:]:
        tmp.seek(0)
        batch.insert(0, tmp)
        merger = merge(batch, page_nrs)
        tmp.truncate()
        merger.write(tmp) # on last iteration this step is not needed
    tmp.close()
    return merger


def merge_multi(pdfs, page_nrs, batch_size=10):
    print('Processing...')
    pdf_batches = get_batch(pdfs, batch_size)
    mergers = []
    merger = merge(pdf_batches[0], page_nrs)
    mergers.append(merger)
    for batch in pdf_batches[1:]:
        merger = merge(batch, page_nrs)
        mergers.append(merger)
    return mergers


def merge_save(pdfs, page_nrs, pathout, batch_size=10):
    print('Processing...')
    pdf_batches = get_batch(pdfs, batch_size)
    merger = merge(pdf_batches[0], page_nrs)
    i = 0
    save(merger, pathname_append(pathout, '-'+str(i)))
    close(merger)
    for batch in pdf_batches[1:]:
        merger = merge(batch, page_nrs)
        i += 1
        save(merger, pathname_append(pathout, '-'+str(i)))
        close(merger)


def save(merger, path, loud=True):
    if loud:
        print('Saving...')
    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    with open(path, 'wb') as f_out:
        merger.write(path)


def save_multiple(mergers, path):
    print('Saving...')
    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    for (i, merger) in enumerate(mergers):
        fpath = pathname_append(path, '-'+str(i))
        with open(fpath, 'wb') as f_out:
            merger.write(path)


def pathname_append(path, s):
    """Append 's' to the end of a path (of a file), but before the path filename's extension"""
    directory = os.path.dirname(path)
    filename, extension = os.path.splitext(os.path.basename(path))
    new_path = os.path.join(directory, filename+s+extension)
    return new_path


def close(merger, files=None, loud=True):
    if loud:
        print('Closing...')
    merger.close()
    if files != None:
        for file in files:
            file.close()


def close_multiple(mergers):
    for merger in mergers:
        merger.close()


def cli_engine(args):
    pdfpath, pages, pathout = args
    pdf_paths = load_paths(pdfpath)
    pdf_paths = sort_cyear(pdf_paths) # sort to get the most recent papers first
    pg = page_repr(pages)

    # single output file
    merger = merge(pdf_paths, pg)
    save(merger, pathout)
    close(merger)

    # with temporary files (incremental)
    # merger = merge_tmp(pdf_paths, pg, 10)
    # save(merger, pathout)
    # close(merger)

    # batched
    # mergers = merge_mult(pdf_paths, pg, 10)
    # save_multiple(mergers, pathout)
    # close_multiple(mergers)

    # merge-save (batches)
    # merge_save(pdf_paths, pg, pathout)


def main():
    args = sys.argv[1:]
    cli_engine(args)


if __name__ == '__main__':
    main()