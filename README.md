The modules with name "consruct_output... .py" takes a directory containing 'conllu format' files, and compute the formal measures for real trees and corressponding random baseline trees. There are six such modules for six baselines. The measures being computed i.e., gap degree, edge degree etc. are stored in same putput file for real trees and random baseline trees.

The modules with name "baseline_conditions... .py" containts the algorithm to generate trees for different baselines. To know more about these baselines and measures being computed, see <a href="http://ceur-ws.org/Vol-1779/10yadav.pdf">this paper</a> and <a href="https://www.aclweb.org/anthology/W19-7802.pdf">this paper</a>. 

To install required dependencies: pip install -r requirements.txt
