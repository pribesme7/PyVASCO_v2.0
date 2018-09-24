from PyQt4.QtGui import QMessageBox,QSizePolicy,QTextEdit,QValidator,QDoubleSpinBox
import numpy as np
import re
import os


class MyMessageBox(QMessageBox):
    """
    Resizeble message box. Innheritates from QMessageBox.
    """
    def __init__(self):
        QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        textEdit = self.findChild(QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return result

# Regular expression to find floats. Match groups are the whole string, the
# whole coefficient, the decimal part of the coefficient, and the exponent
# part.
_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')

def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class ScientificDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, *args, **kwargs):
        super(QDoubleSpinBox,self).__init__(*args, **kwargs)
        self.setMinimum(-np.inf)
        self.setMaximum(np.inf)
        self.setDecimals(1000)

    #def validate(self, text, position):
    #    return self.validator.validate(text, position)

    #def fixup(self, text):
    #    return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return format_float(value)

    def stepBy(self, steps):
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        if groups[3] == None:
            text = "%e"%float(text)
            groups = _float_re.search(text).groups()

        decimal = float(groups[1])
        ex = int(groups[3][1:])
        if decimal == 0 and steps ==-1:
            decimal = 9.
            ex = ("e"+ "%i")%(int(ex-1))
            new_string = "{:g}".format(decimal) + ex
            self.lineEdit().setText(new_string)
        else:
            decimal += steps
            if decimal >=10.:
                decimal = decimal/10.
                ex = "e"+ str(ex+1)
                new_string = "{:g}".format(decimal) + str(ex)
                self.lineEdit().setText(new_string)

            elif decimal == 0:
                decimal = 9.
                ex = "e"+ str(ex-1)
                new_string = "{:g}".format(decimal) + str(ex)
                self.lineEdit().setText(new_string)

            else:
                new_string = "{:g}".format(decimal) + (groups[3] if groups[3] else "")
                self.lineEdit().setText(new_string)

def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = "{:g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string

def ReadComponent(File):
    Data = []
    if os.path.isdir(File):
        Name = os.path.split(File)[-1]
        files = os.listdir(File)
        Data = {}
        for f in files:
            p = f.split("_")[-1].split(".")[0]
            data = ReadComponent(File + "/" +  f)
            Data[p] = data
        return Data

    else:

        with open(File,"r") as f:
            lines = f.readlines()

        for l in lines:
            l = l.strip("\n").split(",")
            Data.append(l)

        return [x[1:] for x in Data[1:]]

def ReWrite(File, Data,vertical_labels= ["d [mm]", "L [mm]", "T [K]", "Material", "Pump", 'Gas source', 'Photon flux [photons/m/s]',
                       'Electron flux [electrons/m/s]'], horizontal_labels = [""] ):
    f = open(File, "w")
    name = os.path.split(str(File))[-1].split("_New")[0].split(".csv")[0]
    if type(horizontal_labels) == list :
        f.write("%s,%s \n" % (name, ",".join(horizontal_labels)))
    else:
        f.write("%s,%s \n" % (name, str(horizontal_labels)))

    for i in range(len(vertical_labels)):
        if type(Data[i]) == list :
            f.write("%s,%s \n" % (vertical_labels[i], ",".join(Data[i])))
        else:
            f.write("%s,%s \n" % (vertical_labels[i], str(Data[i])))
    f.close()
    return
