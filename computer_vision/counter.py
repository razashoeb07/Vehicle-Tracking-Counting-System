from collections import defaultdict


class VehicleCounter:

    def __init__(self, red_line_y=200, blue_line_y=300):

        self.red_line_y = red_line_y
        self.blue_line_y = blue_line_y

        self.counted_ids_red_to_blue = set()
        self.counted_ids_blue_to_red = set()

        self.count_red_to_blue = defaultdict(int)
        self.count_blue_to_red = defaultdict(int)

        self.crossed_red_first = {}
        self.crossed_blue_first = {}

    def update(self, track_id, class_name, cy):

        # Check RED line crossing
        if self.red_line_y - 5 <= cy <= self.red_line_y + 5:

            if track_id not in self.crossed_red_first:
                self.crossed_red_first[track_id] = True

        # Check BLUE line crossing
        if self.blue_line_y - 5 <= cy <= self.blue_line_y + 5:

            if track_id not in self.crossed_blue_first:
                self.crossed_blue_first[track_id] = True

        # RED -> BLUE = DOWN
        if (
            track_id in self.crossed_red_first
            and track_id not in self.counted_ids_red_to_blue
        ):

            if self.blue_line_y - 5 <= cy <= self.blue_line_y + 5:

                self.counted_ids_red_to_blue.add(track_id)
                self.count_red_to_blue[class_name] += 1

        # BLUE -> RED = UP
        if (
            track_id in self.crossed_blue_first
            and track_id not in self.counted_ids_blue_to_red
        ):

            if self.red_line_y - 5 <= cy <= self.red_line_y + 5:

                self.counted_ids_blue_to_red.add(track_id)
                self.count_blue_to_red[class_name] += 1

    def get_counts(self):

        return (
            dict(self.count_red_to_blue),
            dict(self.count_blue_to_red)
        )