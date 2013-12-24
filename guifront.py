from __future__ import division, print_function
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import (QAbstractItemView, pyqtSignal, Qt)
import guitools
import tools
from guitools import infoslot_ as slot_
from guitools import frontblocking as blocking

IS_INIT = False


def rrr():
    'Dynamic module reloading'
    import imp
    import sys
    print('[*front] reloading %s' % __name__)
    imp.reload(sys.modules[__name__])


class StreamStealer(QtCore.QObject):
    message = QtCore.pyqtSignal(str)
    flush_ =  QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(StreamStealer, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))

    def flush(self):
        self.flush_.emit()


def init_plotWidget(front):
    from _tpl.other.matplotlibwidget import MatplotlibWidget
    plotWidget = MatplotlibWidget(front.ui.centralwidget)
    plotWidget.setObjectName(guitools._fromUtf8('plotWidget'))
    plotWidget.setFocus()
    front.ui.root_hlayout.addWidget(plotWidget)
    return plotWidget


def init_ui(front):
    from _frontend.MainSkel import Ui_mainSkel
    ui = Ui_mainSkel()
    ui.setupUi(front)
    return ui


def connect_file_signals(front):
    ui = front.ui
    back = front.back
    ui.actionNew_Database.triggered.connect(back.new_database)
    ui.actionOpen_Database.triggered.connect(back.open_database)
    ui.actionSave_Database.triggered.connect(back.save_database)
    ui.actionImport_Img_file.triggered.connect(back.import_images_from_file)
    ui.actionImport_Img_dir.triggered.connect(back.import_images_from_dir)
    ui.actionQuit.triggered.connect(back.quit)


def connect_action_signals(front):
    ui = front.ui
    back = front.back
    ui.actionAdd_Chip.triggered.connect(back.add_chip)
    ui.actionNew_Chip_Property.triggered.connect(back.new_prop)
    ui.actionQuery.triggered.connect(back.query)
    ui.actionReselect_Ori.triggered.connect(back.reselect_ori)
    ui.actionReselect_ROI.triggered.connect(back.reselect_roi)
    ui.actionDelete_Chip.triggered.connect(back.delete_chip)
    ui.actionNext.triggered.connect(back.select_next)


def connect_option_signals(front):
    ui = front.ui
    back = front.back
    ui.actionLayout_Figures.triggered.connect(back.layout_figures)
    ui.actionPreferences.triggered.connect(back.edit_preferences)
    #ui.actionTogPts.triggered.connect(back.toggle_points)
    #ui.actionTogPlt.triggered.connect(back.toggle_plotWidget)


def connect_help_signals(front):
    ui = front.ui
    back = front.back
    msg_event = lambda title, msg: lambda: guitools.msgbox(title, msg)
    #ui.actionView_Docs.triggered.connect(back.view_docs)
    ui.actionView_DBDir.triggered.connect(back.view_database_dir)
    ui.actionView_Computed_Dir.triggered.connect(back.view_computed_dir)
    ui.actionView_Global_Dir.triggered.connect(back.view_global_dir)

    ui.actionAbout.triggered.connect(msg_event('About', 'hotspotter'))
    ui.actionDelete_computed_directory.triggered.connect(back.delete_computed_dir)
    ui.actionDelete_global_preferences.triggered.connect(back.delete_global_prefs)
    ui.actionDelete_Precomputed_Results.triggered.connect(back.delete_queryresults_dir)
    ui.actionDev_Mode_IPython.triggered.connect(back.dev_mode)
    ui.actionDeveloper_Reload.triggered.connect(back.dev_reload)
    #ui.actionWriteLogs.triggered.connect(back.write_logs)


def connect_batch_signals(front):
    ui = front.ui
    back = front.back
    #ui.actionBatch_Change_Name.triggered.connect(back.batch_rename)
    ui.actionPrecomputeChipsFeatures.triggered.connect(back.precompute_feats)
    ui.actionPrecompute_Queries.triggered.connect(back.precompute_queries)
    #ui.actionScale_all_ROIS.triggered.connect(back.expand_rois)
    #ui.actionConvert_all_images_into_chips.triggered.connect(back.convert_images2chips)
    #ui.actionAddMetaProp.triggered.connect(back.add_chip_property)
    #ui.actionAutoassign.triggered.connect(back.autoassign)


def connect_experimental_signals(front):
    ui = front.ui
    back = front.back
    ui.actionMatching_Experiment.triggered.connect(back.actionRankErrorExpt)
    ui.actionName_Consistency_Experiment.triggered.connect(back.autoassign)


class MainWindowFrontend(QtGui.QMainWindow):
    printSignal     = pyqtSignal(str)
    quitSignal      = pyqtSignal()
    selectGxSignal  = pyqtSignal(int)
    selectCidSignal = pyqtSignal(int)
    selectResSignal = pyqtSignal(int)
    changeCidSignal = pyqtSignal(int, str, str)
    querySignal = pyqtSignal()

    def __init__(front, back, use_plot_widget=True):
        super(MainWindowFrontend, front).__init__()
        #print('[*front] creating frontend')
        front.prev_tbl_item = None
        front.back = back
        front.ui = init_ui(front)
        if use_plot_widget:
            front.plotWidget = init_plotWidget(front)
        # Progress bar is not hooked up yet
        front.ui.progressBar.setVisible(False)
        front.connect_signals()
        front.steal_stdout()

    def steal_stdout(front):
        #import sys
        #front.ui.outputEdit.setPlainText(sys.stdout)
        import sys
        front.ostream = StreamStealer()
        front.ostream.message.connect(front.on_write)
        front.ostream.flush_.connect(front.on_flush)
        sys.stdout = front.ostream

    # TODO: this code is duplicated in back
    def user_info(front, *args, **kwargs):
        return guitools.user_info(front, *args, **kwargs)

    def user_input(front, *args, **kwargs):
        return guitools.user_input(front, *args, **kwargs)

    def user_option(front, *args, **kwargs):
        return guitools.user_option(front, *args, **kwargs)

    @slot_()
    def closeEvent(front, event):
        #front.printSignal.emit('[*front] closeEvent')
        event.accept()
        front.quitSignal.emit()

    def connect_signals(front):
        # Connect signals to slots
        back = front.back
        ui = front.ui
        # Frontend Signals
        front.printSignal.connect(back.backend_print)
        front.quitSignal.connect(back.quit)
        front.selectGxSignal.connect(back.select_gx)
        front.selectCidSignal.connect(back.select_cid)
        front.changeCidSignal.connect(back.change_chip_property)
        front.selectResSignal.connect(back.select_res_cid)
        front.querySignal.connect(back.query)

        # Menubar signals
        connect_file_signals(front)
        connect_action_signals(front)
        connect_option_signals(front)
        connect_batch_signals(front)
        #connect_experimental_signals(front)
        connect_help_signals(front)
        #
        # Gui Components
        # Tables Widgets
        ui.chip_TBL.itemClicked.connect(front.chip_tbl_clicked)
        ui.chip_TBL.itemChanged.connect(front.chip_tbl_changed)
        ui.image_TBL.itemClicked.connect(front.img_tbl_clicked)
        ui.image_TBL.itemChanged.connect(front.img_tbl_changed)
        ui.res_TBL.itemClicked.connect(front.res_tbl_clicked)
        ui.res_TBL.itemChanged.connect(front.res_tbl_changed)
        # Tab Widget
        ui.tablesTabWidget.currentChanged.connect(front.change_view)
        ui.chip_TBL.sortByColumn(0, Qt.AscendingOrder)
        ui.res_TBL.sortByColumn(0, Qt.AscendingOrder)
        ui.image_TBL.sortByColumn(0, Qt.AscendingOrder)

    def print(front, msg):
        print('[*front*] ' + msg)
        #front.printSignal.emit('[*front] ' + msg)

    #def popup(front, pos):
        #for i in front.ui.image_TBL.selectionModel().selection().indexes():
            #front.print(repr((i.row(), i.column())))
        #menu = QtGui.QMenu()
        #action1 = menu.addAction("action1")
        #action2 = menu.addAction("action2")
        #action3 = menu.addAction("action2")
        #action = menu.exec_(front.ui.image_TBL.mapToGlobal(pos))
        #front.print('action = %r ' % action)

    @slot_(bool)
    def setPlotWidgetEnabled(front, flag):
        flag = bool(flag)
        #front.printDBG('setPlotWidgetEnabled(%r)' % flag)
        front.plotWidget.setVisible(flag)

    @slot_(bool)
    def setEnabled(front, flag):
        #front.printDBG('setEnabled(%r)' % flag)
        ui = front.ui
        # Enable or disable all actions
        for uikey in ui.__dict__.keys():
            if uikey.find('action') == 0:
                ui.__dict__[uikey].setEnabled(flag)

        # The following options are always enabled
        ui.actionOpen_Database.setEnabled(True)
        ui.actionNew_Database.setEnabled(True)
        ui.actionQuit.setEnabled(True)
        ui.actionAbout.setEnabled(True)
        ui.actionView_Docs.setEnabled(True)
        ui.actionDelete_global_preferences.setEnabled(True)

        # The following options are no implemented. Disable them
        ui.actionConvert_all_images_into_chips.setEnabled(False)
        ui.actionBatch_Change_Name.setEnabled(False)
        ui.actionScale_all_ROIS.setEnabled(False)
        ui.actionWriteLogs.setEnabled(False)
        ui.actionAbout.setEnabled(False)
        ui.actionView_Docs.setEnabled(False)

    def _populate_table(front, tbl, col_headers, col_editable, row_list, row2_datatup):
        #front.printDBG('_populate_table()')
        hheader = tbl.horizontalHeader()

        def set_header_context_menu(hheader):
            hheader.setContextMenuPolicy(Qt.CustomContextMenu)
            # TODO: for chip table: delete metedata column
            opt2_callback = [
                ('header', lambda: print('finishme')),
                ('cancel', lambda: print('cancel')), ]
            # HENDRIK / JASON TODO:
            # I have a small right-click context menu working
            # Maybe one of you can put some useful functions in these?
            popup_slot = guitools.popup_menu(tbl, opt2_callback)
            hheader.customContextMenuRequested.connect(popup_slot)

        def set_table_context_menu(tbl):
            tbl.setContextMenuPolicy(Qt.CustomContextMenu)
            # TODO: How do we get the clicked item on a right click?
            opt2_callback = [
                ('Query', front.querySignal.emit), ]
                #('item',  lambda: print('finishme')),
                #('cancel', lambda: print('cancel')), ]

            popup_slot = guitools.popup_menu(tbl, opt2_callback)
            tbl.customContextMenuRequested.connect(popup_slot)
        #set_header_context_menu(hheader)
        set_table_context_menu(tbl)

        sort_col = hheader.sortIndicatorSection()
        sort_ord = hheader.sortIndicatorOrder()
        tbl.sortByColumn(0, Qt.AscendingOrder)  # Basic Sorting
        tblWasBlocked = tbl.blockSignals(True)
        tbl.clear()
        tbl.setColumnCount(len(col_headers))
        tbl.setRowCount(len(row_list))
        tbl.verticalHeader().hide()
        tbl.setHorizontalHeaderLabels(col_headers)
        tbl.setSelectionMode( QAbstractItemView.SingleSelection)
        tbl.setSelectionBehavior( QAbstractItemView.SelectRows)
        tbl.setSortingEnabled(False)
        for row in iter(row_list):
            data_tup = row2_datatup[row]
            for col, data in enumerate(data_tup):
                item = QtGui.QTableWidgetItem()

                if tools.is_int(data):
                    item.setData(Qt.DisplayRole, int(data))
                elif tools.is_float(data):
                    item.setData(Qt.DisplayRole, float(data))
                else:
                    item.setText(str(data))

                item.setTextAlignment(Qt.AlignHCenter)
                if col_editable[col]:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    #print(item.getBackground())
                    item.setBackground(QtGui.QColor(250, 240, 240))
                else:
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                tbl.setItem(row, col, item)
        tbl.setSortingEnabled(True)
        tbl.sortByColumn(sort_col, sort_ord)  # Move back to old sorting
        tbl.show()
        tbl.blockSignals(tblWasBlocked)

    @slot_(str, list, list, list, list)
    @blocking
    def populate_tbl(front, table_name, col_headers, col_editable,
                     row_list, row2_datatup):
        table_name = str(table_name)
        #front.printDBG('populate_tbl(%s)' % table_name)
        try:
            tbl = front.ui.__dict__['%s_TBL' % table_name]
        except KeyError:
            valid_table_names = [key for key in front.ui.__dict__.keys()
                                 if key.find('_TBL') >= 0]
            msg = '\n'.join(['Invalid table_name = %s_TBL' % table_name,
                             'valid names:\n  ' + '\n  '.join(valid_table_names)])
            raise Exception(msg)
        front._populate_table(tbl, col_headers, col_editable, row_list, row2_datatup)

    def isItemEditable(self, item):
        return int(Qt.ItemIsEditable & item.flags()) == int(Qt.ItemIsEditable)

    def get_tbl_header(front, tbl, col):
        return str(tbl.horizontalHeaderItem(col).text())

    def get_tbl_cid(front, tbl, row, cid_col):
        cid_header = front.get_tbl_header(tbl, cid_col)
        assert cid_header == 'Chip ID', 'Header is %s' % cid_header
        cid = int(tbl.item(row, cid_col).text())
        return cid

    def get_tbl_gx(front, tbl, row, gid_col):
        gid_header = front.get_tbl_header(tbl, gid_col)
        assert gid_header == 'Image Index', 'Header is %s' % gid_header
        gid = int(tbl.item(row, gid_col).text())
        return gid

    def get_chiptbl_header(front, col):
        return front.get_tbl_header(front.ui.chip_TBL, col)

    def get_imgtbl_header(front, col):
        return front.get_tbl_header(front.ui.image_TBL, col)

    def get_restbl_header(front, col):
        return front.get_tbl_header(front.ui.res_TBL, col)

    def get_restbl_cid(front, row):
        'Gets chip id from result table'
        col = front.back.restbl_headers.index('Chip ID')
        return front.get_tbl_cid(front.ui.res_TBL, row, col)

    def get_chiptbl_cid(front, row):
        'Gets chip id from chip table'
        col = front.back.chiptbl_headers.index('Chip ID')
        return front.get_tbl_cid(front.ui.chip_TBL, row, col)

    def get_imgtbl_gx(front, row):
        'Gets image index from image'
        col = front.back.imgtbl_headers.index('Image Index')
        return front.get_tbl_gx(front.ui.image_TBL, row, col)

    # Table Changed Functions
    @slot_(QtGui.QTableWidgetItem)
    def img_tbl_changed(front, item):
        front.print('img_tbl_changed()')
        raise NotImplementedError('img_tbl_changed()')

    @slot_(QtGui.QTableWidgetItem)
    def chip_tbl_changed(front, item):
        'Chip Table Chip Changed'
        front.print('chip_tbl_changed()')
        row, col = (item.row(), item.column())
        # Get selected chipid
        sel_cid = front.get_chiptbl_cid(row)
        # Get the changed property key and value
        new_val = str(item.text()).replace(',', ';;')  # sanatize for csv
        # Get which column is being changed
        header_lbl = front.get_chiptbl_header(col)
        # Tell the back about the change
        front.changeCidSignal.emit(sel_cid, header_lbl, new_val)

    @slot_(QtGui.QTableWidgetItem)
    def res_tbl_changed(front, item):
        'Result Table Chip Changed'
        front.print('res_tbl_changed()')
        row, col = (item.row(), item.column())
        sel_cid  = front.get_restbl_cid(row)  # The changed row's chip id
        # Get which column is being changed
        header_lbl = front.get_restbl_header(col)
        # The changed items's value
        new_val = str(item.text()).replace(',', ';;')  # sanatize for csv
        # Tell the back about the change
        front.changeCidSignal.emit(sel_cid, header_lbl, new_val)

    # Table Clicked Functions
    @slot_(QtGui.QTableWidgetItem)
    def img_tbl_clicked(front, item):
        'Image Table Clicked'
        row = item.row()
        front.print('img_tbl_clicked(%r)' % (row))
        if item == front.prev_tbl_item:
            return
        front.prev_tbl_item = item
        # Get the clicked Image ID
        sel_gx = front.get_imgtbl_gx(row)
        front.selectGxSignal.emit(sel_gx)

    @slot_(QtGui.QTableWidgetItem)
    def chip_tbl_clicked(front, item):
        'Chip Table Clicked'
        row, col = (item.row(), item.column())
        front.print('chip_tbl_clicked(%r, %r)' % (row, col))
        if front.isItemEditable(item):
            front.print('[front] does not select when clicking editable column')
            return
        if item == front.prev_tbl_item:
            return
        front.prev_tbl_item = item
        # Get the clicked Chip ID (from chip tbl)
        sel_cid = front.get_chiptbl_cid(row)
        front.selectCidSignal.emit(sel_cid)

    @slot_(QtGui.QTableWidgetItem)
    def res_tbl_clicked(front, item):
        'Result Table Clicked'
        row, col = (item.row(), item.column())
        front.print('res_tbl_clicked(%r, %r)' % (row, col))
        if front.isItemEditable(item):
            front.print('[front] does not select when clicking editable column')
            return
        if item == front.prev_tbl_item:
            return
        front.prev_tbl_item = item
        # Get the clicked Chip ID (from res tbl)
        sel_cid = front.get_restbl_cid(row)
        front.selectResSignal.emit(sel_cid)

    @slot_(int)
    def change_view(front, new_state):
        front.print('change_view()')
        prevBlock = front.ui.tablesTabWidget.blockSignals(True)
        front.ui.tablesTabWidget.blockSignals(prevBlock)

    @slot_(str, str, list)
    def modal_useroption(front, msg, title, options):
        pass

    @slot_(str)
    def on_write(front, message):
        front.ui.outputEdit.moveCursor(QtGui.QTextCursor.End)
        front.ui.outputEdit.insertPlainText(message)

    @slot_()
    def on_flush(front):
        pass
        #front.ui.outputEdit.moveCursor(QtGui.QTextCursor.End)
        #front.ui.outputEdit.insertPlainText(message)
