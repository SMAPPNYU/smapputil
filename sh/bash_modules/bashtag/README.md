bashtag
=======

PLEASE DO NOT USE THIS "SOFTWARE"

IT IS A WIP AND NOT AT ALL READY

YOU HAVE BEEN WARNED

bashtag is a process wrapper (it basically just calls eval) that lets you create and run processes / programs with any arbitrary number of extra inputs attached to them.

this is useful for when you want to run a script and tag it with a keyword so that it can later be identified instead of just identifying it via process ID or keywords in the process. 

Let's say you want to run 5 processes that all do similar things but you want to differentiate between them based on a tag. Or you want to imeplement a tagging system for your running programs. You can do that with bashtag.

This was meant to work on a mac. If you don't have a mac/unix or a linux machine, what are you doing? Are you even a programmer?

What it (should) do is run the command as a dependent child process. Then you'll do `bashtag kill` and it will get the process group ID of the parent with the tags and kill all the running dependent children.

Usage
=====

##bashtag

Just run all your scripts or programs as an input to bashtag with any tags you want tacked on as supplemental inputs.

```sh
bash bashtag.sh 'python ../path/to/my/python.py' yvanscripts python sunday 
//OR
bash bashtag.sh 'bash ../path/to/my/bash.sh' yvanscripts bash sunday
```

instead of 

```sh
python ../path/to/my/python.py
//OR
bash ../path/to/my/bash.sh
```

if you now check your process tab (ps aux | grep bashtag) you should see the process running like so:

```sh
bash bashtag.sh 'python ../path/to/my/python.py' yvanscripts python sunday

bash bashtag.sh 'bash ../path/to/my/bash.sh' yvanscripts bash sunday
```

the process inside the single or double quotes is the process that's being run, in addition to the extra tags that are now tacked onto your process and can be used to identify it.

you could use this to attach a unique ID or personal tag to any script you run.

##bashtag kill

```sh
bash bashtag.sh kill 'yvanscripts' 'python'
```

the processes tagged with those tags should now be killed.

To use `bashtag` instead of `bash bashtag.sh` you need to add it to your path:
===========================================

To see your path type `echo $PATH` on the unix command line

To do this you need bashtag.sh to be accessible within your path:

1. Navigate into /usr/local/bin or any other directory referenced by your $PATH (but really I'd stick to /usr/local/bin or /usr/bin).

2. type  `ln -s /full/path/to/bashtag.sh bashtag`

3. now you can use the `bashtag` command instead of directly calling the bashtag.sh script.

entries will now appear on the process tab like so:

```sh
/bin/bash /usr/local/bin/bashtag python ../path/to/my/python.py /dev/null scriptz monday
```

links
=====

[https://kb.iu.edu/d/abbe (symbolic links)] (https://kb.iu.edu/d/abbe)

[http://stackoverflow.com/questions/11065077/eval-command-in-bash-and-its-typical-uses (eval)] (http://stackoverflow.com/questions/11065077/eval-command-in-bash-and-its-typical-uses)

authors
=======

[yvan](https://github.com/yvan)