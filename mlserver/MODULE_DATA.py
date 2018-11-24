import json
import numpy as np
class ModuleData:
    def __init__(self,detection_thread):
        self.detection_thread = detection_thread
        self.image_height = 0;
        self.image_width = 0;

            
    def create_detection_data(self):
        h = self.image_height; w = self.image_width;
        data = {}
        data['type'] = 'detection_data'
        data['name'] = self.detection_thread.name
    
        data['bbs'] = self.fix_bb_coords(self.detection_thread.output_data.bbs.copy(),
                                    h,w)
        data['scores'] = self.detection_thread.output_data.scores.tolist()
        class_names = []
        for c in self.detection_thread.output_data.classes:
            class_names.append(self.detection_thread.output_data.category_index.get(c)['name'])
        data['classes'] = class_names

        return json.dumps(data)
   


    def fix_bb_coords(self,bbs,h,w):
        for indx, bb in enumerate(bbs):
            bbs[indx][0] = int(bbs[indx][0]*h)
            bbs[indx][1] = int(bbs[indx][1]*w)
            bbs[indx][2] = int(bbs[indx][2]*h)
            bbs[indx][3] = int(bbs[indx][3]*w)  

            bbs[indx][0] = max(min(bbs[indx][0],h),0)
            bbs[indx][2] = max(min(bbs[indx][2],h),0)
            bbs[indx][1] = max(min(bbs[indx][1],w),0)
            bbs[indx][3] = max(min(bbs[indx][3],w),0)
        return bbs.tolist()
    
    def updateData(self,message):
        data = json.loads(message)
        try:
            self.image_height = int(data['image_properties']['height'])
            self.image_width = int(data['image_properties']['width'])
        except Exception as e:
            print("Failed loading new data." + str(e))