class BarType:
    def __init__(self, name, cost_per_unit: float, thickness ):
        self.name = name
        self.cost_per_unit = cost_per_unit 
        self.thickness = thickness

class Bar:
    def __init__(self, bar_type, length: float):
        self.bar_type = bar_type
        #self.cost_per_unit = cost_per_unit
        self.length = length

    def cost(self):
        return self.length * self.bar_type.cost_per_unit
    
class PoolProject:
    def __init__(self):
        self.bars = []
    def add_bar(self, bar: Bar):
        self.bars.append(bar)

    def remove_bar(self, bar: Bar):
        self.bars.remove(bar)

    def calculate_total_cost(self):
        total_price = 0
        for bar in self.bars:
            total_price += bar.cost()
        return total_price

BAR_TYPES = [
    BarType(name = 'Select Bar Type', cost_per_unit= 0, thickness = 2),
    BarType(name = '1X2 Open Back', cost_per_unit= .912, thickness = 2),
    BarType(name = '2X2 Post', cost_per_unit= 35.76, thickness = 2),
    BarType(name = '2X4', cost_per_unit= 1.58, thickness = 2),
    BarType(name = '2X5', cost_per_unit= 1.98, thickness = 2),
    BarType(name = '2X6', cost_per_unit= 2.25, thickness = 2),
    BarType(name = '2X7', cost_per_unit= 2.50, thickness = 2),
    BarType(name = '2X8', cost_per_unit= 3.45, thickness = 2),
    BarType(name = '2X9', cost_per_unit= 3.98, thickness = 2),
    BarType(name = '2X10', cost_per_unit= 6.13, thickness = 2),
    BarType(name = '7in Super Gutter', cost_per_unit= 6.50, thickness = 2),
    BarType(name = '5in Super Gutter', cost_per_unit= 4.60, thickness = 2),
    BarType(name = "2X10 Rec Tube", cost_per_unit= 16.80, thickness= 4),
    BarType(name = "2X8 Rec Tube", cost_per_unit= 9.50, thickness= 4),
    BarType(name = "4X4 Post", cost_per_unit= 8.30, thickness= 4),
    BarType(name = "4X4 Casting", cost_per_unit= 7.81, thickness= 4),
]
if __name__ == "__main__":
    project = PoolProject()
    bar1 = Bar(name = "2x2", cost_per_unit= 15, length=5.0)
    bar2 = Bar(name = "2x4", cost_per_unit = 20, length=3.0)
    project.add_bar(bar1)
    project.add_bar(bar2)
    print(f"Total cost: {project.calculate_total_cost()}")