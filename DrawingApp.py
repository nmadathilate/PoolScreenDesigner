import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QToolBar, QInputDialog, QGraphicsTextItem, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QColorDialog, QFileDialog
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QAction, QKeySequence, QIcon, QColor
from PyQt6.QtPrintSupport import QPrinter
from math import sqrt
from Bar import PoolProject, BarType, Bar, BAR_TYPES
from DrawingSection import DrawingArea


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = PoolProject()
        self.current_bar_type = None
        self.current_cost_per_unit = None
        self.bar_counts = {}
        self.history = []
        self.setWindowTitle("Pool Screen Designer")
        self.setGeometry(100, 100, 800, 600)

        #Sets up Tab to switch between inventory and drawing 
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.drawing_tab = QWidget()
        self.inventory_tab = QWidget()

        self.tabs.addTab(self.drawing_tab, "Drawing")
        self.tabs.addTab(self.inventory_tab, "Inventory")

        self.create_drawing_tab()
        self.create_inventory_tab()

       # self.drawing_area = DrawingArea()
        #self.setCentralWidget(self.drawing_area)

        self.create_toolbar()
        self.Ctrl_Z_shortcut() #allows for Ctrl + Z, Ctrl + P, and Ctrl + V
        self.statusBar().showMessage("Total cost: $0.00")
    
    
    def create_drawing_tab(self):
        layout = QVBoxLayout()
        self.drawing_area = DrawingArea(self)
        layout.addWidget(self.drawing_area)
        self.drawing_tab.setLayout(layout)
    
    def create_inventory_tab(self):
        layout = QVBoxLayout()
        self.inventory_table = QTableWidget(0,2)
        self.inventory_table.setHorizontalHeaderLabels(["Bar Type", "Count"])
        layout.addWidget(self.inventory_table)
        self.inventory_tab.setLayout(layout)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        select_action = QAction(QIcon("icons/selection.png"),"Select Bar", self)
        select_action.triggered.connect(self.enable_select_mode)
        toolbar.addAction(select_action)

        draw_action = QAction(QIcon("icons/drawline.png"), "Draw Bar", self)
        draw_action.triggered.connect(self.enable_draw_mode)
        toolbar.addAction(draw_action)

        remove_action = QAction(QIcon("icons/eraser.jpeg"),"Delete Bar", self)
        remove_action.triggered.connect(self.enable_delete_mode)
        toolbar.addAction(remove_action)

        grid_action = QAction(QIcon("icons/togglegrid.png"),"Toggle Grid", self)
        grid_action.triggered.connect(self.toggle_grid)
        toolbar.addAction(grid_action)

        color_action = QAction(QIcon("icons/colorWheel.jpg"), "Color", self)
        color_action.triggered.connect(self.select_color)
        toolbar.addAction(color_action)

        textbox_action = QAction(QIcon("icons/textbox.jpg"), "Textbox", self)
        textbox_action.triggered.connect(self.enable_text_mode)
        toolbar.addAction(textbox_action)

        save_action = QAction(QIcon("icons/saveImage.png"),"Save", self)
        save_action.triggered.connect(self.export_to_pdf)
        toolbar.addAction(save_action)


        self.combo_box = QComboBox()
        for bar_type in BAR_TYPES:
            self.combo_box.addItem(bar_type.name, bar_type)
        self.combo_box.currentIndexChanged.connect(self.update_bar_type)
        toolbar.addWidget(self.combo_box)

    def export_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "*.pdf")
        if file_path:
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"
            
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            printer.setResolution(1200)

            painter = QPainter(printer)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            background_color = QColor(Qt.GlobalColor.black)
            painter.fillRect(printer.pageRect(QPrinter.Unit.Point), background_color)


            rect = self.drawing_area.scene.sceneRect()
            page_rect = printer.pageRect(QPrinter.Unit.Point)
            scale_factor = min(page_rect.width() / rect.width(),
                                page_rect.height() / rect.height())
            painter.scale(scale_factor, scale_factor)

            painter.translate((page_rect.width() - rect.width() * scale_factor) / 2,
                              (page_rect.height() - rect.height() * scale_factor) / 2)

            self.drawing_area.scene.render(painter, QRectF(0,0,rect.width(),rect.height()),rect)

            painter.end()
            print(f"Saved drawing to {file_path}")
    
    def Ctrl_Z_shortcut(self):
        undo_action = QAction("Undo", self)
        undo_shortcut = QKeySequence("Ctrl+Z")
        undo_action.setShortcut(undo_shortcut)
        undo_action.triggered.connect(self.undo)
        self.addAction(undo_action)


    def update_bar_type(self, index):
        selected_bar_type = self.combo_box.itemData(index)
        if selected_bar_type:
            self.current_bar_type = selected_bar_type
            self.current_cost_per_unit = selected_bar_type.cost_per_unit
            print(f"Selected bar type: {self.current_bar_type.name}, Cost per unit: {self.current_cost_per_unit}")

    def update_inventory_table(self):
        self.inventory_table.setRowCount(len(self.bar_counts))
        for row, (bar_type, count) in enumerate(self.bar_counts.items()):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(bar_type))
            self.inventory_table.setItem(row,1, QTableWidgetItem(str(count)))

    def add_drawn_bar(self, length, start_point, end_point):
        if self.current_bar_type is None or self.current_cost_per_unit is None:
            self.statusBar().showMessage("Please select a bar type first")
            return None
        bar = Bar(bar_type = self.current_bar_type, length = length/10)
        self.project.add_bar(bar)
        self.update_total_cost()

        text_item = QGraphicsTextItem(f"{self.current_bar_type.name} ( {length / 10:.2f} ft)")
        text_item.setPos((start_point.x() +  end_point.x()) / 2, (start_point.y() + end_point.y()) /2)
        self.drawing_area.scene.addItem(text_item)

        bar_data = {
            'line': self.drawing_area.current_line, 
            'text': text_item,
            'bar': bar,
            'start_point' : start_point,
            'end_point' : end_point,
            'original_color' : self.drawing_area.current_color
            }
        
        self.drawing_area.drawn_bars.append(bar_data)
        self.history.append(('add', bar_data))

        #updates the inventory 
        if self.current_bar_type.name in self.bar_counts:
            self.bar_counts[self.current_bar_type.name] += 1
        else:
            self.bar_counts[self.current_bar_type.name] = 1
        self.update_inventory_table()

        return bar_data
    
    def delete_bar(self, item):
        for bar_data in self.drawing_area.drawn_bars:
            if bar_data['line'] == item or bar_data['text'] == item:
                print(f"Deleting bar: {bar_data} ")
                self.drawing_area.scene.removeItem(bar_data['line'])
                self.drawing_area.scene.removeItem(bar_data['text'])
                self.project.bars.remove(bar_data['bar'])
                self.update_total_cost()

                bar_type_name = bar_data['bar'].bar_type.name
                if bar_type_name in self.bar_counts:
                    self.bar_counts[bar_type_name] -= 1
                    if self.bar_counts[bar_type_name] <= 0:
                        del self.bar_counts[bar_type_name]
                self.update_inventory_table()
                    
                self.drawing_area.drawn_bars.remove(bar_data)
                self.history.append(('delete', bar_data))
                break
    
    def edit_bar(self, item):
        for bar_data in self.drawing_area.drawn_bars:
            if bar_data['line'] == item or bar_data['text'] == item:
                print(f"Editing bar: {bar_data}")
                new_length, ok = QInputDialog.getDouble(self, 'Edit Bar Length', 'Enter new bar length:', min = 0 )
                if ok:
                    bar_data['bar'].length = new_length
                    self.project.calculate_total_cost()
                    self.update_total_cost()
                    #updates actual line
                    start_point = bar_data['start_point']
                    end_point = bar_data['end_point']
                    direction_vector = QPointF(end_point.x() - start_point.x(), end_point.y() - start_point.y())
                    vector_length = sqrt(direction_vector.x()**2 + direction_vector.y()**2)
                    normalized_vector = QPointF(direction_vector.x() / vector_length, direction_vector.y() / vector_length)
                
                # Calculate the new end point
                    new_end_point = QPointF(start_point.x() + normalized_vector.x() * new_length * 10,
                                        start_point.y() + normalized_vector.y() * new_length * 10)
                    bar_data['line'].setLine(start_point.x(), start_point.y(), new_end_point.x(), new_end_point.y())
                    bar_data['text'].setPlainText(f"{bar_data['bar'].bar_type.name} ({new_length:.2f} ft)")
                    bar_data['text'].setPos((start_point.x() + new_end_point.x()) / 2, (start_point.y() + new_end_point.y()) / 2)
    
    def enable_draw_mode(self):
        self.clear_properties_table()
        #self.drawing_area.drawing = True
        self.drawing_area.deleting = False
        self.drawing_area.editing = False
        self.drawing_area.selecting = False
        self.drawing_area.adding_text = False
    def enable_delete_mode(self):
        self.clear_properties_table()
        self.drawing_area.deleting = True
        self.drawing_area.editing = False
        self.drawing_area.adding_text = False

    def enable_edit_mode(self):
        self.clear_properties_table()
        self.drawing_area.editing = True
        self.drawing_area.deleting = False
        self.drawing_area.drawing = False
        self.drawing_area.selecting = False
        self.drawing_area.adding_text = False

    def enable_select_mode(self):
        self.clear_properties_table()
        self.drawing_area.editing = False
        self.drawing_area.drawing = False
        self.drawing_area.deleting = False
        self.drawing_area.selecting = True
        self.drawing_area.adding_text = False
    
    def enable_text_mode(self):
        self.drawing_area.adding_text = True
        self.drawing_area.selecting = False
        self.drawing_area.drawing = False
        self.drawing_area.deleting = False
        self.drawing_area.editing = False
    
    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawing_area.set_color(color)
    
    def show_bar_properties(self, bar_data):
        self.properties_table = QTableWidget(3,2)
        self.properties_table.setHorizontalHeaderLabels(['Property', 'Value'])
        self.properties_table.setItem(0, 0, QTableWidgetItem('Bar Type'))
        self.properties_table.setItem(0, 1, QTableWidgetItem(bar_data['bar'].bar_type.name))
        self.properties_table.setItem(1, 0, QTableWidgetItem('Length'))
        self.properties_table.setItem(1, 1, QTableWidgetItem(str(bar_data['bar'].length)))
        self.properties_table.setItem(2, 0, QTableWidgetItem('Price'))
        self.properties_table.setItem(2, 1, QTableWidgetItem(str(bar_data['bar'].cost())))

        self.properties_table.itemChanged.connect(lambda item: self.update_bar_properties(item, bar_data))

        layout = self.drawing_tab.layout()
        layout.addWidget(self.properties_table) #adds property table to right side of drawing area

    def update_bar_properties(self, item, bar_data):
        if item.row() == 1:
            new_length = float(item.text())
            bar_data['bar'].length = new_length
            self.project.calculate_total_cost()
            self.update_total_cost()
            start_point = bar_data['start_point']
            end_point = bar_data['end_point']
            direction_vector = QPointF(end_point.x() - start_point.x(), end_point.y() - start_point.y())
            vector_length = sqrt(direction_vector.x()**2 + direction_vector.y()**2)
            normalized_vector = QPointF(direction_vector.x() / vector_length, direction_vector.y() / vector_length)
                
             # Calculate the new end point
            new_end_point = QPointF(start_point.x() + normalized_vector.x() * new_length * 10,
                                     start_point.y() + normalized_vector.y() * new_length * 10)
            bar_data['line'].setLine(start_point.x(), start_point.y(), new_end_point.x(), new_end_point.y())
            bar_data['text'].setPlainText(f"{bar_data['bar'].bar_type.name} ({new_length:.2f} ft)")
            bar_data['text'].setPos((start_point.x() + new_end_point.x()) / 2, (start_point.y() + new_end_point.y()) / 2)

            #updates cost for new length 
            self.properties_table.item(3,1).setText(str(bar_data['bar'].cost()))
        elif item.row() == 0:
            new_bar_type_name = item.text()
            for bar_type in BAR_TYPES:
                if bar_type.name == new_bar_type_name:
                    bar_data['bar'].bar_type = bar_type
                    self.properties_table.item(1,1).setText(str(bar_type.cost_per_unit))
                    break

    def clear_properties_table(self):
        if hasattr(self, 'properties_table') and self.properties_table is not None:
            self.drawing_tab.layout().removeWidget(self.properties_table)
            self.properties_table.deleteLater()
            self.properties_table = None

            #sets bar color back to black
            if self.drawing_area.selected_bar:
                self.drawing_area.selected_bar['line'].setPen(QPen(Qt.GlobalColor.white))
                self.drawing_area.selected_bar = None

    def toggle_grid(self):
        self.drawing_area.grid_enabled = not self.drawing_area.grid_enabled
        self.drawing_area.viewport().update()
    
    def undo(self):
        if not self.history:
            return 
        last_action, bar_data = self.history.pop()
        if last_action == 'add':
            self.drawing_area.scene.removeItem(bar_data['line'])
            self.drawing_area.scene.removeItem(bar_data['text'])
            self.project.bars.remove(bar_data['bar'])
            self.drawing_area.drawn_bars.remove(bar_data)

            bar_type_name = bar_data['bar'].bar_type.name
            if bar_type_name in self.bar_counts:
                self.bar_counts[bar_type_name] -= 1
                if self.bar_counts[bar_type_name] <= 0:
                    del self.bar_counts[bar_type_name]
            self.update_inventory_table()
            self.update_total_cost()
        elif last_action == 'delete':
            self.drawing_area.scene.addItem(bar_data['line'])
            self.drawing_area.scene.addItem(bar_data['text'])
            self.project.bars.append(bar_data['bar'])
            self.drawing_area.drawn_bars.append(bar_data)

            bar_type_name = bar_data['bar'].bar_type.name
            if bar_type_name in self.bar_counts:
                self.bar_counts[bar_type_name] += 1
            else:
                self.bar_counts[bar_type_name] = 1
            self.update_inventory_table()
            self.update_total_cost()



    def update_total_cost(self):
        total_cost = self.project.calculate_total_cost()
        self.statusBar().showMessage(f"Total cost: ${total_cost:.2f}")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())