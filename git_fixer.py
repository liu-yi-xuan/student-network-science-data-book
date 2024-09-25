import os
import time
import glob
import sys

os.system('git fetch upstream && git diff main upstream/main > diff.diff')
# check for differences between upstream (Alyssa's main repo) and your own forked version
# writes the git diff to a file called diff.diff.

# looks at each file diff that git raises and appends it to its own block
with open("diff.diff", 'r') as f:
    block = []
    blocks = []
    for line in f.readlines():
        if line.startswith('diff --git'):
            if len(block) != 0:
                blocks.append(block)
                block = []
        block.append(line)
    blocks.append(block)

# ignore if it's a new file (no conflicts will occur)
# if it's an existing file, we need to deal with it.
fnames_to_ignore = []
fnames_to_move = []
for b in blocks:
    if len(b[0]) < 12:
        print('no diffs exist - try committing changes if changes are present!')
        sys.exit()
    fname = b[0][12:].split()[0]
    if b[1].startswith('new file mode '):
        fnames_to_ignore.append(fname)
    else:
        fnames_to_move.append(fname)

# for modified files, we create a new copy of the modified file and change its name so git doesn't overwrite it
# with the old ("clean") version from Alyssa's main repo.
fname_wildcards = []
for fname in fnames_to_move:
    fname_extension = fname.split('.')[-1]
    fname_prefix = '.'.join(fname.split('.')[:-1])
    fname_wildcards.append(fname_prefix + '_MODIFIED_*.' + fname_extension)
    new_fname = fname_prefix + '_MODIFIED_{}'.format(str(time.time()).split('.')[0]) + '.' + fname_extension
    os.system('cp {} {}'.format(fname[1:], new_fname[1:]))

# pulls down the code from Alyssa's repo and integrates any new updates.
# you will have clean versions of any modified files in addition to the copies you modified.
os.system('git checkout main')
os.system('git merge upstream/main')

# clean up old modified files that match each other
for wildcard in fname_wildcards:
    print(wildcard)
    keepers = []
    fnames_from_most_recent = sorted([f for f in glob.glob(wildcard[1:])])
    print(fnames_from_most_recent)
    for idx in range(1, len(fnames_from_most_recent)):
        # use cmp command to check for even single-byte differences between any two files that match a wildcard.
        os.system('cmp --silent -- {} {} > mod.txt'.format(
            fnames_from_most_recent[0], 
            fnames_from_most_recent[idx],
        ))
        with open('mod.txt', 'r') as f:
            bytes_diff = ''
            for line in f.readlines():
                bytes_diff.append(line)
            print(len(bytes_diff))
        if len(bytes_diff) == 0:
            os.system('rm {}'.format(fnames_from_most_recent[idx]))
        
                  
        
    
    

