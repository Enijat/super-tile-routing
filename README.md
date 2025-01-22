# How to run:
It's pretty simple, if you want to just use **supertile_layout_generator.cpp**, all you have to do is compile it and run it. You could do this with 

```bash
g++ -o supertile_layout_generator supertile_layout_generator.cpp
./supertile_layout_generator -h
```

If you want to use the Python script you will need Python 3.10 or newer, and the compiled executable of the **supertile_layout_generator.cpp** file will have to have the name **supertile_layout_generator**. You can then run the python script with

```bash
python json_generator.py
```

Both programs will tell you everything you need to know in the command line (especially **supertile_layout_generator** has a decently exhaustive explanation for all options and possible inputs), for any more options you will have to change the code yourself.

# Disclaimer:
The **supertile_layout_generator.cpp** is quite a mess and not really "nice code", this is due the three reasons:
  - I originally wanted to force myself to learn C++ when I started working on this, but I just ended up using C syntax most of the time, with some rare occurrences of C++ showing up in random places.
  - The program "isn't finished" in the sense that I originally intended for it do to way more and be more optimized, but ended up first using it as a tec demonstration and now I just use it to generate lookup tables, as can be determined by the large amount of "TODO" comments. '^^
  - As mentioned it was retrofitted to generate lookup tables for the actual implementation of this subject into [fiction](https://github.com/cda-tum/fiction). Which created some random pieces of code that only make sense in the bigger context.

So the current content is just something that was thrown together to show that the concept works and at every step of the process only more stuff was thrown at it to test new concepts.

# Context
The logic and ideas present in this code were used for a contribution to [fiction](https://github.com/cda-tum/fiction) in the form of a Bachelors Thesis with the name "Super-Tile Routing for Omnidirectional Information Flow in SiDB Logic".
