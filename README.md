The modules with name <i>"consruct_output... .py"</i> takes a directory containing <i>conllu format</i> files, and compute the formal measures for real trees and corressponding random baseline trees. There are six such modules for six baselines. The measures being computed i.e., gap degree, edge degree etc. are stored in same output file for real trees and random baseline trees.

The modules with name "baseline_conditions... .py" containts the algorithm to generate trees for different baselines. To know more about these baselines and measures being computed, see <a href="https://www.aclweb.org/anthology/W19-7802.pdf">this</a> and <a href="http://socsci.uci.edu/~rfutrell/papers/yadav2021dependency.pdf">this</a> paper. 

To install required dependencies: pip install -r requirements.txt
