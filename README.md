# Tex select random MCPs


This code selects random, shuffled questions from tex files that have latex exam package Multiple Choice Questions. Those files should have only Multiple Choice Questions. 

This way, you can create your exam db as latex files, then select from them and prepare specific exams.

# Requirements

Python and hatch is needed to be installed. Hatch installs the rest of the python packages.

# Usage

Download the repo. Run 

    hatch run yxslx --help

You will see how you can use the program.


# Tips

You can edit tex_exam/tpl/main.tex file to your liking. Then re-generate the program.

There is an example file in tex_exam/tpl/db. You can start building your question db from that file.

# Caveats and todos

Originally the cli was named yxslx. I will at some point change the cli name.

If your options are complex, it does not work. E.g. if you have multiline content, with tikz graphs, etc. there seems to be a bug that prevents it working. If you can find and solve the bug, you are welcome to submit a PR. 

# License

MIT License.

# Author

Oğuz Altun.
