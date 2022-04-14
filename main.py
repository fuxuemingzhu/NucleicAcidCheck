import os
import cv2
from paddleocr import PPStructure,draw_structure_result,save_structure_res

table_engine = PPStructure(show_log=True)

save_folder = './output/table'
img_path = '2022.4.14/张三.JPG'
img = cv2.imread(img_path)

results = table_engine(img)
save_structure_res(results, save_folder,os.path.basename(img_path).split('.')[0])

for result in results:
    result.pop('img')
    for line in result["res"]:
        print(line["text"])