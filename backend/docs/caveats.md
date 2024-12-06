# Getting the Head of the Tree
If you wanna get the head of a tree, don't filter any field that are present on other tables.
Eg: A checkout can trigger builds that are tests on raspberry-pis, but the next checkout of the same tree will not always be tested on the same hardware (maybe they were swapped or got stolen, who knows.) Filtering a checkout by a field from other tables can result on count bugs.
