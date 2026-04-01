# ===========================
# 5D
# ===========================
# rw511
# 2022 
# ===========================

from PyQt5.QtCore import QDateTime, Qt, QTimer, QPersistentModelIndex
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QHeaderView, QTableWidgetItem, QStackedWidget,
        QStackedLayout,
        QFileDialog,
        QDoubleSpinBox,
        QAbstractScrollArea,
        QTableView,
        QListWidget)
        
from PyQt5.QtGui import QFont, QBrush, QColor, QIcon, QPixmap

import os
from datetime import datetime # For date conversion
        
                
class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)        
        

        # Layout for GUI
        layout_main = QGridLayout()
        self.setLayout(layout_main)
        
        # Main table for data
        self.createMainDataTable()
        
        # Layout to hold the buttons
        self.createLayout_buttons()
        
        # Get the current folder
        self.cwd = os.getcwd()
            
        layout_main.addWidget(QLabel(self.cwd ), 0, 0)
        layout_main.addWidget(self.mainDataTable, 1, 0)
        layout_main.addWidget(self.buttons_box, 1, 1)
        
        # Connect button hooks
        self.button_quit.clicked.connect(lambda: sys.exit(0)) 
        self.button_refresh.clicked.connect(lambda event:self.refreshButtonClicked()) 
        self.button_rewind.clicked.connect(lambda event:self.rewindButtonClicked()) 
        
    def cancelButtonClicked(self, dialog):
        
        dialog.reject()
        
    # Initiates the rewinding/deletion process
    def rewindButtonClicked(self):
        
        # Store the selected rows of the table
        # These rows (indices) are the ones that will be rewound
        rows = (set(index.row() for index in self.mainDataTable.selectedIndexes()))
        
        # Get the corresponding decks from these selected rows
        selectedDecks = [] 
        for row in rows:
            selectedDecks.append(self.mainDataTable.item(row, 0).text())            
        
        # Show these decks to the user to get them to confirm they want to rewind them
        self.userCheck(selectedDecks, rows)
        
    # Dialog where the user will see the decks ready to be rewound
    def userCheck(self, decksToBeDeleted, rows):
    
        userConfirmation = QDialog()   
        
        # Display only the decks to be deleted (those that were highlighted before)
        deletionList = QListWidget()
        for deck in decksToBeDeleted:
            deletionList.addItem(deck)        
        
        # Widgets 
        self.button_delete  = QPushButton("Delete Files")
        self.button_close   = QPushButton("Close")     

        # Connect button hooks        
        self.button_delete.clicked.connect(lambda event:self.deleteButtonClicked(rows))    
        self.button_close.clicked.connect(lambda event:self.cancelButtonClicked(userConfirmation))        
        
        # Layout
        layout         = QGridLayout()
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_delete)
        layout_buttons.addWidget(self.button_close)        
        
        label = QLabel("There is no option to recover the files after you click ok.")
        layout.addWidget(label, 0, 0)
        layout.addWidget(deletionList, 1, 0)
        layout.addLayout(layout_buttons, 2, 0)
        
        # Additional settings for the dialog
        userConfirmation.setWindowTitle("Are you sure you want to delete all data save saves after time zero for the following decks?") 
        #userConfirmation.setWindowIcon(QIcon('5D.png'))     
        userConfirmation.setLayout(layout)
        userConfirmation.resize(600,300)        
        userConfirmation.exec_() 
    
    # Called when the delete button is clicked
    def deleteButtonClicked(self, rows):
    
        # Apply the file removal only on the decks of the selected rows
        for row in rows:
            self.removeH5Files(self.XXXXDeckPaths[row])
        
        # Refresh the table once the deletion has happened
        self.refreshButtonClicked()
    
    # The function that does the actual deletion
    def removeH5Files(self, deckWithPath):
        
        # Only removes .h5 file extensions
        fileEnding      = '.h5'
        
        # 0.h5 is a protected file and won't be deleted
        protectedFile   =  '0.h5'
        
        # Storing so we can redirect to log file
        original_stdout = sys.stdout 
        
        with open('deletedFiles.log', 'a+') as logFile:
            
            # Redirect stdout to our file
            sys.stdout = logFile
            
            # Loop over all the selected files from the table
            for file in os.listdir(deckWithPath):
            
                # Need to use the full file path to remove with os
                fileAndPath = os.path.join(deckWithPath , file)
                
                # Verify the file is a .h5 file and isn't 0.h5
                if(fileAndPath[-3:] == fileEnding) and (file != protectedFile):
                
                    try:
                        os.remove(fileAndPath)
                        print(fileAndPath + '\\' + file + ' deleted')  
                        
                    except OSError:
                        print("Rewind failed. Could not remove file " + file)    

        # Put stdout back to how it was originally
        sys.stdout = original_stdout

    # Refreshes the main window
    def refreshButtonClicked(self):
        
        # Lists to store all the data
        self.XXXXDeckPaths = []
        self.XXXXDeckNames = []
        self.XXXXDeckSaves = []
        self.XXXXDeckSizes = []
        self.XXXXDeckDates = []
        
        # Get all the relevant h5 data 
        self.getXXXXDecks(self.cwd, self.XXXXDeckPaths, self.XXXXDeckNames, self.XXXXDeckSaves, self.XXXXDeckSizes, self.XXXXDeckDates)
        
        # Clear the current table
        self.clearCurrentTable(self.mainDataTable)
                
        # Update with new data      
        self.populateMainDataTable(self.XXXXDeckNames, self.XXXXDeckSaves, self.XXXXDeckSizes, self.XXXXDeckDates)        
        
           
    # Clear table contents
    def clearCurrentTable(self, table):

        table.setRowCount(0)
        table.clearContents()   

    # Get the size of the passed directory
    def getDirSize(self, start_path = '.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        
        # os.getsize returns in bytes so setting to gigabytes
        return total_size/1e9
                
    # Get all XXXX decks from the current path
    def getXXXXDecks(self, path, deckPaths, deckNames, numSaves, deckSizes, deckDates):
        
        # Will pull in any folder with this suffix
        XXXXDeckEndString = '_data'
        
        for root, dirs, files in os.walk(path, topdown = False):
            
            #for dir in dirs:
                
            if(root[-5:] == XXXXDeckEndString):
                #print(dir + " is an XXXX deck")
                deckPaths.append(root)
                deckSizes.append(self.getDirSize(root))
                unixTime = os.stat(root).st_ctime
                deckDates.append(str(datetime.utcfromtimestamp(unixTime)))      
                deckNames.append(os.path.basename(root))
                numSaves.append(len(os.listdir(root)))                
                
    # Creates a table of the number of rows and columns specified
    def createTable(self, rows, columns, headers):
        
        tableWidget = QTableWidget(rows, columns)
        
        # Column options
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.setHorizontalHeaderLabels(headers)
        tableWidget.horizontalHeader().setFont(QFont('Times', 8))
        tableWidget.horizontalHeader().setHighlightSections(False)
        tableWidget.setStyleSheet( "QTableWidget ::section {border: 1px outset #161618;}" );
        
        # Row options
        tableWidget.verticalHeader().setVisible(False);
                
        return tableWidget     
        
    # Creates main data table
    # This will store the data seen by the user
    # DeckName; Timesteps; Size (GB); Date created
    def createMainDataTable(self):
        
        cwd = os.getcwd()
        headers = ["Deck name", "No. data saves", "Total size (GB)", "Date 0.h5 created"]
        self.mainDataTable = self.createTable(1,4, headers)        
        self.mainDataTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.mainDataTable.setSelectionBehavior(QTableView.SelectRows)
    
    # Inserts the passed data into the table, by row
    def populateMainDataTable(self, deckNames, numSaves, deckSize, dateCreated):
    
        for i in range(len(deckNames)):
        
            self.mainDataTable.insertRow(self.mainDataTable.rowCount())
            self.mainDataTable.setItem(i, 0, QTableWidgetItem(deckNames[i]))
            self.mainDataTable.setItem(i, 1, QTableWidgetItem(str(numSaves[i])))
            self.mainDataTable.setItem(i, 2, QTableWidgetItem(str(round(deckSize[i],2))))
            self.mainDataTable.setItem(i, 3, QTableWidgetItem(str(dateCreated[i])))
            self.mainDataTable.resizeColumnsToContents()
            
    
    # Creates the buttons and the layout  for them
    def createLayout_buttons(self):
        
        self.buttons_box = QGroupBox()
        
        # Widgets
        button_x_length = 75
        button_y_length = 30
        
        self.button_refresh = QPushButton("Refresh")     
        self.button_rewind  = QPushButton("Rewind")       
        self.button_quit    = QPushButton("Quit")
        
        self.button_refresh.setMinimumSize(button_x_length,button_y_length) 
        self.button_rewind .setMinimumSize(button_x_length,button_y_length) 
        self.button_quit   .setMinimumSize(button_x_length,button_y_length) 
       
        # Layout
        layout_buttons = QVBoxLayout()
        
        layout_buttons.addWidget(self.button_refresh)
        layout_buttons.addWidget(self.button_rewind)
        layout_buttons.addWidget(self.button_quit)
        
        self.buttons_box.setLayout(layout_buttons)
        
        self.buttons_box.setMinimumSize(100,300)
        
if __name__ == '__main__':
    
    import sys 
    
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.setWindowTitle("5D")    
    # gallery.setWindowIcon(QIcon('5D.png'))
    gallery.show()
    gallery.resize(900,600)
    sys.exit(app.exec_())
