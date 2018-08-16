
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from PyQt4.QtGui import QApplication, QIcon

from Visualisation import MainWindow


def main():

    app = QApplication(sys.argv)

    # app.setOrganizationName("CERN Vacuum Simulation")
    # app.setOrganizationDomain("CERN")
    app.setApplicationName("PyVASCO")
    app.setStyle("cleanlooks")
    app.setWindowIcon(QIcon("Icon.png"))
    window = MainWindow.Window()
    window.show()
    app.exec_()



if __name__ == "__main__":
    main()
