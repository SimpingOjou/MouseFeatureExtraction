class CameraData:
    def __init__(self, focal_length:float, pixel_size:float, resolution:tuple[int,int]):
        self.focal_length = focal_length
        self.pixel_size = pixel_size
        self.resolution = resolution

    def px_to_meter(self, value_px:int):
        return value_px * self.pixel_size