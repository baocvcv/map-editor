#!/bin/python
"""
Hello World, but with more meat.
"""

import wx
import numpy as np
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
        self.isFileOpen = False
        self.mapHeight = 0
        self.mapWidth = 0
        self.sceneNum = 0
        self.sceneData = []
        self.mapData = np.empty(0)
        self.sceneSize = [40,22]
        self.currentPos = [0,0]

        self.tilePath = "D:\\Documents\\Programming\\Projects\\the-jumping-game\\resources\\tiles\\"
        self.tileList = {}
        self.tileSize = 30
        self.tileOriSize = 128

        self.brush = 0

        self.selectedBox = [0,0]
        self.heroSize = [290,500]
        self.bkgSize = [1280,720]
        
        # load the tiles
        self.tileNames = [f for f in listdir(self.tilePath) if isfile(join(self.tilePath, f))]
        for f in self.tileNames:
            key = int(f.split('.')[0])
            self.tileList[key] = wx.Bitmap(join(self.tilePath, f), wx.BITMAP_TYPE_ANY)
        self.bmpHero = wx.Bitmap('D:\\Documents\\Programming\\Projects\\the-jumping-game\\resources\\hero.png', wx.BITMAP_TYPE_ANY)
        self.bmpBkg = wx.Bitmap('D:\\Documents\\Programming\\Projects\\the-jumping-game\\resources\\bkg.png', wx.BITMAP_TYPE_ANY)
        
        # create ui
        self.mapDrawer = MapDrawing(self)
        self.panel = wx.Panel(self)
        self.makeMenuBar()
        self.CreateStatusBar()

        self.initUI()
        self.SetSize(200,700)
        self.SetPosition((50,100))
        self.mapDrawer.Show()
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        newItem = fileMenu.Append(wx.ID_ANY, "&New\tCtrl-N", "New File")
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
        self.Bind(wx.EVT_MENU, self.OnNew, newItem)

        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def initUI(self):

        buttonBox = wx.BoxSizer(wx.VERTICAL) 
        self.bmpInUse = wx.StaticBitmap(self.panel, wx.ID_ANY, self.tileList[self.brush])
        buttonBox.Add(self.bmpInUse, flag=wx.ALIGN_CENTER)
        combo = wx.ComboBox(self.panel, choices = self.tileNames, style=wx.CB_READONLY)
        combo.Bind(wx.EVT_COMBOBOX, self.OnTileSelect)
        buttonBox.Add(combo, flag=wx.ALL | wx.EXPAND, border=10)

        self.listBox = wx.ListBox(self.panel, size=(150,150))
        buttonBox.Add(self.listBox, flag=wx.ALL|wx.EXPAND, border=10)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.OnSceneShow)

        btn1 = wx.Button(self.panel, label='Add scene', size=(80,30))
        btn2 = wx.Button(self.panel, label='Delete scene', size=(80,30))
        wrap = wx.BoxSizer(wx.HORIZONTAL)
        wrap.Add(btn1, proportion = 1)
        wrap.Add(btn2, proportion = 1)
        buttonBox.Add(wrap, flag=wx.BOTTOM|wx.EXPAND, border=20)
        btn1.Bind(wx.EVT_BUTTON, self.OnAddScene)
        btn2.Bind(wx.EVT_BUTTON, self.OnDelScene)

# TODO: add a all the controls: change width and height
        
        st1 = wx.StaticText(self.panel, label='Map Width', style=wx.ALIGN_LEFT)
        self.inputWidth = wx.SpinCtrl(self.panel, value='0')
        self.inputWidth.SetRange(0, 1000)
        st2 = wx.StaticText(self.panel, label='Map Height', style=wx.ALIGN_LEFT)
        self.inputHeight = wx.SpinCtrl(self.panel, value='0')
        self.inputHeight.SetRange(0, 1000)
        wrapWid = wx.BoxSizer(wx.HORIZONTAL)
        wrapWid.Add(st1, proportion=1, flag=wx.RIGHT, border=14)
        wrapWid.Add(self.inputWidth, proportion=3)
        wrapHei = wx.BoxSizer(wx.HORIZONTAL)
        wrapHei.Add(st2, proportion=1, flag=wx.RIGHT, border=10)
        wrapHei.Add(self.inputHeight, proportion=3)
        buttonBox.Add(wrapWid, flag=wx.BOTTOM, border=10)
        buttonBox.Add(wrapHei, flag=wx.BOTTOM, border=10)

        btn3 = wx.Button(self.panel, label='Confirm')
        buttonBox.Add(btn3, flag=wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, border=15)
        btn3.Bind(wx.EVT_BUTTON, self.OnChangeMapDim)

        btn = {}
        btn[0] = wx.Button(self.panel, label='Up')
        btn[1] = wx.Button(self.panel, label='Left')
        btn[2] = wx.Button(self.panel, label='Right')
        btn[3] = wx.Button(self.panel, label='Down')
        wrap2 =  wx.BoxSizer(wx.HORIZONTAL)
        wrap3 =  wx.BoxSizer(wx.HORIZONTAL)
        wrap2.Add(btn[0], proportion = 1)
        wrap2.Add(btn[1], proportion = 1)
        wrap3.Add(btn[2], proportion = 1)
        wrap3.Add(btn[3], proportion = 1)
        buttonBox.Add(wrap2)
        buttonBox.Add(wrap3, flag=wx.BOTTOM, border=10)
        for i in range(4):
            btn[i].Bind(wx.EVT_BUTTON, self.MapMove)

        self.panel.SetSizer(buttonBox)

    # events
    def OnExit(self, event):
        if self.contentNotSaved:
            dlg = wx.MessageDialog(self, "Exit without saving?", "Confirm Exit", wx.OK|wx.CANCEL)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                if self.mapDrawer:
                    self.mapDrawer.Close(True)
                self.Destroy()
        else:
            if self.mapDrawer:
                    self.mapDrawer.Close(True)
            self.Destroy()

    def OnNew(self, event):
        if self.contentNotSaved:
            if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                            wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return
        self.isFileOpen = True
        self.mapHeight = 44
        self.mapWidth = 120
        self.sceneNum = 0
        self.sceneData = []
        self.mapData = np.zeros((self.mapHeight, self.mapWidth))
        self.listBox.Clear()
        self.render(1)

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
                    self.isFileOpen = True
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def OnSave(self, event):
        if not self.isFileOpen:
            return
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
                self.isFileOpen = False
        else:
            self.resetApp()
            self.isFileOpen = False

    def OnSaveAs(self, event):
        if not self.isFileOpen:
            return
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
                    self.isFileOpen = False
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def OnChangeMapDim(self, event):
        mapWidth = self.inputWidth.GetValue()
        mapHeight = self.inputHeight.GetValue()
        if len(self.mapData) < mapHeight:
            self.mapData[self.mapHeight-1:mapHeight][:] = 0
        if len(self.mapData[0]) < mapWidth:
            self.mapData[:][self.mapWidth-1:mapWidth] = 0
        self.mapWidth = self.inputWidth.GetValue()
        self.mapHeight = self.inputHeight.GetValue()
        self.ShowMapDim()

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
            text = '%d %d %d %d' % (self.selectedBox[0], self.selectedBox[1], self.currentPos[0], self.currentPos[1])
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
        self.currentPos[0] = int(text.split()[2])
        self.currentPos[1] = int(text.split()[3])
        self.selectedBox[0] = int(text.split()[0])
        self.selectedBox[1] = int(text.split()[1])
        self.render(2)

    def MapMove(self, event):
        if not self.mapData:
            return
        dirList = {'Up':[0,-1],'Left':[-1,0],'Right':[1,0],'Down':[0,1]}
        dir = event.GetEventObject().GetLabel()
        newX = self.currentPos[0]
        newY = self.currentPos[1]
        for i in range(5):
            newX += dirList[dir][0]
            newY += dirList[dir][1]
            if newX < 0 or newX + self.sceneSize[0] >= self.mapWidth:
                newX -= dirList[dir][0]
            if newY < 0 or newY + self.sceneSize[1] >= self.mapHeight:
                newY -= dirList[dir][1]
        self.currentPos[0] = newX
        self.currentPos[1] = newY
        self.render(1)
    
    def ShowMapDim(self):
        self.inputHeight.SetValue(self.mapHeight)
        self.inputWidth.SetValue(self.mapWidth)

    # functions
    def doSaveData(self, file):
        self.sceneNum = self.listBox.GetCount()
        file.write("%d %d %d\n" % (self.mapWidth, self.mapHeight, self.sceneNum))
        for li in self.sceneData:
            file.write(li+'\n')
        for i in range(self.mapHeight):
            for j in range(self.mapWidth):
                if j < self.mapWidth-1:
                    file.write("%d " % self.mapData[i][j])
                else:
                    if i <  self.mapHeight - 1:
                        file.write("%d\n" % self.mapData[i][j])
                    else:
                        file.write("%d" % self.mapData[i][j])

    def LoadData(self, file):
        lines_list = file.readlines()
        self.mapWidth, self.mapHeight, self.sceneNum = (int(val) for val in lines_list[0].split())
        self.sceneData = [line[:-1] for line in lines_list[1:self.sceneNum+1]]
        self.mapData = [[int(val) for val in line.split()] for line in lines_list[self.sceneNum+1:]]
        self.listBox.Clear()
        for li in self.sceneData:
            self.listBox.Append(li)
        self.ShowMapDim()
        self.render(1)

    def resetApp(self):
        self.contentNotSaved = False
        self.mapHeight = 0
        self.mapWidth = 0
        self.sceneNum = 0
        self.sceneData = []
        self.mapData = []
        self.listBox.Clear()
        self.ShowMapDim()
        self.render(0)
    
    def render(self, what):
        self.mapDrawer.render(what)

class MapDrawing(wx.Frame):
    def __init__(self, parent):
        # ensure the parent's __init__ is called
        wx.Frame.__init__(self, None, title='Map')
        self.parent = parent
        x = parent.tileSize * parent.sceneSize[0] + 50
        y = parent.tileSize * parent.sceneSize[1] + 50
        self.SetSize((x,y))
        self.SetPosition((250,50))

        size = self.ClientSize
        self._Buffer = wx.Bitmap(*size)

        self.LButtonDown = False

        #TODO: Mouse event (left click & drag) to change the tiles
        #TODO: Mouse event (right click) to highlight tile
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLButtonUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRButtonDown)
        
    def render(self, what):
        d = self.parent.tileSize
        memDC = wx.MemoryDC()
        memDC.SelectObject(self._Buffer)
        
        tmpDC = wx.MemoryDC()
        '''
        tmpDC.SelectObject(self.parent.bmpBkg)
        memDC.StretchBlit(0, 0, d*self.parent.sceneSize[0], d*self.parent.sceneSize[1], tmpDC, 0, 0, self.parent.bkgSize[0], self.parent.bkgSize[1])
        '''
        for y in range(self.parent.sceneSize[1]):
            for x in range(self.parent.sceneSize[0]):
                xx = x + self.parent.currentPos[0]
                yy = y + self.parent.currentPos[1]
                
                if what is 0:
                    b = 0
                else:
                    b = self.parent.mapData[yy][xx]
                tmpDC.SelectObject(self.parent.tileList[b])
                memDC.StretchBlit(x*d, y*d, d, d, tmpDC, 0, 0, self.parent.tileOriSize, self.parent.tileOriSize)
        if what is 2: # draw hero
            x = (self.parent.selectedBox[0]-self.parent.currentPos[0])*d
            y = (self.parent.selectedBox[1]-self.parent.currentPos[1])*d - d*2
            tmpDC.SelectObject(self.parent.bmpHero)
            memDC.StretchBlit(x, y, d*1, d*2, tmpDC, 0, 0, self.parent.heroSize[0], self.parent.heroSize[1])
        del memDC
        self.Refresh(eraseBackground=False)
        self.Update()

    def OnPaint(self, event):
        wndDC = wx.BufferedPaintDC(self, self._Buffer)

    def OnLButtonDown(self, event):
        if not self.parent.isFileOpen:
            return
        self.LButtonDown = True
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)

    def OnLButtonUp(self, event):
        if not self.parent.isFileOpen:
            return
        self.LButtonDown = False
        self.Unbind(wx.EVT_MOTION)

    def OnMouseMove(self, event):
        nx = int(event.GetPosition()[0] / self.parent.tileSize + self.parent.currentPos[0])
        ny = int(event.GetPosition()[1] / self.parent.tileSize + self.parent.currentPos[1])
        if nx < 0 or nx >= self.parent.mapWidth or ny < 0 or ny >= self.parent.mapHeight:
            pass
        else:
            if self.parent.mapData[ny][nx] != self.parent.brush:
                self.parent.mapData[ny][nx] = self.parent.brush
                self.render(1)

    def OnRButtonDown(self, event):
        nx = int(event.GetPosition()[0] / self.parent.tileSize + self.parent.currentPos[0])
        ny = int(event.GetPosition()[1] / self.parent.tileSize + self.parent.currentPos[1])
        if nx < 0 or nx >= self.parent.mapWidth or ny < 0 or ny >= self.parent.mapHeight:
            pass
        else:
            self.parent.selectedBox[0] = nx
            self.parent.selectedBox[1] = ny
            self.render(2)

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MapEditor(None, title='MapEditor')
    frm.Show()
    app.MainLoop()