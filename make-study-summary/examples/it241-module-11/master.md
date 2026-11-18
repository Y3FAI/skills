## 1. Files
### Key terms
- **File**: A contiguous logical address space, with contents defined by its creator; a logical storage unit and collection of related information.
- **Name**: The only file attribute kept in human-readable form.
- **Identifier**: A unique tag (number) identifying the file within the file system.
- **Location**: A pointer to the file's location on the device.
- **Protection**: The attribute that controls who can read, write and execute the file.
- **Extended file attributes**: Extra metadata beyond the standard attributes, such as a file checksum or the character encoding.
- **Shared lock**: A file lock several processes can hold at the same time, like a reader lock.
- **Exclusive lock**: A file lock only one process can hold, like a writer lock.
- **Mandatory locking**: Locking where access is denied depending on the locks held and requested.
- **Advisory locking**: Locking where processes can find the status of locks and decide what to do.
- **Extension**: The part of a file name that tells its type, as in app.exe.
- **Object file**: A compiled, machine-language file that is not linked (obj, o).
- **Executable file**: A ready-to-run machine-language program (exe, com, bin or none).
- **Batch file**: A file of commands to the command interpreter (bat, sh).
- **Library file**: Libraries of routines for programmers (lib, a, so, dll).
- **Archive file**: Related files grouped into one file, sometimes compressed (arc, zip, tar).
### Rules
- **What are the two main types of files?** Data (numeric, character, binary) and program.
- **File locks are similar to which locks?** Reader-writer locks, provided by some operating systems and file systems.
- **Why are file extensions useful?** They show the file's type, so the system opens it with the right program.
### Written questions
**Q. List the file attributes.**
- Name: the only human-readable information.
- Identifier: a unique number within the file system.
- Type.
- Location: a pointer to the file on the device.
- Size.
- Protection: who can read, write, execute.
- Time, date and user identification.
**Q. List the six basic file operations, plus the two added for efficiency.**
- The six basic operations are create, write, read, reposition (seek), delete and truncate.
- Open and close are added so the directory is not searched on every access.
**Q. What do the open and close operations do?**
- Open searches the directory on disk for the entry and moves the entry to memory, so later reads and writes do not search the disk again.
- Close moves the entry from memory back to the directory structure on disk.
**Q. Compare shared and exclusive locks.**
- Shared: like a reader lock; several processes can hold it at once.
- Exclusive: like a writer lock; only one process can hold it.
**Q. Compare mandatory and advisory locking.**
- Mandatory: the OS denies access depending on the locks held and requested.
- Advisory: processes check the lock status and decide what to do themselves.
**Q. Differentiate between truncate and delete.**
- Truncate: erases the contents but keeps the file and its attributes.
- Delete: removes the file and frees its space.
**Q. Differentiate between an object file and an executable file.**
- Object: compiled machine language, not linked.
- Executable: a ready-to-run machine-language program.
### Traps
- **How does the OS handle access in advisory locking?** In advisory locking the processes decide; the OS denies access only in mandatory locking.
- **What does the open operation move to memory?** It moves the directory entry to memory (close moves it back to disk), without reading the file's data.
## 2. Access methods
### Key terms
- **Sequential access**: Access where records are processed in order (read next, write next, reset; no read after the last write, which is a rewrite). It is the simplest and most common access method.
- **Direct (relative) access**: Access in no particular order, using a relative block number counted from the start of the file (read n, write n, position to n, read next, write next, rewrite n).
- **ISAM (indexed sequential-access method)**: IBM's method where a small master index points to disk blocks of a secondary index, and the file is kept sorted on a key.
- **In-memory index**: An index of the disk index, kept in memory when the disk index is too large.
- **VMS index file**: Lists each key (such as a last name) with its logical record number.
- **VMS relative file**: Holds the records, read directly by that logical record number.
### Rules
- **For access methods, what is a file made of?** Fixed-length logical records.
- **In sequential access, what does "no read after last write" mean?** A write becomes the new end of the file.
- **How is sequential access simulated on a direct-access file?** Keep a current position cp: reset is cp = 0; read next is read cp, then cp = cp + 1.
- **What do other access methods built on the base methods generally involve?** Creating an index for the file, kept in memory for fast lookup.
- **In ISAM, who does the indexing work?** The OS (all done by the OS).
### Written questions
**Q. Differentiate between sequential and direct access.**
- Sequential: records in order, one after another (read next, write next, reset; no read after the last write). Simplest and most common.
- Direct: records in no particular order, by relative block number (read n, write n, position to n, rewrite n).
## 3. Disks, volumes and many file systems
### Key terms
- **Partition**: a subdivision of a disk, also called a minidisk or a slice.
- **Volume**: The entity containing a file system.
- **Device directory (volume table of contents)**: Where a volume tracks its file system's information.
- **Raw partition**: A disk or partition used without a file system; its blocks are used directly.
- **Formatted (cooked) partition**: A disk or partition that holds a file system, used through files and directories.
- **tmpfs**: Solaris memory-based volatile file system for fast, temporary I/O.
- **★ objfs**: Solaris interface into kernel memory to get kernel symbols for debugging.
- **ctfs**: Solaris contract file system for managing daemons.
- **lofs**: Solaris loopback file system that lets one file system be accessed in place of another.
- **procfs**: Solaris kernel interface to process structures.
- **ufs and zfs**: The Solaris general-purpose file systems.
### Rules
- **How are disks or partitions protected against failure?** With RAID.
- **What can a volume be?** Part of a disk, a whole disk, or several disks: whatever holds a file system.
- **What is the file system format of a CD-ROM?** ISO 9660.
- **What are the formats of UNIX?** UFS and FFS.
- **What are the formats of Windows?** FAT, FAT32 and NTFS.
- **What are the leading formats of Linux?** ext3 and ext4 (out of more than 130 types).
- **What are some newer formats still arriving?** ZFS, GoogleFS, Oracle ASM and FUSE.
### Written questions
**Q. Differentiate between a raw and a formatted partition.**
- Raw: no file system; its blocks are used directly.
- Formatted: holds a file system, used through files and directories.
### Traps
- **Which Solaris file systems are general-purpose?** Only ufs and zfs (tmpfs is memory-based and volatile).
## 4. Directories
### Key terms
- **Directory structure**: A collection of nodes containing information about all files (names, locations), used to locate them.
- **Single-level directory**: A single directory for all users.
- **★ Two-level directory**: Directory organization with a separate directory for each user. A file is named by a path name (user name plus file name, such as /user1/test).
- **Tree-structured directory**: Directories that hold files and subdirectories under one root, with one path per file.
- **Acyclic-graph directory**: Directories that have shared subdirectories and files, with no cycles.
- **General graph directory**: Directories where links can point anywhere, so cycles are possible.
- **Aliasing**: One file having two different names.
- **Dangling pointer**: A directory entry left pointing at a file that was deleted.
- **Link**: Another name (pointer) to an existing file.
- **Resolving the link**: Following a link's pointer to locate the file.
- **Entry-hold count**: A count of the entries pointing to a file; the file is deleted only when it reaches 0.
- **Garbage collection**: Finding and freeing files that can no longer be reached, when cycles exist.
- **Current (working) directory**: The directory where files are created and deleted, set with cd.
### Rules
- **Where is information about files kept?** In the directory structure, on disk.
- **Where do the directory structure and the files reside?** Both on disk.
- **Which problem does a two-level directory fix, and which does it leave?** Fixes naming (same name for different users); leaves grouping (no grouping capability).
- **Why is searching efficient in a two-level directory?** Only the user's own directory is searched.
- **What does a tree-structured directory add, and what does it lack?** Adds grouping (subdirectories); lacks sharing.
- **What does an acyclic graph add, and what problems come with it?** Adds sharing; brings aliasing and dangling pointers.
- **Deleting the directory "mail" deletes what?** The entire subtree rooted at mail.
- **What command creates a new subdirectory in the current directory?** mkdir dir-name.
### Written questions
**Q. ★ What is the difference between a file and a directory?**
- File: a collection of related information; it holds the data.
- Directory: a collection of nodes with information about files (names, locations); it is used to locate them.
**Q. List the operations performed on a directory.**
- Search for a file
- Create a file
- Delete a file
- List a directory
- Rename a file
- Traverse the file system
**Q. What three goals is a directory organized to obtain?**
- Efficiency: locating a file quickly.
- Naming: convenient to users (two users can have the same name for different files; one file can have several names).
- Grouping: logical grouping of files by properties.
**Q. What is a dangling pointer and what are its solutions?**
- A directory entry that still points to a file after the file was deleted through another name.
- Solutions: backpointers; backpointers in a daisy-chain organization; an entry-hold count.
**Q. What are backpointers and daisy chains?**
- Backpointers: each file keeps a list of every directory entry that points to it, but this makes the file's record variable size.
- Daisy chain: the entries pointing to the same file are chained together.
**Q. How can a general graph directory prevent cycles from being created?**
- Allow only links to files, not to subdirectories.
- Run a cycle detection algorithm every time a new link is added.
**Q. How does a general graph directory handle existing cycles?**
- Garbage collection runs to find and free space for files that can no longer be reached.
**Q. What are the two problems of a single-level directory?**
- Naming problem: every file of every user needs a unique name.
- Grouping problem: files cannot be grouped.
**Q. Compare the single-level and the two-level directory.**
- Single-level: one directory for all users; naming and grouping problems.
- Two-level: a separate directory for each user; same name for different users and efficient searching, but no grouping.
**Q. Compare the tree-structured and the acyclic-graph directory.**
- Tree: each file has one path; grouping, but no sharing.
- Acyclic graph: shared subdirectories and files; sharing, but aliasing and dangling pointers.
## 5. Protection
### Key terms
- **Access-control list (ACL)**: A list attached to a file of users and groups with the access each one is allowed (Allow or Deny in Windows).
### Rules
- **What is the most common protection approach?** Making access depend on the user's identity.
- **What should a file's owner be able to control?** What can be done, and by whom.
- **What does the UNIX command chgrp G game do?** Attaches group G to the file game.
- **In a Windows ACL, what can each permission be set to?** Allow or Deny, for each user or group.
### Written questions
**Q. List the types of access a file owner can control.**
- Read
- Write
- Execute
- Append
- Delete
- List
**Q. Name the three classes of users in UNIX file protection.**
- Owner, group, public (public is also called universe).
- Each class has read, write and execute (r, w, x) bits.
### Calculations
**Q. UNIX: what does chmod 761 game give each class?**
- Bits are r = 4, w = 2, x = 1.
- Owner 7 = 4 + 2 + 1 = rwx. Group 6 = 4 + 2 = rw-. Public 1 = --x.
- Answer: owner rwx, group rw-, public --x.
**Q. UNIX: write rwxr-x--- as a number.**
- rwx = 7, r-x = 4 + 1 = 5, --- = 0.
- Answer: 750.
## 6. File-system structure
### Key terms
- **★ File control block (FCB)**: A storage structure consisting of information about a file. In UNIX it is called an inode.
- **Sector**: Usually 512 bytes.
- **Block**: Made of sectors, it is the unit of transfer between memory and disk.
- **Device driver**: What controls the physical device in the I/O control layer.
- **I/O control layer**: The layer where device drivers turn commands into low-level hardware commands for the controller.
- **Basic file system layer**: The layer given commands like "retrieve block 123", which also manages buffers and caches.
- **★ File-organization module**: The layer that translates logical block numbers to physical block numbers and manages free space.
- **Logical file system layer**: The layer that translates a file name into the file's number, handle and location through the FCB. It manages metadata, keeps the FCBs, and handles directory management and protection.
### Rules
- **Which two disk properties suit file systems?** In-place rewrite and random access.
- **What does an FCB typically hold?** Inode number, permissions, dates, owner/group/ACL, size, and pointers to the data blocks.
- **What is the benefit and cost of layering?** Reduces complexity and redundancy; adds overhead and can decrease performance.
### Written questions
**Q. ★ What is the purpose of a file system?**
- To organize and manage data storage on secondary storage (disks).
- It gives users an interface to storage, mapping logical to physical with efficient, convenient access.
- It allows data to be stored, located and retrieved easily.
**Q. List the layers of a layered file system, from lowest to highest.**
- Devices
- I/O control (device drivers)
- Basic file system
- File-organization module
- Logical file system
- Application programs
**Q. What does each file-system layer do?**
- I/O control: device drivers turn commands into low-level hardware commands for the controller.
- Basic file system: handles "retrieve block 123"; manages buffers and caches.
- File-organization module: translates logical to physical block numbers; manages free space and allocation.
- Logical file system: manages metadata and FCBs; directory management and protection.
**Q. What is a file control block (FCB)? Name three things it holds.**
- A storage structure with the information about one file (the inode in UNIX).
- Permissions; size; pointers to the file's data blocks. (Also dates, owner, group, ACL.)
### Traps
- **Where is the file's name kept?** In the directory entry, not in the FCB (which holds everything else).
- **What is the unit of transfer between memory and disk?** A block (made of sectors), while a sector is usually 512 bytes.
- **Which layer translates logical to physical blocks: the basic file system or the file-organization module?** The file-organization module. The basic file system handles "retrieve block 123" and the buffers.
- **Which layer translates a file name into an FCB?** The logical file system.
- **What is the effect of layering on overhead?** It adds overhead (while reducing complexity and redundancy).
## 7. Implementation structures
### Key terms
- **Boot control block**: On disk, info needed to boot the OS from the volume, usually its first block.
- **Volume control block**: On disk, volume details (total blocks, free blocks, block size, free-block pointers). UNIX calls it the superblock; NTFS keeps both the volume details and the directory structure in the master file table.
- **Mount table**: In memory, the file-system mounts, mount points and file-system types.
- **★ Mounting**: Attaching a file system to the directory structure at a mount point, so its files appear there.
- **System-wide open-file table**: In memory, a copy of the FCB of each open file, with an open count of the processes using it.
- **Per-process open-file table**: In memory, for each process, pointers to entries in the system-wide open-file table.
- **Directory-structure cache**: In memory, recently used directories.
- **Buffers**: In memory, hold file-system blocks in transit.
- **Caches**: In memory, hold frequently used data.
- **Linear list directory**: A directory implementation using a list of file names with pointers to the data blocks.
- **Hash table directory**: A directory implementation that decreases search time by hashing the file name.
- **Collision**: Two file names hashing to the same location.
- **Chained overflow**: Each hash slot keeps a linked list of the entries that hash there.
### Rules
- **When is a boot control block needed?** When the volume contains an OS.
- **What is the advantage and drawback of a linear-list directory?** Simple to program; time-consuming to execute (linear search time).
- **How can a linear-list directory be searched faster?** Keep it ordered alphabetically (linked list) or use a B+ tree.
- **When is a hash-table directory a good choice?** Only if entries are fixed size, or with chained overflow.
### Written questions
**Q. How does the open-file table handle shared files?**
- A shared file has one entry in the system-wide open-file table (with an open count).
- Each process that opened it has one entry in its per-process open-file table pointing to the system-wide entry.
- Example: process A has 2 files open, process B has 3, and 2 files are shared. A's table has 2 entries, B's has 3, the system-wide table has 3.
**Q. Name three on-disk structures used to implement a file system.**
- Boot control block: info to boot the OS from the volume.
- Volume control block: volume details (total blocks, free blocks, block size, free-block pointers).
- Directory structure: file names and inode numbers.
**Q. Name three in-memory file-system structures.**
- Mount table: mounts, mount points, file-system types.
- System-wide open-file table: a copy of the FCB of each open file.
- Per-process open-file table: pointers into the system-wide table. (Plus the directory-structure cache and buffers.)
**Q. Compare the boot control block and the volume control block.**
- Boot control block: info to boot the OS from that volume; usually the first block.
- Volume control block: volume details (total blocks, free blocks, block size, free-block pointers).
**Q. Compare the system-wide and the per-process open-file tables.**
- System-wide: one entry per open file, holding a copy of its FCB.
- Per-process: one table per process, with pointers to entries in the system-wide table.
**Q. Compare the linear list and the hash table for directory implementation.**
- Linear list: simple to program, but time-consuming (linear search).
- Hash table: decreases search time, but has collisions; good only with fixed-size entries or chained overflow.
**Q. ★ What is mounting of a file system?**
- Attaching a file system to the directory structure at a mount point, so its files appear there.
- The mount table records each mounted file system, its mount point and its type.
### Traps
- **What is the hash-table directory's problem: linear search time or collisions?** Collisions. Linear search time is the linear list's problem.
## 8. Allocation methods
### Key terms
- **Allocation method**: How disk blocks are allocated for files (contiguous, linked, indexed).
- **Contiguous allocation**: Each file occupies a set of contiguous blocks.
- **Extent**: A contiguous run of disk blocks; a file consists of one or more of them (used in extent-based file systems, such as Veritas).
- **Linked allocation**: Each file is a linked list of blocks, and the file ends at a nil pointer.
- **FAT (file-allocation table)**: A variation of linked allocation where the next-block pointers sit in one table at the start of the volume.
- **Indexed allocation**: Each file has its own index block(s) of pointers to its data blocks.
- **Linked scheme**: For large files, the blocks of the index table are linked together, with no limit on size.
- **Multi-level (two-level) index**: For large files, an outer index points to index blocks, which point to the data blocks.
- **Combined scheme**: UNIX UFS uses 4 KB blocks and 32-bit addresses, with direct blocks plus single, double and triple indirect blocks in the inode. With indirect blocks, a file can have more index blocks than a 32-bit file pointer can address.
- **Clustering**: Allocating blocks in groups called clusters to cut pointers and seeks.
### Rules
- **What does the best allocation method depend on?** The file access type. If declared at creation, the OS can choose contiguous (good for random access) or linked (sequential only).
- **What does the directory need to locate a contiguous file?** Only the starting block and the length (number of blocks).
- **Which allocation method gives the best performance in most cases?** Contiguous (great for sequential and random access).
- **Why do extent-based systems help contiguous allocation?** A file can grow by adding another extent instead of needing one big hole.
- **★ In linked allocation, how is the end of a file identified?** A nil (null) pointer in the last block.
- **★ Which allocation method is good for sequential, but not random, access?** Linked allocation.
- **Why is direct access slow in linked allocation?** Locating a block takes many I/Os and disk seeks: every block before it is read.
- **What is weak in linked allocation besides direct access?** Reliability: one lost pointer cuts off the rest of the file.
- **How does FAT work?** The table can be cached in memory, so reaching a block follows the table instead of reading every earlier data block. A new block is just a free (0) entry linked in.
- **What does indexed allocation give, and what does it cost?** Random access with no external fragmentation; costs an index block per file.
- **How many reads does a single block direct access need?** Contiguous needs 1 read. Linked needs k + 1 reads to reach block k (counted from 0). Indexed reads the index block(s), then the data block (up to 2 index-block reads in a two-level index).
- **Why do NVM devices need different algorithms?** No disk head: old algorithms waste CPU cycles avoiding non-existent head movement.
- **Why is adding instructions to save one disk I/O reasonable?** Because one disk I/O lasts about 630 million instructions.
### Written questions
**Q. What are the fragmentation issues of the allocation methods?**
- Contiguous allocation (and extent-based systems) suffers from external fragmentation, needing compaction.
- Linked and indexed allocation do not have external fragmentation.
- All methods have internal fragmentation in the last block.
**Q. List the allocation methods.**
- Contiguous
- Linked
- Indexed
- (FAT is a variation of linked allocation)
**Q. What are the problems of contiguous allocation?**
- Finding space on the disk for a file.
- Knowing the file size in advance.
- External fragmentation, which needs compaction off-line (downtime) or on-line.
**Q. What are the problems of linked allocation?**
- Locating a block takes many I/Os and disk seeks (slow direct access).
- Reliability: a lost or damaged pointer breaks the file.
- Each block spends space on a pointer.
**Q. What is the FAT allocation method?**
- A table at the beginning of the volume, indexed by block number; each entry holds the file's next block.
- Like a linked list, but faster on disk and cacheable; new block allocation is simple.
**Q. What is indexed allocation? Give its advantages and disadvantage.**
- Each file has its own index block of pointers to its data blocks.
- Advantages: random access; no external fragmentation.
- Disadvantage: the overhead of the index block.
**Q. What are the two schemes for indexing a file of unbounded length?**
- Linked scheme: link the blocks of the index table (no limit on size).
- Multi-level index: an outer index points to index blocks, which point to the data blocks.
**Q. Compare contiguous and linked allocation.**
- Contiguous: one run of blocks; fast sequential and random access; external fragmentation and compaction.
- Linked: each block points to the next; no external fragmentation; sequential only, slow direct access, weak reliability.
**Q. Compare linked allocation and FAT.**
- Linked: the next-block pointer is inside each data block.
- FAT: the pointers sit in one table at the start of the volume; faster on disk and cacheable.
**Q. Compare linked and indexed allocation.**
- Linked: blocks chained by pointers; good for sequential, not random access.
- Indexed: an index block points to all the data blocks; random access, at the cost of an index block.
**Q. Which access type does each allocation method suit?**
- Contiguous: sequential and random.
- Linked: sequential, not random.
- Indexed: random, but more complex (up to 2 index reads before the data).
### Calculations
**Q. What is the standard model for all the mapping calculations?**
- In these problems a block holds 512 units (words) and a pointer takes 1 unit.
- Contiguous and indexed: divide the logical address by 512.
- Linked: each block keeps 1 unit for the pointer, so 511 units hold data. Divide by 511; the displacement is R + 1.
- Linked scheme of index blocks: each index block uses 1 entry to link the next index block, so it covers 511 data blocks of 512 units. Divide by 512 × 511.
- Two-level index: each outer-index entry covers 512 index entries of 512 units each. Divide by 512 × 512.
**Q. Contiguous allocation, blocks of 512 units. File mail starts at block 19. Find the block and displacement of logical address 3000.**
- 3000 ÷ 512 = 5, remainder 440. Q = 5, R = 440.
- Block = starting address + Q = 19 + 5 = 24.
- Displacement = R = 440.
- Answer: block 24, displacement 440.
**Q. Linked allocation, blocks of 512 units. File jeep's chain is 9, 16, 1, 10, 25. Find the block and displacement of logical address 1200.**
- Each block keeps 1 unit for the pointer, so 511 units hold data. Divide by 511: 1200 ÷ 511 = 2, remainder 178.
- Q = 2, so block 2 of the chain, counting from 0: chain 9, 16, 1, so physical block 1.
- Answer: block 1, displacement 179.
**Q. Indexed allocation, blocks of 512 units. Jeep's index block holds 9, 16, 1, 10, 25. Find the block and displacement of logical address 1600.**
- 1600 ÷ 512 = 3, remainder 64.
- Q = 3 is the displacement into the index table: entry 3 holds block 10.
- R = 64 is the displacement into the block.
- Answer: block 10, displacement 64.
**Q. Two-level index, 512 per block. Map logical address 300,000.**
- Outer index: 300,000 ÷ (512 × 512) = 300,000 ÷ 262,144 = 1, remainder 37,856. Q1 = 1 (entry in the outer index).
- Index level: 37,856 ÷ 512 = 73, remainder 480.
- Answer: Q1 = 1, Q2 = 73 (entry in the index block), R2 = 480 (displacement in the data block).
**Q. Linked scheme of index blocks, 512 per block. Map logical address 300,000.**
- Outer level: 300,000 ÷ (512 × 511) = 300,000 ÷ 261,632 = 1, remainder 38,368. Q1 = 1 (which index block in the chain).
- Inner level: 38,368 ÷ 512 = 74, remainder 480.
- Answer: Q1 = 1, Q2 = 74 (entry in that index block), R2 = 480 (displacement in the data block).
**Q. Small indexed file: A file of at most 256K units, blocks of 512 units, and one index block holds 512 pointers. How many index blocks does it need?**
- 256K units ÷ 512 = 512 blocks.
- One index block holds 512 pointers (1 unit each), so it needs 1 index block.
- Answer: 1 index block.
**Q. Real-bytes example: Two-level index with 4 KB blocks and 4-byte pointers. How many data blocks, and what maximum file size?**
- One 4 KB block holds 4096 ÷ 4 = 1,024 pointers.
- 1,024 × 1,024 = 1,048,576 data blocks.
- Answer: 1,048,576 data blocks, maximum size 4 GB (1,048,576 × 4 KB).
**Q. Disk reads for direct access: linked allocation, 4 KB blocks, byte 20,680. How many reads?**
- 20,680 ÷ 4096 = 5, so block 5.
- Reaching block 5 (counted from 0) needs k + 1 reads: block 5, so 5 + 1 = 6 reads.
- Answer: 6 reads.
**Q. A CPU runs 159,000 MIPS. How many instructions run during one disk I/O on a 250 IOPS disk? On a 60,000 IOPS SSD?**
- Disk: 159,000 ÷ 250 = 636 million (about 630 million).
- SSD: 159,000 ÷ 60,000 = 2.65 million.
- Answer: 636 million for disk, 2.65 million for SSD.
### Traps
- **★ Which allocation methods have external fragmentation?** Only contiguous (including extent-based). Linked and indexed do not. All methods have internal fragmentation (a partly empty last block).
- **FAT is a variation of which allocation method?** Linked allocation, with the chain kept in a table.
- **How are the block and displacement calculated in linked allocation?** Divide by 511, and the displacement is R + 1 (because the first unit holds the pointer).
- **What is the difference between clustering and grouping?** Clustering allocates blocks in groups for files; grouping is a method for managing free space.
- **What does clustering do to internal fragmentation?** It increases it (while it reduces pointers and seeks).
## 9. Free-space management
### Key terms
- **Free-space list**: What the file system keeps to track available blocks.
- **Bit vector (bit map)**: One bit per block: 1 if the block is free, 0 if occupied.
- **Linked free list**: Free blocks chained together, each pointing to the next.
- **Grouping**: The first free block stores the addresses of the next n−1 free blocks, plus a pointer to the next such block.
- **Counting**: Keep the address of the first free block and the count of free blocks that follow it.
- **Metaslabs**: The units ZFS divides device space into.
- **Space map**: ZFS's record of free space for each metaslab, a log in counting format.
### Rules
- **How do CPUs speed up the bit-vector search?** Instructions that return the offset of the first 1 bit in a word.
- **When is there no need to traverse the whole linked free list?** When the number of free blocks is recorded.
- **Why does counting work well?** Space is frequently used and freed contiguously (contiguous allocation, extents, clustering).
- **Why does ZFS use space maps?** On very large file systems, full bit maps cannot fit in memory, so updates take thousands of I/Os.
- **How does a ZFS space map work?** Counting entries are logged in time order; loaded into a balanced tree in memory, the log replayed, and contiguous free blocks combined.
### Written questions
**Q. ★ What is the bit vector (bit map) method used for free-space management?**
- The file system keeps one bit for each disk block.
- Bit = 1: the block is free. Bit = 0: the block is occupied.
- Advantage: easy to find contiguous free blocks.
- Disadvantage: the map needs extra space; for a large disk the whole map cannot be kept in main memory.
**Q. What is the advantage and drawback of the linked free list?**
- Advantage: no waste of space.
- Drawback: cannot get contiguous space easily.
**Q. List the free-space management methods.**
- Bit vector (bit map)
- Linked list (free list)
- Grouping
- Counting
- Space maps (in ZFS)
**Q. What is the counting method?**
- Keep the address of the first free block and the count of free blocks that follow it.
- It works because space is often used and freed in contiguous runs.
**Q. What is the grouping method?**
- The first free block stores the addresses of the next n−1 free blocks, plus a pointer to the next block of free-block pointers.
**Q. Compare the bit vector and the linked free list.**
- Bit vector: one bit per block; easy to get contiguous space, but needs extra space.
- Linked list: free blocks point to each other; no waste, but contiguous space is hard to get.
**Q. Compare grouping and counting.**
- Grouping: a free block stores the addresses of the next n−1 free blocks.
- Counting: entries of (first free block, count of free blocks that follow).
### Calculations
**Q. A 16-block disk has blocks 0, 1, 5, 9 and 15 free. Write the bit vector.**
- 1 for free, 0 for occupied, block 0 first.
- Answer: 1100010001000001.
**Q. 8-bit words: 00000000, 00000000, 00101000. Find the first free block.**
- The offset of the first 1 bit is counted from 0, starting at the left.
- Block number = (bits per word) × (number of 0-value words) + offset of the first 1 bit.
- = 8 × 2 + 2 = 18.
- Answer: 18.
**Q. Disk of 1 TB (2^40 bytes), blocks of 4 KB (2^12 bytes). How big is the bit map? With clusters of 4 blocks?**
- Number of blocks = 2^40 ÷ 2^12 = 2^28 bits = 2^25 bytes = 32 MB.
- Clusters of 4: 2^28 ÷ 4 = 2^26 bits = 8 MB.
- Answer: 32 MB bit map; 8 MB with clusters of 4.
**Q. Free blocks: 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 17, 18, 25, 26, 27. Write the counting list.**
- Each entry is (first free block, count).
- Answer: (2, 4), (8, 6), (17, 2), (25, 3).
### Traps
- **In the bit vector, what does bit 1 mean?** Free (0 means occupied).
- **Which free-space method can give contiguous space easily?** The bit vector (the linked list cannot).
