#!/bin/python
"""
Hello World, but with more meat.
"""

import wx
from os import listdir
from os.path import isfile, join

# menu item ids
openItemId = 100
saveItemId = 101
closeItemId = 102



class MapEditor(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MapEditor, self).__init__(*args, **kw)

        # init vars
        self.contentNotSaved = False
        self.mapHeight = 0
        self.mapWidth = 0
        self.sceneNum = 0
        self.sceneData = []
        self.mapData = []
        self.sceneSize = [40,22]
        self.currentPos = [0,0]

        self.tilePath = "D:\\Documents\\Programming\\Projects\\the-jumping-game\\resources\\tiles\\"
        self.tileList = {}

        self.brush = 0

        self.selectedBox = [0,0]
        self.mapGridItems = {}
        
        # load the tiles
        self.tileNames = [f for f in listdir(self.tilePath) if isfile(join(self.tilePath, f))]
        for f in self.tileNames:
            key = int(f.split('.')[0])
            self.tileList[key] = wx.Bitmap(join(self.tilePath, f), wx.BITMAP_TYPE_ANY)
        
        # create a panel in the frame
        self.panel = wx.Panel(self)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.initUI()
        self.SetSize(1000,700)
        self.Centre()
       
        
        
    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(openItemId, "&Open\tCtrl-O","Open File")
        saveItem = fileMenu.Append(saveItemId, "&Save\tCtrl-S", "Save File")
        saveasItem = fileMenu.Append(wx.ID_ANY, "Save As", "Save File")
        closeItem = fileMenu.Append(closeItemId, "&Close\tCtrl-C", "Close File")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # help menu
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # make menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnOpen, openItem)
        self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, saveasItem)
        self.Bind(wx.EVT_MENU, self.OnClose, closeItem)

        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def initUI(self):
        # TODO: font

        bigBox = wx.BoxSizer(wx.HORIZONTAL)

        buttonBox = wx.BoxSizer(wx.VERTICAL) 
        self.bmpInUse = wx.StaticBitmap(self.panel, wx.ID_ANY, self.tileList[self.brush])
        buttonBox.Add(self.bmpInUse, flag=wx.BOTTOM, proportion = 2, border=10)
        combo = wx.ComboBox(self.panel, choices = self.tileNames, style=wx.CB_READONLY)
        combo.Bind(wx.EVT_COMBOBOX, self.OnTileSelect)
        buttonBox.Add(combo, flag=wx.BOTTOM, border=10)

        self.listBox = wx.ListBox(self.panel)
        # TODO: move this to LoadData
        for li in self.sceneData:
            self.listBox.Append(li)
        buttonBox.Add(self.listBox, flag=wx.ALL|wx.EXPAND, border=10)
        btn1 = wx.Button(self.panel, label='Add scene', size=(100,50))
        buttonBox.Add(btn1, proportion = 1, flag=wx.BOTTOM | wx.EXPAND, border=10)
        btn2 = wx.Button(self.panel, label='Delete scene', size=(100,50))
        buttonBox.Add(btn2, proportion = 1, flag=wx.BOTTOM | wx.EXPAND, border=10)
        btn1.Bind(wx.EVT_BUTTON, self.OnAddScene)
        btn2.Bind(wx.EVT_BUTTON, self.OnDelScene)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSceneShow)
        bigBox.Add(buttonBox, proportion = 2)

        mapGrid = wx.GridSizer(rows = self.sceneSize[1], cols = self.sceneSize[0], gap = (0,0))
        for y in range(self.sceneSize[1]):
            for x in range(self.sceneSize[0]):
                self.mapGridItems[(x,y)] = wx.StaticBitmap(self.panel, wx.ID_ANY, self.tileList[self.brush])
                mapGrid.Add(self.mapGridItems[(x,y)], 0, wx.EXPAND)
        bigBox.Add(mapGrid, proportion = 15)

        self.panel.SetSizer(bigBox)

    # events
    def OnExit(self, event):
        if self.contentNotSaved:
            dlg = wx.MessageDialog(self, "Exit without saving?", "Confirm Exit", wx.OK|wx.CANCEL)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Close(True)
        else:
            self.Close(True)

    def OnOpen(self, event):

        if self.contentNotSaved:
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                            wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open map data file", defaultDir="D:\\Documents\\Programming\\Projects\\the-jumping-game\\resources", 
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            self.pathname = fileDialog.GetPath()
            try:
                with open(self.pathname, 'r') as file:
                    self.LoadData(file)
                    file.close()
                    self.contentNotSaved = True
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def OnSave(self, event):
        try:
            with open(self.pathname, 'w') as file:
                self.doSaveData(file)
                file.close()
                self.contentNotSaved = False
        except IOError:
            wx.LogError("Cannot open file '%s'." % newfile)

    def OnClose(self, event):
        if self.contentNotSaved:
            dlg = wx.MessageDialog(self, "Close without saving?", "Confirm Exit", wx.OK|wx.CANCEL)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.resetApp()

    def OnSaveAs(self, event):

        with wx.FileDialog(self, "Save map data file", wildcard="data files (*.data)|*.data",
                        defaultDir="D:\\Documents\\Programming\\Projects\\the-jumping-game\\resources",
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    self.doSaveData(file)
                    file.close()
                    self.contentNotSaved = False
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def OnTileSelect(self, event):
        i = event.GetString()
        self.brush = int(i.split('.')[0])
        self.bmpInUse.SetBitmap(self.tileList[self.brush])

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)

    # list box events
    def OnAddScene(self, event):
        if len(self.selectedBox) == 2:
            text = '%d %d %d %d' % self.currentPos[0], self.currentPos[1], self.selectedBox[0], self.selectedBox[1]
            self.listBox.Append(text)
            self.sceneData.append(text)

    def OnDelScene(self, event):
        sel = self.listBox.GetSelection()
        if sel != -1:
            text = self.listBox.GetString(sel)
            self.listBox.Delete(sel)
            if text in self.sceneData:
                self.sceneData.remove(text)

    def OnSceneShow(self, event):
        sel = event.GetSelection()
        text = event.GetString()
        print(text.split())
        self.currentPos[0] = int(text.split()[0])
        self.currentPos[1] = int(text.split()[1])
        self.selectedBox[0] = int(text.split()[2])
        self.selectedBox[1] = int(text.split()[3])
        self.render()

    # functions
    def doSaveData(self, file):
        file.write("%d %d %d\n" % (self.mapWidth, self.mapHeight, self.sceneNum))
        for i in range(self.sceneNum):
            for k in range(len(self.sceneData[i])):
                file.write(self.sceneData[i] + '\n')
        for i in range():
            for j in range(self.mapWidth):
                if j < self.mapWidth-1:
                    file.write("%d " % self.mapData[i][j])
                else:
                    if i <  - 1:
                        file.write("%d\n" % self.mapData[i][j])
                    else:
                        file.write("%d" % self.mapData[i][j])

    def LoadData(self, file):
        lines_list = file.readlines()
        self.mapWidth, self.mapHeight, self.sceneNum = (int(val) for val in lines_list[0].split())
        self.sceneData = [line[:-1] for line in lines_list[1:self.sceneNum+1]]
        self.mapData = [[int(val) for val in line.split()] for line in lines_list[self.sceneNum+1:]]
        self.render()

    def resetApp(self):
        self.contentNotSaved = False
        self.mapHeight = 0
        self.mapWidth = 0
        self.sceneNum = 0
        self.sceneData = []
        self.mapData = []
        self.render()
    
    def render(self):
        for li in self.sceneData:
            self.listBox.Append(li)
        for y in range(self.sceneSize[1]):
            for x in range(self.sceneSize[0]):
                item = self.mapData[y+self.currentPos[1]][x+self.currentPos[0]]
                self.mapGridItems[(x,y)].SetBitmap(self.tileList[item])


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MapEditor(None, title='MapEditor')
    frm.Show()
    app.MainLoop()