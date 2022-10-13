class Space:
    def __init__(self, new_x, new_y, flagged, flaggedby, bomb, visible, surrounding):
        self.xposition = new_x                # Space's x coordinate
        self.yposition = new_y                # Space's y coordinate
        self.flagged = flagged                # Tag if space is flagged
        self.flaggedby = flaggedby            # Tag who space is flagged by
        self.bomb = bomb                      # Tag if a space is a bomb
        self.visible = visible                # Tag if a space is visible to players
        self.surrounding = surrounding        # Number of bombs around the space
