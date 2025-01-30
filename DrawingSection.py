import sys
import requests
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QInputDialog, QGraphicsLineItem, QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QAction, QKeySequence
from math import sqrt, atan2, pi, cos, sin
from Bar import PoolProject, BarType, Bar, BAR_TYPES
SERVER_URL = "http://127.0.0.1:5000"

def send_bar_to_server(bar_data):
    """ Sends bar data to the Flask server """
    try:
        data = {
            "bar_type": bar_data['bar'].bar_type.name,
            "length": bar_data['bar'].length,
            "start_x": bar_data['start_point'].x(),
            "start_y": bar_data['start_point'].y(),
            "end_x": bar_data['end_point'].x(),
            "end_y": bar_data['end_point'].y(),
        }
        response = requests.post(f"{SERVER_URL}/add_bar", json=data)
        response.raise_for_status()  # Raises an error for bad responses (4xx, 5xx)
        print(f"✅ Sent bar data to server: {response.json()}")
    except requests.RequestException as e:
        print(f"Error sending bar data to server: {e}")

class DrawingArea(QGraphicsView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.grid_enabled = True
        self.drawing = False
        self.deleting = False
        self.editing = False
        self.selecting = False
        self.moving = False
        self.adding_text = False
        self.start_point = QPointF()
        self.current_line = None
        self.drawn_bars = []
        self.selected_bar = None
        self.offset = QPointF()
        self.current_color = Qt.GlobalColor.white
    
       
    def drawBackground(self, painter, rect):
        if self.grid_enabled:
            pen = QPen(Qt.GlobalColor.lightGray, 0, Qt.PenStyle.DotLine)
            painter.setPen(pen)
            left = int(rect.left()) - (int(rect.left()) % 20)
            top = int(rect.top()) - (int(rect.top()) % 20)
            for x in range(left, int(rect.right()), 20):
                painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            for y in range(top, int(rect.bottom()), 20):
                painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            print(f"Mouse press at view coordinates: {event.pos()}, scene coordinates: {scene_pos}")
            if self.deleting:
                items = self.scene.items(scene_pos)
                if items:
                    print(f"Deleting Item at scene position: {scene_pos} Item: {items[0]}")
                    self.main_window.delete_bar(items[0])
                   
            elif self.editing:
                items = self.scene.items(scene_pos)
                if items:
                    print(f"Editing items at scene position: {scene_pos} Item: {items[0]}")
                    self.main_window.edit_bar(items[0])
                    self.editing = False
            elif self.selecting: 
                items = self.scene.items(scene_pos)
                for item in items:
                    if isinstance(item, QGraphicsLineItem):
                        self.select_bar(item)  
                        self.moving = True 
                        self.offset = scene_pos - item.line().p1()
                        break
                    if isinstance(item, QGraphicsTextItem):
                        self.select_bar(item)
                        break
            elif self.adding_text:
                text, ok = QInputDialog.getText(self, 'Add Text', 'Enter text:')
                if ok and text:
                    text_item = QGraphicsTextItem(text)
                    text_item.setPos(scene_pos)
                    self.scene.addItem(text_item)
            else:
                self.drawing = True
                self.start_point = self.mapToScene(event.pos())
                self.current_line = QGraphicsLineItem()
                pen_thickness = self.main_window.current_bar_type.thickness
                pen = QPen(self.current_color)
                pen.setWidth(pen_thickness)
                self.current_line.setPen(pen)
                self.scene.addItem(self.current_line)
    
    def mouseMoveEvent(self, event):
        if self.drawing:
            end_point = self.mapToScene(event.pos())
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
               # end_point = snap_to_45_degrees(self.start_point, end_point)
                
                angle = atan2(end_point.y() - self.start_point.y(), end_point.x() - self.start_point.x())
                angle = round(angle/ (pi /4)) * (pi / 4) # 45 degree increments
                distance = sqrt((end_point.x() - self.start_point.x()) ** 2 + (end_point.y() - self.start_point.y()) ** 2)
                end_point.setX(self.start_point.x() + cos(angle) * distance)
                end_point.setY(self.start_point.y() + sin(angle) * distance)
                
            self.current_line.setLine(self.start_point.x(), self.start_point.y(), end_point.x(), end_point.y())
            length = sqrt((end_point.x() - self.start_point.x()) ** 2 + (end_point.y() - self.start_point.y()) ** 2)
        elif self.moving and self.selected_bar:
            new_pos = self.mapToScene(event.pos()) - self.offset
            self.move_selected_bar(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            end_point = self.mapToScene(event.pos())
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                angle = atan2(end_point.y() - self.start_point.y(), end_point.x() - self.start_point.x())
                angle = round(angle/ (pi /4)) * (pi / 4) # 45 degree increments
                distance = sqrt((end_point.x() - self.start_point.x()) ** 2 + (end_point.y() - self.start_point.y()) ** 2)
                end_point.setX(self.start_point.x() + cos(angle) * distance)
                end_point.setY(self.start_point.y() + sin(angle) * distance)
             #   end_point = self.snap_to_45_degrees(self.start_point, end_point)
            self.current_line.setLine(self.start_point.x(), self.start_point.y(), end_point.x(),  end_point.y())
            length = sqrt((end_point.x()- self.start_point.x())**2 + (end_point.y() - self.start_point.y())**2)
            bar_data = self.main_window.add_drawn_bar(length, self.start_point, end_point)
            if bar_data:
                self.drawn_bars.append(bar_data)
                self.main_window.history.append(('add', bar_data))
                send_bar_to_server(bar_data)

                

                #prompts the user to select length when drawing bar 
                new_length, ok = QInputDialog.getDouble(self,'Bar Length', 'Enter Bar Length', min = 0)
                if ok and new_length != 0:
                    bar_data['bar'].length = new_length
                    self.main_window.project.calculate_total_cost()
                    self.main_window.update_total_cost()
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
                send_bar_to_server(bar_data)
            self.current_line = None
            self.scene.update()

        elif self.moving:
            self.moving = False
            if self.selected_bar:
                self.selected_bar['line'].setPen(QPen(self.selected_bar['original_color']))
            self.selected_bar = None 

    def move_selected_bar(self, new_pos):
        if not self.selected_bar:
            return 

        delta = new_pos - self.selected_bar['line'].line().p1()
        print(f"Delta for moving: {delta}")

        new_p1 = self.selected_bar['line'].line().p1() + delta
        new_p2 = self.selected_bar['line'].line().p2() + delta

        self.selected_bar['line'].setLine(
            new_p1.x(), new_p1.y(),
            new_p2.x(), new_p2.y()
        )
        
        self.selected_bar['text'].setPos(
            (new_p1.x() + new_p2.x()) / 2,
            (new_p1.y() + new_p2.y()) / 2
        )

        print(f"Moved bar to new position: {new_pos}")
        self.update()
                
    def select_bar(self, item):
        if self.selected_bar:
            self.selected_bar['line'].setPen(QPen(self.selected_bar['original_color']))

        for bar_data in self.drawn_bars:
            if bar_data['line'] == item: #or bar_data['text'] == item:
                self.selected_bar = bar_data
                self.selected_bar['line'].setPen(QPen(Qt.GlobalColor.red))
                self.main_window.show_bar_properties(self.selected_bar)
                print(f"Bar selected: {bar_data}")
                break
    
    def set_color(self, color):
        self.current_color = color

    def snap_to_45_degrees(start_point: QPointF, end_point: QPointF) -> QPointF:
        angle = atan2(end_point.y() - start_point.y(), end_point.x() - start_point.x())
        angle = round(angle / (pi / 4)) * (pi / 4)  # 45 degree increments
        distance = sqrt((end_point.x() - start_point.x()) ** 2 + (end_point.y() - start_point.y()) ** 2)
        snapped_end_point = QPointF(
            start_point.x() + cos(angle) * distance,
            start_point.y() + sin(angle) * distance
        )
        return snapped_end_point
    