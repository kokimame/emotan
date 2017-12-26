from gui.qt import *


class Indexer(QSpinBox):
    def __init__(self, val):
        super(Indexer, self).__init__()
        self.setObjectName("index")
        self.setMaximum(99999)
        self.setValue(val)
        self.setFixedWidth(42)
        self.setFocusPolicy(Qt.StrongFocus)

    def stepBy(self, step):
        # Change default down-button to increase the number and vice versa.
        super().stepBy(-step)


class Editor(QWidget):
    _ITALIC = QFont()
    _ITALIC.setItalic(True)

    COLOR = {'atop': "background-color : rgb(%d,%d,%d)" % (255,255,180),
             'def': "background-color : rgb(%d,%d,%d)" % (255,180,230),
             'ex': "background-color : rgb(%d,%d,%d)" % (180,230,255),}

    def __init__(self, ewkey, text=""):
        super(Editor, self).__init__()
        self.ewkey = ewkey
        self.label = QLabel(ewkey)
        self.label.setFixedWidth(40)
        self.label.setFont(self._ITALIC)
        self.label.setStyleSheet(self._color(ewkey))
        self.editor = QLineEdit(text)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def _color(self, ewkey):
        sk = ewkey.split('-')
        if 'atop' in sk:
            return self.COLOR['atop']
        elif 'def' in sk:
            return self.COLOR['def']
        elif 'ex' in sk:
            return self.COLOR['ex']
        else:
            raise Exception("Wrong ewkey")

    # The function name is camel case as the class had to overwrite QLineEdit
    # otherwise too many rename were required.
    def setText(self, text):
        self.editor.setText(text)

    def text(self):
        return self.editor.text()


class EntryWidget(QWidget):
    # Design of QLabel shown on 'View' mode
    _ENTRY_VIEW = '<html><head/><body>{content}</body></html>'
    _FONT_ATOP = '<p><span style=" font-size:16pt; font-weight:520;">{text}</span></p>'
    _FONT_DEF = '<p>{num}. {text}</p>'
    _FONT_EX = '<p><span style="color:#8d8d8d;">&quot;{text}&quot;</span></p>'

    _BOLD, _ITALIC = QFont(), QFont()
    _BOLD.setBold(True)
    _ITALIC.setItalic(True)

    move = pyqtSignal(int, int)
    delete = pyqtSignal(int)

    def __init__(self, parent, row, atop, mode, eset):
        super(EntryWidget, self).__init__(parent)
        # the EntryList this entry belongs to
        self.parent = parent
        # Row at EntryList takes from 0 to list.count()-1
        self.row = row
        self.mode = mode
        # Entry setting
        self.lv1 = eset['lv1']
        self.lv2 = eset['lv2']
        # External sources where the items of an entry came
        self.sources = []

        # Dictionary of QLineEdit.
        # Text stored in the editors will be the actual learning materials.
        # The keys, referenced as 'ewkey' (with underscode), come in 'atop', 'def-n', 'ex-n-n' where 0 < n < 10
        # ===
        # 'atop' : The name of Entry. Should be identical in the parent.
        # 'def-x' : Main part of an Entry. Each entry has upto 9 of this section.
        # 'ex-x-x' : Sub part. Each 'def-x' has upto 9 of the sub section.
        # ===
        # NOTE: The name of keys must not be modified because we alphabetically sort them out in a process
        self.editors = {}

        # Building UI
        layout = QStackedLayout()
        layout.addWidget(self._ui_view(atop))
        layout.addWidget(self._ui_editor(atop=atop))
        self.setLayout(layout)
        self.set_mode(mode)

    def set_mode(self, new_mode):
        if new_mode == "View":
            self.layout().setCurrentIndex(0)
            self.mode = new_mode
        if new_mode == "Edit":
            self.layout().setCurrentIndex(1)
            self.mode = new_mode

    def _ui_view(self, atop):
        view = QLabel()
        view.setWordWrap(True)
        view.setObjectName("view")

        if atop == '':
            atop = "Unnamed Entry"

        view.setText(self._ENTRY_VIEW.format
                     (content=self._FONT_ATOP.format(text=atop)))
        index = Indexer(self.row + 1)
        index.valueChanged.connect(self._move_to)

        layout = QHBoxLayout()
        layout.addWidget(index)
        layout.addWidget(view)
        base = QWidget()
        base.setLayout(layout)
        return base

    def _ui_editor(self, atop=None):
        # Widget shown on Editor mode of EntryList
        layout = QVBoxLayout()

        if atop != None:
            self.editors['atop'] = Editor('atop', text=atop)
        layout.addWidget(self.editors['atop'])
        row = 1
        for i in range(1, self.lv1 + 1):
            ewkey = 'def-%d' % i
            if ewkey not in self.editors:
                self.editors[ewkey] = Editor(ewkey)
            layout.addWidget(self.editors[ewkey])
            for j in range(1, self.lv2 + 1):
                ewkey = "ex-%d-%d" % (i, j)
                if ewkey not in self.editors:
                    self.editors[ewkey] = Editor(ewkey)
                layout.addWidget(self.editors[ewkey])
                row += 1
            row += 1

        base = QWidget()
        base.setLayout(layout)
        return base

    def reshape(self, lv1, lv2):
        self.lv1, self.lv2 = lv1, lv2
        stacked = self.layout()
        assert stacked
        # Old editor widget
        wig = stacked.widget(1)
        stacked.removeWidget(wig)
        stacked.addWidget(self._ui_editor())
        stacked.widget(0).repaint()
        stacked.widget(1).repaint()
        self.set_mode(self.mode)

    def update_index(self, row):
        index = self.findChild(QSpinBox, "index")
        index.valueChanged.disconnect()
        index.setValue(row + 1)
        index.valueChanged.connect(self._move_to)
        self.row = row

    def update_view(self):
        if self.editors['atop'].text() == '':
            atop = "Unnamed entry"
        else:
            atop = self.editors['atop'].text()
        content = self._FONT_ATOP.format(num=self.row + 1, text=atop)

        for i in range(1, self.lv1 + 1):
            if self.editors['def-%d' % i].text() != '':
                content += self._FONT_DEF.format(num=i, text=self.editors['def-%d' % i].text())
            for j in range(1, self.lv2 + 1):
                if self.editors['ex-%d-%d' % (i, j)].text() != '':
                    content += self._FONT_EX.format(text=self.editors['ex-%d-%d' % (i, j)].text())

        view = self.findChild(QLabel, "view")
        view.setText(self._ENTRY_VIEW.format(content=content))

    # Set the text of downloaded contents to each of matched editors
    def update_editor(self, items):
        if 'atop' in items:
            self.editors['atop'].setText(items['atop'])

        for i in range(1, self.lv1 + 1):
            if 'def-%d' % i in items:
                self.editors['def-%d' % i].setText(items['def-%d' % i])
            for j in range(1, self.lv2 + 1):
                if 'ex-%d-%d' % (i, j) in items:
                    self.editors['ex-%d-%d' % (i, j)].setText(items['ex-%d-%d' % (i, j)])

    def _move_to(self, next):
        # Converts index to row of list.count()
        next -= 1
        if next == self.row:
            # When spin.setValue triggers this method
            return

        if not 0 <= next < self.parent.count():
            spin = self.findChild(QSpinBox, "index")
            spin.setValue(self.row + 1)
        else:
            self.move.emit(self.row, next)

    def str_index(self):
        # Return string number from 00000 to 99999 based on the index
        index = self.row + 1
        snum = (5 - len(str(index))) * '0' + str(index)
        return snum

    # Returns the class' properties in a dictionary. Will be called on saving.
    def data(self):
        data = {}
        data['idx'] = self.row + 1
        data['atop'] = self.editors['atop'].text()
        data['lv1'] = self.lv1
        data['lv2'] = self.lv2
        for i in range(1, self.lv1 + 1):
            data['def-%d' % i] = self.editors['def-%d' % i].text()
            for j in range(1, self.lv2 + 1):
                data['ex-%d-%d' % (i, j)] = self.editors['ex-%d-%d' % (i, j)].text()

        return data

