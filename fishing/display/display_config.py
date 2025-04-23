from PIL import Image
from core import Singleton, ConfigLoader

class DisplayConfig(metaclass=Singleton):
    def __init__(self):
        self._config = ConfigLoader().config['display']

        # Important Display Variables
        self.config_file = self._config["config_file"]
        self.parse_colors = self._config['parse_colors']

        self.screen_width = None
        self.screen_height = None
        
        # DISPLAY COORDS
        """
        Finds left-most, top-most, right-most, bottom-most value of all pixels
        Default: {
            "left": None,
            "top": None,
            "right": None,
            "bottom": None
        }
        """
        self.fishing_indicator_coords = {}
        self.hunger_bar_coords = {}
        self.health_bar_coords = {}
        self.catch_title_coords = {}
        self.catch_background_coords = {}
        self.item_slots = [{}, {}, {}, {}, {}, {}, {}, {}, {}]

        self.current_item_slot = 0
        self.parsing_item_slot = False

        self._parse_display_config()

    @property
    def fishing_indicator_bounds(self):
        return self._get_bounds(self.fishing_indicator_coords)

    @property
    def hunger_bar_bounds(self):
        return self._get_bounds(self.hunger_bar_coords)

    @property
    def catch_title_bounds(self):
        return self._get_bounds(
            self.catch_title_coords,
            y_offset=-self._get_quest_y_offset(self._config["active_quests"])
        )
    
    @property
    def catch_background_bounds(self):
        return self._get_bounds(
            self.catch_background_coords,
            y_offset=-self._get_quest_y_offset(self._config["active_quests"])
        )
    
    @property
    def health_bar_bounds(self):
        return self._get_bounds(self.health_bar_coords)
    
    def get_item_slot_bound(self, slot):
        if slot < 0 or slot >= len(self.item_slots):
            raise Exception("Invalid slot") 

        return self._get_bounds(self.item_slots[slot])

    def get_center_box_bound(self, width, height):
        center = (self.screen_width // 2, self.screen_height // 2)
        w = width // 2
        h = height // 2
        
        return (
            (center[0]-w, center[1]-h), 
            (center[0]+w, center[1]+h)
        )

    def shrink_bounds(self, bounds, amt):
        bounds = list(bounds)
        bounds[0] = list(bounds[0])
        bounds[1] = list(bounds[1])

        bounds[0][0] += amt
        bounds[0][1] += amt
        bounds[1][0] -= amt
        bounds[1][1] -= amt

        bounds[0] = tuple(bounds[0])
        bounds[1] = tuple(bounds[1])
        bounds = tuple(bounds)

        return bounds

    def combine_bounds(self, bound1, bound2):
        return (
            (
                min(bound1[0][0], bound2[0][0]),
                min(bound1[0][1], bound2[0][1])
            ),
            (
                max(bound1[1][0], bound2[1][0]),
                max(bound1[1][1], bound2[1][1])
            )
        )

    def _get_quest_y_offset(self, quests):
        if quests == 0:
            return 0
        if quests == 1:
            return self._config["first_quest_offset"]
        if quests > 1:
            return self._config['quest_height'] + self._get_quest_y_offset(quests - 1)

    def _get_bounds(self, reference, x_offset=0, y_offset=0):
        return ( 
            (
                reference.get("left") + x_offset,
                reference.get("top") + y_offset
            ),
            (
                reference.get("right") + x_offset,
                reference.get("bottom") + y_offset
            )
        )
        
    def _parse_display_config(self):
        print(f"Parsing display config {self.config_file}")

        display_img = Image.open(self.config_file)
        self.screen_width, self.screen_height = display_img.size
        px = display_img.load()

        for y in range(self.screen_height):
            for x in range(self.screen_width):
                if (
                    self.is_same_color(self.parse_colors["item_slot"], px[x, y])
                ):
                    if not self.parsing_item_slot:
                        self.parsing_item_slot = True

                    self._update_coords(
                        self.item_slots[self.current_item_slot],
                        x, y
                    )               
                else:
                    if self.parsing_item_slot:
                        self.current_item_slot += 1    
                        self.parsing_item_slot = False

                    ref = self._get_pixel_reference(px[x, y])

                    if ref != None:
                        self._update_coords(
                            ref,
                            x, y
                        )
            
            self.current_item_slot = 0 # Reset at end of row
        
        print("Finished parsing display config.")
    
    def is_same_color(self, px1, px2):
        for i in range(3):
            if px1[i] != px2[i]:
                return False

        return True
    
    # cannot be item slot
    def _get_pixel_reference(self, pixel):
        if pixel[3] < 250:
            return
        
        if self.is_same_color(self.parse_colors["fishing_indicator"], pixel): 
            return self.fishing_indicator_coords
        if self.is_same_color(self.parse_colors["hunger_bar"], pixel):
            return self.hunger_bar_coords
        if self.is_same_color(self.parse_colors["catch_title"], pixel):
            return self.catch_title_coords
        if self.is_same_color(self.parse_colors["catch_background"], pixel):
            return self.catch_background_coords
        if self.is_same_color(self.parse_colors["health_bar"], pixel):
            return self.health_bar_coords

    def _update_coords(self, reference, x, y):
        reference["left"] = min(
            x,
            reference.get("left", self.screen_width)
        )
        reference["top"] = min(
            y,
            reference.get("top", self.screen_height)
        )
        reference["right"] = max(
            x,
            reference.get("right", 0)
        )
        reference["bottom"] = max(
            y,
            reference.get("bottom", 0)
        )
    
    def __str__(self):
        return (f"Fishing Indicator Bounds: {self.fishing_indicator_bounds}\n"
                f"Hunger Bar Bounds: {self.hunger_bar_bounds}\n"
                f"Catch Title Bounds: {self.catch_title_bounds}\n"
                f"Catch Background Bounds: {self.catch_background_bounds}\n"
                f"Health Bar Bounds: {self.health_bar_bounds}\n"
                f"Item Slots Bounds: {[self.get_item_slot_bound(i) for i in range(len(self.item_slots))]}")