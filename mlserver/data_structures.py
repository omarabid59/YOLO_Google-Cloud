import numpy as np
class ImageData:
    def __init__(self):
        self.image_np = ()
        self.isInit = False
        self.width = None
        self.height = None
        
class OutputClassificationData:
    def __init__(self):
        self.bbs = np.asarray([])
        self.score_thresh = ()
        self.scores = np.asarray([])
        self.classes = np.asarray([])
        self.image_data = ImageData()
        self.category_index = ()