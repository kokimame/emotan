# -*- coding: utf-8 -*-
# Copyright (C) 2017-Present: Kohki Mametani <kohkimametani@gmail.com>
# License: GNU GPL version 3 or later; http://www.gnu.org/licenses/gpl.html
#
# This module consists of several GUI classes originally developed in AwesomeTTS projects,
# and merges some of them into one big AwesomeTTS class.
# You can find other components from the project under joytan/joytan/speaker.
#
# Joytan adds Overview to the GUI to show users which TTS service is allocated to
# each of text stored in EntryWidget.
# The original copyright notice is shown below.
# ==========================================
# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import inspect

from gui.qt import *


class Label(QLabel):
    """Label with HTML disabled."""

    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)
        self.setTextFormat(Qt.PlainText)


class Note(Label):
    """Label with wrapping enabled and HTML disabled."""

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.setWordWrap(True)


class ServiceQuo(QLabel):
    """Description of TTS options for a given Entry's editor"""
    _BODY = '<p><span style="font-size:13pt">{body}</span>' \
            '<span style="font-size:15pt; font-weight:600;">  {svc}</span></p>'
    _UNINIT = '<p><span style="color:#ff0000;">TTS undefined</span></p>'
    _OPTIONS = '<p>{options}</p>'

    def __init__(self, ewkey):
        super(ServiceQuo, self).__init__()
        self.setWordWrap(True)
        self.ewkey = ewkey
        self.idx = None
        self.options = None

        self.set_desc(None, None)

    def set_desc(self, svc_id, options):
        if not options:
            content = self._BODY.format(body=self.ewkey, svc="")
            content += self._UNINIT
        else:
            content = self._BODY.format(body=self.ewkey, svc=svc_id)
            # desc = self.summarizer(option)
            s=str(options.items())
            s=str(options.items())[12:len(s)-1]
            content += self._OPTIONS.format(options=s)
            self.options = options
        self.setText(content)

    def summarizer(self):
        pass

class AwesomeTTS(QWidget):
    _FONT_HEADER = QFont()
    _FONT_HEADER.setPointSize(12)
    _FONT_HEADER.setBold(True)

    _FONT_INFO = QFont()
    _FONT_INFO.setItalic(True)

    _FONT_LABEL = QFont()
    _FONT_LABEL.setBold(True)

    _FONT_TITLE = QFont()
    _FONT_TITLE.setPointSize(16)
    _FONT_TITLE.setBold(True)

    _SPACING = 10

    _OPTIONS_WIDGETS = (QComboBox, QAbstractSpinBox)
    _INPUT_WIDGETS = _OPTIONS_WIDGETS + (QAbstractButton,
                                         QLineEdit, QTextEdit)

    def __init__(self, el_conf, alerts, ask, *args, **kargs):
        super(AwesomeTTS, self).__init__()

        from joytan.speaker import router, config, logger
        self.router = router
        self.config = config
        self.logger = logger

        self._panel_built = {}
        self._panel_set = {}
        self._svc_id = None
        self._svc_count = 0
        self._alerts = alerts
        self._ask = ask
        # Access to mw.entrylist
        # el_conf[0]: el.get_config('ewkey')
        # el_conf[1]: el_set_config('ewkey', new_config)
        self.el_conf = el_conf

        vbox = QVBoxLayout()
        # vbox.addLayout(self._banner())
        # vbox.addWidget(self._divider(QFrame.HLine))
        vbox.addLayout(self._services())
        vbox.addSpacing(self._SPACING)
        vbox.addLayout(self._control())

        hbox = QHBoxLayout()
        hbox.addLayout(self._overview())
        hbox.addWidget(self._divider())
        hbox.addLayout(vbox)


        self.setLayout(hbox)


        dropdown = self.findChild(QComboBox, 'service')
        """
        Recall the last used (or default) service and call in to
        activate its panel, populate presets, and then clear the input
        text box.
        """
        # refresh the list of groups
        while dropdown.count() > self._svc_count:
            dropdown.removeItem(dropdown.count() - 1)
        groups = list(self.config['groups'].keys())
        if groups:
            dropdown.insertSeparator(dropdown.count())
            for group in sorted(groups):
                dropdown.addItem(group, 'group:' + group)

        # If voice for 'atop' item in the EntryList is already defined
        # such as the case you load it from .jel file or
        # you open TTS preference second time.
        if self.el_conf[0]('atop'):
            idx, options = self.el_conf[0]('atop')[0], self.el_conf[0]('atop')[2]
            self._on_service_activated(idx, initial=True, use_options=options)
        else:
            idx = max(dropdown.findData(self.config['last_service']), 0)
            self._on_service_activated(idx, initial=True)
        dropdown.setCurrentIndex(idx)

        self._on_preset_refresh(select=True)

        text = self.findChild(QWidget, 'text')
        try:
            text.setText("")
        except AttributeError:
            text.setPlainText("")


    def _control(self):
        """
        Returns the "Test Settings" header, the text input and a preview
        button.

        Subclasses should either extend this or replace it, but if they
        replace this (e.g. to display the text input differently), the
        objects created must have setObjectName() called with 'text'
        and 'preview'.
        """

        text = QLineEdit()
        text.keyPressEvent = lambda key_event: (
            self._on_preview()
            if key_event.key() in [Qt.Key_Enter, Qt.Key_Return]
            else QLineEdit.keyPressEvent(text, key_event)
        )
        text.setObjectName('text')
        text.setPlaceholderText("type a phrase to test...")

        button = QPushButton("&Preview")
        button.setObjectName('preview')
        button.clicked.connect(self._on_preview)

        hor = QHBoxLayout()
        hor.addWidget(text)
        hor.addWidget(button)

        header = Label("Preview")
        header.setFont(self._FONT_HEADER)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(hor)
        layout.addStretch()
        layout.addSpacing(self._SPACING)

        return layout

    def _overview(self):
        overview = QListWidget()
        overview.setStyleSheet("""
                            QListWidget::item { border-bottom: 1px solid black; }
                            QListWidget::item:selected { background: rgba(0,255,255,30); }
                           """)
        overview.setObjectName('overview')
        for i, ewkey in enumerate(self.el_conf[0]('ewkeys')):
            quo = ServiceQuo(ewkey)
            svc_values = self.el_conf[0](ewkey)
            if svc_values:
                quo.idx = svc_values[0]
                # Pass svc_id & options
                quo.set_desc(svc_values[1], svc_values[2])
            else:
                # Reinitialize ttsmap if ewkey has unavailable TTS on the platform
                self.el_conf[1](ewkey, None)
            lwi = QListWidgetItem()
            lwi.setSizeHint(quo.sizeHint())
            overview.addItem(lwi)
            overview.setItemWidget(lwi, quo)
            # First item in the list is selected by default
            if i == 0:
                lwi.setSelected(True)
                overview.setCurrentItem(lwi)

        overview.currentItemChanged.connect(self._on_overview_changed)

        header = Label("Overview")
        header.setFont(self._FONT_HEADER)
        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(overview)
        return layout

    def _on_overview_changed(self):
        """
        Called when users clicked other items in the Overview list,
        rebuild the service panel based on options the newly selected item stores,
        or initialize the same panel with previously selected one.
        """
        overview = self.findChild(QListWidget, 'overview')
        item = overview.currentItem()
        iw = overview.itemWidget(item)

        dropdown = self.findChild(QComboBox, 'service')

        if not iw.options:
            # If TTS options are undefined for the item
            idx = dropdown.currentIndex()
            self._on_service_activated(idx)
        else:
            # If TTS options are already defined,
            # do the same routine as activating presets does
            dropdown.setCurrentIndex(iw.idx)
            self._on_service_activated(iw.idx, use_options=iw.options)


    def _update_overview(self):
        overview = self.findChild(QListWidget, 'overview')
        try:
            svc_id, options = self._get_service_values()
        except AssertionError:
            # TOO EARLY TO UPDATE OVERVIEW
            return

        dropdown = self.findChild(QComboBox, 'service')
        idx = dropdown.currentIndex()
        item = overview.currentItem()

        iw = overview.itemWidget(item)
        iw.options = options
        iw.idx = idx
        iw.set_desc(svc_id, options)
        item.setSizeHint(iw.sizeHint())
        self.el_conf[1](iw.ewkey, (idx, svc_id, options))
        overview.repaint()

        idx = dropdown.currentIndex()
        combo = self.findChild(QComboBox, 'service')
        svc_id = combo.itemData(idx)
        options = self.router.get_options(svc_id)


    def _services(self):
        """
        Return the service panel, which includes a dropdown for the
        service and a stacked widget for each service's options.
        """

        dropdown = QComboBox()
        dropdown.setObjectName('service')

        stack = QStackedWidget()
        stack.setObjectName('panels')

        for svc_id, text in self.router.get_services():
            dropdown.addItem(text, svc_id)

            svc_layout = QGridLayout()
            svc_layout.addWidget(Label("Pass the following to %s:" % text),
                                 0, 0, 1, 2)

            svc_widget = QWidget()
            svc_widget.setLayout(svc_layout)
            stack.addWidget(svc_widget)


        self._svc_count = dropdown.count()

        # one extra widget for displaying a group
        group_layout = QVBoxLayout()
        group_layout.addWidget(Note())
        group_layout.addStretch()
        group_widget = QWidget()
        group_widget.setLayout(group_layout)
        stack.addWidget(group_widget)

        dropdown.activated.connect(self._on_service_activated)
        dropdown.currentIndexChanged.connect(self._on_preset_reset)


        hor = QHBoxLayout()
        hor.addWidget(Label("Generate using:"))
        hor.addWidget(dropdown)
        hor.addStretch()

        header = Label("Configure Service")
        header.setFont(self._FONT_HEADER)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(hor)
        layout.addWidget(stack)
        layout.addStretch()
        layout.addLayout(self._ui_services_presets())

        return layout

    def _on_service_activated(self, idx, initial=False, use_options=None):
        """
        Construct the target widget if it has not already been built,
        recall the last-used values for the options, and then switch the
        stack to it.
        """
        combo = self.findChild(QComboBox, 'service')
        svc_id = combo.itemData(idx)
        stack = self.findChild(QStackedWidget, 'panels')
        save = self.findChild(QPushButton, 'presets_save')

        if svc_id.startswith('group:'):  # we handle groups differently
            svc_id = svc_id[6:]
            group = self.config['groups'][svc_id]
            presets = [preset for preset in group['presets'] if preset]

            stack.setCurrentIndex(stack.count() - 1)
            stack.widget(stack.count() - 1).findChild(QLabel).setText(
                svc_id +
                (" has no presets yet." if len(presets) == 0
                 else " uses " + presets[0] + "." if len(presets) == 1
                 else ((" randomly selects" if group['mode'] == 'random'
                        else " tries in-order") + " from:\n -" +
                       "\n -".join(presets[0:5]) +
                       ("\n    (... and %d more)" % (len(presets) - 5)
                        if len(presets) > 5 else ""))) +
                "\n\n"
                "Go to AwesomeTTS config for group setup.\n"
                "Access preset options in dropdown below."
            )
            save.setEnabled(False)
            return

        save.setEnabled(True)
        panel_unbuilt = svc_id not in self._panel_built
        panel_unset = svc_id not in self._panel_set

        if panel_unbuilt or panel_unset or use_options:
            widget = stack.widget(idx)
            options = self.router.get_options(svc_id)

            if panel_unbuilt:
                self._panel_built[svc_id] = True
                # FIXME: Building service panel while opening the tab looks shacky on Mac
                self._on_service_activated_build(svc_id, widget, options)

            if panel_unset or use_options:
                self._panel_set[svc_id] = True
                self._on_service_activated_set(svc_id, widget, options,
                                               use_options)

        stack.setCurrentIndex(idx)
        if panel_unbuilt and not initial:
            self.adjustSize()

        self._svc_id = svc_id
        help_svc = self.findChild(QAction, 'help_svc')
        if help_svc:
            help_svc.setText("Using the %s service" % combo.currentText())
        self._update_overview()

    def _ui_services_presets(self):
        """Returns the preset controls as a horizontal layout."""
        label = Label("Quickly access this service later?")
        label.setObjectName('presets_label')

        dropdown = QComboBox()
        dropdown.setObjectName('presets_dropdown')
        dropdown.setSizePolicy(QSizePolicy.MinimumExpanding,
                               QSizePolicy.Preferred)
        dropdown.activated.connect(self._on_preset_activated)

        delete = QPushButton(QIcon(':icons/editdelete.png'), "")
        delete.setObjectName('presets_delete')
        delete.setIconSize(QSize(16, 16))
        delete.setFixedSize(18, 18)
        delete.setFlat(True)
        delete.setToolTip("Remove this service configuration from\n"
                          "the list of remembered services.")
        delete.clicked.connect(self._on_preset_delete)

        save = QPushButton("Save")
        save.setObjectName('presets_save')
        save.setFixedWidth(save.fontMetrics().width(save.text()) + 20)
        save.setToolTip("Remember the selected service and its input\n"
                        "settings so that you can quickly access it later.")
        save.clicked.connect(self._on_preset_save)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(dropdown)
        layout.addWidget(delete)
        layout.addSpacing(self._SPACING)
        layout.addWidget(save)

        return layout

    def _on_service_activated_build(self, svc_id, widget, options):
        """
        Based on the list of options, build a grid of labels and input
        controls.
        """
        self.logger.debug("Constructing panel for %s", svc_id)

        row = 1
        panel = widget.layout()

        for option in options:
            label = Label(option['label'])
            label.setFont(self._FONT_LABEL)

            if isinstance(option['values'], tuple):
                start, end = option['values'][0], option['values'][1]

                vinput = (
                    QDoubleSpinBox
                    if isinstance(start, float) or isinstance(end, float)
                    else QSpinBox
                )()

                vinput.setRange(start, end)
                if len(option['values']) > 2:
                    vinput.setSuffix(" " + option['values'][2])
                vinput.valueChanged.connect(self._on_preset_reset)

            else:  # list of tuples
                vinput = QComboBox()
                for value, text in option['values']:
                    vinput.addItem(text, value)

                if len(option['values']) == 1:
                    vinput.setDisabled(True)
                vinput.currentIndexChanged.connect(self._on_preset_reset)


            panel.addWidget(label, row, 0)
            panel.addWidget(vinput, row, 1, 1, 2)
            if option['key']=='voice':
                vinput.currentIndexChanged.connect(self._on_voice_change)
            row += 1

        label = Label("Additional Parameters:")
        line = QLineEdit()
        label.setObjectName("addLabel")
        line.setObjectName("addLine")
        line.textChanged.connect(self._update_overview)
        panel.addWidget(label, row, 0)
        panel.addWidget(line, row, 1, 1, 2)
        row+=1


        extras = self.router.get_extras(svc_id)
        if extras:
            config = self.config

            def glue_edit(edit, key):
                """Wires `textEdited` on `edit`, closing on `key`."""

                def on_text_edited(val):
                    """Updates `extras` dict when user input changes."""
                    config['extras'] = dict(
                        list(config['extras'].items()) +
                        [(
                            svc_id,
                            dict(
                                list(config['extras'].get(svc_id, {}).items()) +
                                [(key, val)]
                            ),
                        )]
                    )

                edit.textEdited.connect(on_text_edited)

            for extra in extras:
                label = Label(extra['label'])
                label.setFont(self._FONT_LABEL)

                edit = QLineEdit()
                key = extra['key']
                try:
                    edit.setText(config['extras'][svc_id][key])
                except KeyError:
                    pass

                glue_edit(edit, key)

                panel.addWidget(label, row, 0)
                panel.addWidget(edit, row, 1)
                panel.addWidget(Label("(global)"), row, 2)
                row += 1

        note = Note(self.router.get_desc(svc_id))
        note.setFont(self._FONT_INFO)

        panel.addWidget(note, row, 0, 1, 3, Qt.AlignTop)
        panel.setRowStretch(row, 1)

    def _on_service_activated_set(self, svc_id, widget, options,
                                  use_options=None):
        """
        Based on the list of options and the user's last known options,
        restore the values of all input controls.
        """
        self.logger.debug("Restoring options for %s", svc_id)


        last_options = (use_options or
                        self.config['last_options'].get(svc_id, {}))

        vinputs = widget.findChildren(self._OPTIONS_WIDGETS)

        assert len(vinputs) == len(options)

        for i, opt in enumerate(options):
            vinput = vinputs[i]

            if isinstance(opt['values'], tuple):
                try:
                    val = last_options[opt['key']]
                    if not opt['values'][0] <= val <= opt['values'][1]:
                        raise ValueError

                except (KeyError, ValueError):
                    try:
                        val = opt['default']
                        if not opt['values'][0] <= val <= opt['values'][1]:
                            raise ValueError

                    except (KeyError, ValueError):
                        val = opt['values'][0]

                vinput.setValue(val)

            else:
                try:
                    idx = vinput.findData(last_options[opt['key']])
                    if idx < 0:
                        raise ValueError

                except (KeyError, ValueError):
                    try:
                        idx = vinput.findData(opt['default'])
                        if idx < 0:
                            raise ValueError

                    except (KeyError, ValueError):
                        idx = 0

                vinput.setCurrentIndex(idx)
        if use_options and 'addPara' in use_options:
            line = widget.findChild(QLineEdit, "addLine")
            line.setText(str(use_options['addPara']))



    def _on_preset_reset(self):
        """Sets preset dropdown back and disables delete button."""
        self._update_overview()

        # FIXME: The usage of inspect module on bundled version makes the app freeze.
        # So we don't use the original if-statement below.
        # It seemes there's no big difference even if we catch the value change events,
        # but we may recover the original behavior by passing the flag of value change
        # --------------
        # if next((True
        #          for frame in inspect.stack()
        #          if frame[3] == '_on_preset_activated'),
        #         False):
        #     return  # ignore value change events triggered by preset loads

        self.findChild(QPushButton, 'presets_delete').setDisabled(True)
        self.findChild(QComboBox, 'presets_dropdown').setCurrentIndex(0)


    def _on_preset_refresh(self, select=None):
        """Updates the view of the preset controls."""
        label = self.findChild(Label, 'presets_label')
        dropdown = self.findChild(QComboBox, 'presets_dropdown')
        delete = self.findChild(QPushButton, 'presets_delete')
        presets = self.config['presets']

        dropdown.clear()
        dropdown.addItem("Load Preset...    ")
        dropdown.insertSeparator(1)
        delete.setDisabled(True)

        if presets:
            label.hide()
            dropdown.show()
            dropdown.addItems(sorted(presets.keys(),
                                     key=lambda key: key.lower()))
            if select:
                if select is True:
                    # if one of the presets exactly match the svc_id and
                    # options that were just deserialized, then we want to
                    # select that one in the dropdown (this makes getting the
                    # same "preset" in the template helper dialog easier)
                    svc_id, options = self._get_service_values()
                    select = next(
                        (
                            name for name, preset in list(presets.items())
                            if svc_id == preset.get('service')
                            and not next(
                                (True for key, value in list(options.items())
                                 if preset.get(key) != options.get(key)),
                                False,
                            )
                        ),
                        None,
                    ) if options else None

                if select:
                    idx = dropdown.findText(select)
                    if idx > 0:
                        dropdown.setCurrentIndex(idx)
                        delete.setDisabled(False)
            delete.show()
        else:
            label.show()
            dropdown.hide()
            delete.hide()

    def _on_preset_save(self):
        """Saves the current service state back as a preset."""

        svc_id, options = self._get_service_values()

        assert "bad get_service_values() value", \
               not svc_id.startswith('group:') and options
        svc_name = self.findChild(QComboBox, 'service').currentText()

        name, okay = self._ask(
            title="Save a Preset Service Configuration",
            prompt=(
                "Please enter a name for <strong>%s</strong> with "
                "<strong>%s</strong> set to <kbd>%s</kbd>." %
                ((svc_name,) + list(options.items())[0])

                if len(options) == 1 else

                "Please enter a name for <strong>%s</strong> with the "
                "following:<br>%s" % (
                    svc_name,
                    "<br>".join(
                        "- <strong>%s:</strong> <kbd>%s</kbd>" % item
                        for item in sorted(options.items())
                    )
                )

                if len(options) > 1 else

                "Please enter a name for <strong>" + svc_name + "</strong>."
            ),
            default=(svc_name if not options.get('voice')
                     else "%s (%s)" % (svc_name, options['voice'])),
            parent=self,
        )

        name = okay and name.strip()
        if name:
            self.config['presets'] = dict(
                list(self.config['presets'].items()) +
                [(name, dict([('service', svc_id)] + list(options.items())))]
            )
            self._on_preset_refresh(select=name)

    def _on_preset_activated(self, idx):
        """Loads preset at given index and toggles delete button."""

        delete = self.findChild(QPushButton, 'presets_delete')

        if idx > 0:
            delete.setEnabled(True)
            name = self.findChild(QComboBox,
                                  'presets_dropdown').currentText()
            try:
                preset = self.config['presets'][name]
                svc_id = preset['service']
            except KeyError:
                self._alerts("%s preset is invalid." % name, self)
                return

            dropdown = self.findChild(QComboBox, 'service')
            idx = dropdown.findData(svc_id)
            if idx < 0:
                self._alerts(self.router.get_unavailable_msg(svc_id),
                             self)
                return

            dropdown.setCurrentIndex(idx)
            self._on_service_activated(idx, use_options=preset)
        else:
            delete.setEnabled(False)

    def _on_preset_delete(self):
        """Removes the currently selected preset from configuration."""

        presets = dict(self.config['presets'])
        try:
            del presets[self.findChild(QComboBox,
                                       'presets_dropdown').currentText()]
        except KeyError:
            pass
        else:
            self.config['presets'] = presets

        self._on_preset_refresh()

    def _on_preview(self):
        """
        Handle parsing the inputs and passing onto the router.
        """
        class Player:
            def __init__(self):
                self.mp = QMediaPlayer()
            def playMp3(self, path):
                content = QMediaContent(QUrl.fromLocalFile(path))
                self.mp.setMedia(content)
                self.mp.play()

        self.player = Player()

        svc_id, values = self._get_service_values()
        text_input, text_value = self._get_service_text()
        self._disable_inputs()

        # text_value = self._addon.strip.from_user(text_value)
        callbacks = dict(
            done=lambda: self._disable_inputs(False),
            okay=self.player.playMp3,
            fail=lambda exception: self._alerts(
                "Cannot preview the input phrase with these settings.\n\n%s" %
                str(exception),
                self,
            ),
            then=text_input.setFocus,
        )

        if svc_id.startswith('group:'):
            config = self.config
            self.router.group(text=text_value,
                                     group=config['groups'][svc_id[6:]],
                                     presets=config['presets'],
                                     callbacks=callbacks)
        else:
            self.router(svc_id=svc_id, text=text_value,
                               options=values, callbacks=callbacks)

    # Auxiliary ##############################################################

    def _disable_inputs(self, flag=True):
        """
        Mass disable (or enable if flag is False) all inputs, except the
        cancel button.
        """

        for widget in (
                widget
                for widget in self.findChildren(self._INPUT_WIDGETS)
                if widget.objectName() != 'cancel'
                and (not isinstance(widget, QComboBox) or
                     len(widget) > 1)
        ):
            widget.setDisabled(flag)

        if not flag:
            self.findChild(QPushButton, 'presets_delete').setEnabled(
                self.findChild(QComboBox,
                               'presets_dropdown').currentIndex() > 0
            )
            self.findChild(QPushButton, 'presets_save').setEnabled(
                self.findChild(QComboBox,
                               'service').currentIndex() < self._svc_count
            )

    def _get_service_values(self):
        """
        Return the service ID and a dict of all the options.
        """

        dropdown = self.findChild(QComboBox, 'service')
        idx = dropdown.currentIndex()
        svc_id = dropdown.itemData(idx)
        if svc_id.startswith('group:'):
            return svc_id, None

        vinputs = self.findChild(QStackedWidget, 'panels') \
            .widget(idx).findChildren(self._OPTIONS_WIDGETS)
        options = self.router.get_options(svc_id)

        assert len(options) == len(vinputs)
        from collections import OrderedDict
        optVal=OrderedDict()
        for i in range(len(options)):
            if isinstance(vinputs[i], QAbstractSpinBox):
                optVal[options[i]['key']]=vinputs[i].value()
            else:
                optVal[options[i]['key']]=vinputs[i].itemData(vinputs[i].currentIndex())


        line= self.findChild(QStackedWidget, 'panels') \
            .widget(idx).findChild(QLineEdit,"addLine")
        if line.text().strip()!="":
            try:
                d=eval(line.text())
                if(type(d).__name__=='dict'):
                    optVal['addPara']=d
            except:
                pass
        return svc_id, optVal

    def _get_service_text(self):
        """
        Return the text box and its phrase.
        """

        text_input = self.findChild(QWidget, 'text')
        try:
            text_value = text_input.text()
        except AttributeError:
            text_value = text_input.toPlainText()

        return text_input, text_value

    def _get_all(self):
        """
        Returns a dict of the options that need to be updated to
        remember and process the state of the form.
        """

        svc_id, values = self._get_service_values()
        return {
            'last_service': svc_id,
            'last_options': {
                **self.config['last_options'],
                **{svc_id: values}
            },
        } if values else dict(last_service=svc_id)

    def _banner(self):
        title = Label('AwesomeTTS Interface')
        title.setFont(self._FONT_TITLE)
        version = Label("Joytan version x.x.x")
        version.setFont(self._FONT_INFO)

        layout = QHBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(self._SPACING)
        layout.addStretch()
        layout.addWidget(version)

        return layout

    def _divider(self, orientation_style=QFrame.VLine):
        """
        Returns a divider.

        For subclasses, this method will be called automatically as part
        of the base class _ui() method.
        """

        frame = QFrame()
        frame.setFrameStyle(orientation_style | QFrame.Sunken)

        return frame

    def _on_voice_change(self):
        dropdown = self.findChild(QComboBox, 'service')
        idx = dropdown.currentIndex()
        svc_id = dropdown.itemData(idx)
        # if svc_id.startswith('group:'):
        #     return svc_id, None
        widge = self.findChild(QStackedWidget, 'panels') \
            .widget(idx)
        line=widge.findChild(QLineEdit,"addLine")
        if line!=None:
            line.setText("")






