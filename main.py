# # # import cv2
# # # import os
# # # import pandas as pd
# # # from ultralytics import YOLO
# # # # from tracker import Tracker
# # # import time
# # # import math
# # # from flask import Flask, render_template, request, redirect, url_for, send_from_directory



# # # class Tracker:
# # #     def __init__(self):
# # #         # Store the center positions of the objects
# # #         self.center_points = {}
# # #         # Keep the count of the IDs
# # #         self.id_count = 0

# # #     def update(self, objects_rect):
# # #         # Objects boxes and ids
# # #         objects_bbs_ids = []

# # #         # Get center point of new object
# # #         for rect in objects_rect:
# # #             x, y, w, h = rect
# # #             cx = (x + x + w) // 2
# # #             cy = (y + y + h) // 2

# # #             # Check if object already detected
# # #             same_object_detected = False
# # #             for id, pt in self.center_points.items():
# # #                 dist = math.hypot(cx - pt[0], cy - pt[1])
# # #                 if dist < 35:
# # #                     self.center_points[id] = (cx, cy)
# # #                     objects_bbs_ids.append([x, y, w, h, id])
# # #                     same_object_detected = True
# # #                     break

# # #             # Assign new ID to new objects
# # #             if not same_object_detected:
# # #                 self.center_points[self.id_count] = (cx, cy)
# # #                 objects_bbs_ids.append([x, y, w, h, self.id_count])
# # #                 self.id_count += 1

# # #         # Clean center points for removed IDs
# # #         new_center_points = {object_id: self.center_points[object_id] for _, _, _, _, object_id in objects_bbs_ids}
# # #         self.center_points = new_center_points
# # #         return objects_bbs_ids

# # # # تحميل نموذج YOLO
# # # model = YOLO('yolov8s.pt')

# # # # تحميل الفيديو
# # # cap = cv2.VideoCapture('car.mov')

# # # # فئات المركبات المراد اكتشافها
# # # class_list = ['car', 'motorcycle', 'truck', 'bus']

# # # # إنشاء متتبع
# # # tracker = Tracker()

# # # # تحديد خط في منتصف الفريم لحساب عدد المركبات
# # # middle_line_y = 250  # خط في منتصف الفريم
# # # offset = 6

# # # # المتغيرات المطلوبة
# # # counter_middle = []  # لتسجيل المركبات التي تعبر خط المنتصف
# # # vehicle_count_middle = 0  # عداد المركبات التي تعبر المنتصف
# # # vehicles_in_time_frame = 0  # عدد المركبات خلال فترة زمنية محددة
# # # time_since_last_change = 0  # الوقت منذ آخر تغيير في حدود السرعة
# # # last_change_time = time.time()  # لحفظ الوقت الحالي

# # # # المتغيرات المطلوبة لحساب السرعة
# # # car_speed = {}  # لتسجيل السرعة لكل مركبة

# # # # المتغيرات الخاصة بالسرعة الافتراضية
# # # default_speed_range = [80, 100]  # السرعة الافتراضية بين 80 و 100 كم/س
# # # speed_range = default_speed_range.copy()  # نطاق السرعة الحالي
# # # last_reset_time = time.time()  # لحساب المدة الزمنية منذ آخر إعادة ضبط

# # # # تحديد الحدود الخاصة بكل مستوى ازدحام
# # # speed_limits = {
# # #     "low": [80, 100],
# # #     "medium": [60, 80],
# # #     "high": [40, 60]
# # # }

# # # # دالة لتقدير السرعة
# # # def estimate_speed(location1, location2, fps=20, ppm=8.8):
# # #     d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
# # #     d_meters = d_pixels / ppm
# # #     speed = d_meters * fps * 3.6  # تحويل إلى كم/س
# # #     return speed

# # # # دالة لتخفيض التغييرات الكبيرة في السرعة
# # # def smooth_speed(old_speed, new_speed, alpha=0.7):
# # #     if old_speed is None:
# # #         return new_speed
# # #     return (alpha * old_speed) + ((1 - alpha) * new_speed)

# # # # دالة لتحديث حدود السرعة بناءً على عدد المركبات
# # # def update_speed_limit(vehicle_count):
# # #     global speed_range, vehicles_in_time_frame, last_change_time

# # #     # تحديث الوقت منذ آخر تغيير
# # #     time_since_last_change = time.time() - last_change_time

# # #     if vehicle_count <= 10 and time_since_last_change >= 45:  # إذا كان عدد المركبات 10 أو أقل خلال 45 ثانية
# # #         speed_range = speed_limits["medium"]
# # #         vehicles_in_time_frame = 0  # تصفير عداد المركبات
# # #         last_change_time = time.time()  # تحديث الوقت الحالي
# # #     elif vehicle_count <= 15 and time_since_last_change >= 45:  # إذا كان عدد المركبات 15 أو أقل
# # #         speed_range = speed_limits["high"]
# # #         vehicles_in_time_frame = 0  # تصفير عداد المركبات
# # #         last_change_time = time.time()  # تحديث الوقت الحالي
# # #     elif time_since_last_change >= 45:  # إذا لم يصل عدد المركبات إلى 10 خلال 45 ثانية
# # #         speed_range = default_speed_range  # العودة إلى السرعة الافتراضية
# # #         vehicles_in_time_frame = 0  # تصفير عداد المركبات
# # #         last_change_time = time.time()  # تحديث الوقت الحالي

# # # # حفظ الفيديو المعدل
# # # output_folder = r"C:\Users\fatim\Desktop\testingCap"  # تحديث مسار المجلد حسب نظام التشغيل
# # # if not os.path.exists(output_folder):
# # #     os.makedirs(output_folder)
# # # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# # # out = cv2.VideoWriter(os.path.join(output_folder, 'output.mp4'), fourcc, 20.0, (1020, 500))

# # # # قائمة لتخزين المخالفات
# # # violations = []

# # # while True:
# # #     ret, frame = cap.read()
# # #     if not ret:
# # #         break

# # #     frame = cv2.resize(frame, (1020, 500))

# # #     # توقع YOLO
# # #     results = model.predict(frame)
# # #     detections = results[0].boxes.data.detach().cpu().numpy()
# # #     detections_df = pd.DataFrame(detections).astype("float")

# # #     vehicles = []

# # #     # فلترة المركبات حسب الفئة (سيارة، حافلة، شاحنة، دراجة نارية)
# # #     for _, row in detections_df.iterrows():
# # #         x1, y1, x2, y2, class_id = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[5])
# # #         vehicle_class = class_list[class_id] if class_id < len(class_list) else None
# # #         if vehicle_class in class_list:
# # #             vehicles.append([x1, y1, x2, y2])

# # #     # تحديث المتتبع
# # #     bbox_id = tracker.update(vehicles)

# # #     # تحديث عدد المركبات
# # #     vehicle_count_middle = len(counter_middle)

# # #     for bbox in bbox_id:
# # #         x3, y3, x4, y4, id = bbox
# # #         cx, cy = (x3 + x4) // 2, (y3 + y4) // 2

# # #         # تحقق من عبور المركبة لخط المنتصف
# # #         if middle_line_y - offset < cy < middle_line_y + offset:
# # #             if id not in counter_middle:
# # #                 counter_middle.append(id)
# # #                 vehicle_count_middle += 1  # زيادة عدد المركبات
# # #                 vehicles_in_time_frame += 1  # زيادة عداد المركبات خلال الفترة الزمنية المحددة

# # #         # حساب السرعة لكل مركبة
# # #         if id in car_speed:
# # #             old_speed = car_speed[id]['speed']
# # #             old_position = car_speed[id]['position']
# # #             new_position = [cx, cy]
# # #             new_speed = estimate_speed(old_position, new_position)
# # #             smoothed_speed = smooth_speed(old_speed, new_speed)  # حساب السرعة الملساء
# # #             car_speed[id] = {'speed': smoothed_speed, 'position': new_position}
# # #         else:
# # #             car_speed[id] = {'speed': None, 'position': [cx, cy]}  # تسجيل المركبة الجديدة

# # #         # رسم الصندوق وعرض ID المركبة والسرعة
# # #         cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 1)  # صندوق أخضر
# # #         cv2.putText(frame, f'ID: {id}', (x3, y3 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # النص بالأبيض

# # #         # عرض السرعة إذا تم حسابها
# # #         if car_speed[id]['speed'] is not None:
# # #             cv2.putText(frame, f'Speed: {int(car_speed[id]["speed"])} km/h', (x3, y3 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)  # تحسين خط السرعة

# # #             # تسجيل المخالفات فقط للسيارات التي تتجاوز الحد الأقصى
# # #             speed = int(car_speed[id]['speed'])
# # #             if speed > speed_range[1]:  # تحقق إذا كانت السرعة تتجاوز الحد الأقصى
# # #                 current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # الوقت الحالي بالثواني
# # #                 violations.append({'ID': id, 'Speed': speed, 'Time': current_time})

# # #     # تحديث حدود السرعة بناءً على عدد المركبات
# # #     update_speed_limit(vehicles_in_time_frame)

# # #     # رسم لوحة السرعة الافتراضية بشكل مربع أكبر
# # #     square_x, square_y = 850, 400  # إحداثيات مركز المربع (يمكن تعديلها حسب الحاجة)
# # #     square_size = 150  # حجم المربع (150x150 بكسل)

# # #     # رسم المربع بخلفية بيضاء
# # #     cv2.rectangle(frame,
# # #                   (square_x - square_size // 2, square_y - square_size // 2),
# # #                   (square_x + square_size // 2, square_y + square_size // 2),
# # #                   (255, 255, 255),
# # #                   -1)

# # #     # رسم الحدود السوداء للمربع
# # #     cv2.rectangle(frame,
# # #                   (square_x - square_size // 2, square_y - square_size // 2),
# # #                   (square_x + square_size // 2, square_y + square_size // 2),
# # #                   (0, 0, 0),
# # #                   3)

# # #     # رسم الحدود الحمراء داخل الحدود السوداء
# # #     cv2.rectangle(frame,
# # #                   (square_x - square_size // 2 + 5, square_y - square_size // 2 + 5),
# # #                   (square_x + square_size // 2 - 5, square_y + square_size // 2 - 5),
# # #                   (0, 0, 255),
# # #                   2)

# # #     # إضافة النص داخل المربع
# # #     text_speed_range = f'{speed_range[0]}-{speed_range[1]}'  # نص السرعة (الحد الأدنى - الحد الأقصى)
# # #     cv2.putText(frame, text_speed_range,
# # #                 (square_x - 40, square_y - 20),
# # #                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)

# # #     # كتابة "km/h" تحت الرقم
# # #     cv2.putText(frame, 'km/h',
# # #                 (square_x - 30, square_y + 30),
# # #                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

# # #     # رسم خط المنتصف
# # #     cv2.line(frame, (0, middle_line_y), (1020, middle_line_y), (255, 0, 0), 2)
# # #     cv2.putText(frame, 'Middle Line', (10, middle_line_y - 10),
# # #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

# # #     # عرض عدد المركبات في الجزء العلوي الأيمن
# # #     cv2.putText(frame, f'Count: {vehicle_count_middle}', (800, 50),
# # #                 cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# # #     # عرض الفيديو
# # #     out.write(frame)
# # #     cv2.imshow('Traffic Monitoring', frame)

# # #     # إنهاء العملية عند الضغط على "q"
# # #     if cv2.waitKey(1) & 0xFF == ord('q'):
# # #         break

# # # # إنهاء العملية
# # # cap.release()
# # # out.release()
# # # cv2.destroyAllWindows()

# # # # حفظ المخالفات في ملف CSV بعد انتهاء الفيديو
# # # if violations:
# # #     violations_df = pd.DataFrame(violations)
# # #     violations_df.to_csv(os.path.join(output_folder, 'violations.csv'), index=False)
# # #     print(f"تم حفظ المخالفات في الملف: {os.path.join(output_folder, 'violations.csv')}")
# # # else:
# # #     print("لا توجد مخالفات لتسجيلها.")

# # import cv2
# # import os
# # import pandas as pd
# # from ultralytics import YOLO
# # import time
# # import math

# # class Tracker:
# #     def __init__(self):
# #         self.center_points = {}
# #         self.id_count = 0

# #     def update(self, objects_rect):
# #         objects_bbs_ids = []
# #         for rect in objects_rect:
# #             x, y, w, h = rect
# #             cx = (x + x + w) // 2
# #             cy = (y + y + h) // 2
# #             same_object_detected = False
# #             for id, pt in self.center_points.items():
# #                 dist = math.hypot(cx - pt[0], cy - pt[1])
# #                 if dist < 35:
# #                     self.center_points[id] = (cx, cy)
# #                     objects_bbs_ids.append([x, y, w, h, id])
# #                     same_object_detected = True
# #                     break
# #             if not same_object_detected:
# #                 self.center_points[self.id_count] = (cx, cy)
# #                 objects_bbs_ids.append([x, y, w, h, self.id_count])
# #                 self.id_count += 1

# #         new_center_points = {object_id: self.center_points[object_id] for _, _, _, _, object_id in objects_bbs_ids}
# #         self.center_points = new_center_points
# #         return objects_bbs_ids

# # # Load YOLO model
# # model = YOLO('yolov8s.pt')
# # class_list = ['car', 'motorcycle', 'truck', 'bus']
# # middle_line_y = 250
# # offset = 6

# # def estimate_speed(location1, location2, fps=20, ppm=8.8):
# #     d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
# #     d_meters = d_pixels / ppm
# #     speed = d_meters * fps * 3.6
# #     return speed

# # def smooth_speed(old_speed, new_speed, alpha=0.7):
# #     if old_speed is None:
# #         return new_speed
# #     return (alpha * old_speed) + ((1 - alpha) * new_speed)

# # def process_video(input_video_path, output_folder):
# #     # Create a tracker object
# #     tracker = Tracker()

# #     cap = cv2.VideoCapture(input_video_path)
# #     if not os.path.exists(output_folder):
# #         os.makedirs(output_folder)

# #     # Output video path
# #     output_video_path = os.path.join(output_folder, 'output.mp4')
# #     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# #     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (1020, 500))

# #     counter_middle = []
# #     vehicle_count_middle = 0
# #     car_speed = {}

# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             break

# #         frame = cv2.resize(frame, (1020, 500))

# #         # YOLO prediction
# #         results = model.predict(frame)
# #         detections = results[0].boxes.data.detach().cpu().numpy()
# #         detections_df = pd.DataFrame(detections).astype("float")

# #         vehicles = []

# #         for _, row in detections_df.iterrows():
# #             x1, y1, x2, y2, class_id = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[5])
# #             vehicle_class = class_list[class_id] if class_id < len(class_list) else None
# #             if vehicle_class in class_list:
# #                 vehicles.append([x1, y1, x2, y2])

# #         bbox_id = tracker.update(vehicles)
# #         vehicle_count_middle = len(counter_middle)

# #         for bbox in bbox_id:
# #             x3, y3, x4, y4, id = bbox
# #             cx, cy = (x3 + x4) // 2, (y3 + y4) // 2

# #             if middle_line_y - offset < cy < middle_line_y + offset:
# #                 if id not in counter_middle:
# #                     counter_middle.append(id)
# #                     vehicle_count_middle += 1

# #             if id in car_speed:
# #                 old_speed = car_speed[id]['speed']
# #                 old_position = car_speed[id]['position']
# #                 new_position = [cx, cy]
# #                 new_speed = estimate_speed(old_position, new_position)
# #                 smoothed_speed = smooth_speed(old_speed, new_speed)
# #                 car_speed[id] = {'speed': smoothed_speed, 'position': new_position}
# #             else:
# #                 car_speed[id] = {'speed': None, 'position': [cx, cy]}

# #             cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 1)
# #             cv2.putText(frame, f'ID: {id}', (x3, y3 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

# #             if car_speed[id]['speed'] is not None:
# #                 cv2.putText(frame, f'Speed: {int(car_speed[id]["speed"])} km/h', (x3, y3 - 5),
# #                             cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)

# #         # Draw the middle line
# #         cv2.line(frame, (0, middle_line_y), (1020, middle_line_y), (255, 0, 0), 2)
# #         cv2.putText(frame, 'Middle Line', (10, middle_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
# #         out.write(frame)

# #     cap.release()
# #     out.release()

# #     return output_video_path
# import cv2
# import os
# import pandas as pd
# from ultralytics import YOLO
# import time
# import math

# class Tracker:
#     def __init__(self):
#         self.center_points = {}
#         self.id_count = 0

#     def update(self, objects_rect):
#         objects_bbs_ids = []
#         for rect in objects_rect:
#             x, y, w, h = rect
#             cx = (x + x + w) // 2
#             cy = (y + y + h) // 2
#             same_object_detected = False
#             for id, pt in self.center_points.items():
#                 dist = math.hypot(cx - pt[0], cy - pt[1])
#                 if dist < 35:
#                     self.center_points[id] = (cx, cy)
#                     objects_bbs_ids.append([x, y, w, h, id])
#                     same_object_detected = True
#                     break
#             if not same_object_detected:
#                 self.center_points[self.id_count] = (cx, cy)
#                 objects_bbs_ids.append([x, y, w, h, self.id_count])
#                 self.id_count += 1

#         new_center_points = {object_id: self.center_points[object_id] for _, _, _, _, object_id in objects_bbs_ids}
#         self.center_points = new_center_points
#         return objects_bbs_ids

# # Load YOLO model
# model = YOLO('yolov8s.pt')
# class_list = ['car', 'motorcycle', 'truck', 'bus']
# middle_line_y = 250
# offset = 6

# def estimate_speed(location1, location2, fps=20, ppm=8.8):
#     d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
#     d_meters = d_pixels / ppm
#     speed = d_meters * fps * 3.6
#     return speed

# def smooth_speed(old_speed, new_speed, alpha=0.7):
#     if old_speed is None:
#         return new_speed
#     return (alpha * old_speed) + ((1 - alpha) * new_speed)

# def process_video(input_video_path, output_folder):
#     # Create a tracker object
#     tracker = Tracker()

#     cap = cv2.VideoCapture(input_video_path)
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     # Output video path
#     output_video_path = os.path.join(output_folder, 'output.mp4')
#     # Using H264 codec, which should ensure browser compatibility
#     fourcc = cv2.VideoWriter_fourcc(*'avc1')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (1020, 500))

#     counter_middle = []
#     vehicle_count_middle = 0
#     car_speed = {}

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame = cv2.resize(frame, (1020, 500))

#         # YOLO prediction
#         results = model.predict(frame)
#         detections = results[0].boxes.data.detach().cpu().numpy()
#         detections_df = pd.DataFrame(detections).astype("float")

#         vehicles = []

#         for _, row in detections_df.iterrows():
#             x1, y1, x2, y2, class_id = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[5])
#             vehicle_class = class_list[class_id] if class_id < len(class_list) else None
#             if vehicle_class in class_list:
#                 vehicles.append([x1, y1, x2, y2])

#         bbox_id = tracker.update(vehicles)
#         vehicle_count_middle = len(counter_middle)

#         for bbox in bbox_id:
#             x3, y3, x4, y4, id = bbox
#             cx, cy = (x3 + x4) // 2, (y3 + y4) // 2

#             if middle_line_y - offset < cy < middle_line_y + offset:
#                 if id not in counter_middle:
#                     counter_middle.append(id)
#                     vehicle_count_middle += 1

#             if id in car_speed:
#                 old_speed = car_speed[id]['speed']
#                 old_position = car_speed[id]['position']
#                 new_position = [cx, cy]
#                 new_speed = estimate_speed(old_position, new_position)
#                 smoothed_speed = smooth_speed(old_speed, new_speed)
#                 car_speed[id] = {'speed': smoothed_speed, 'position': new_position}
#             else:
#                 car_speed[id] = {'speed': None, 'position': [cx, cy]}

#             cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 1)
#             cv2.putText(frame, f'ID: {id}', (x3, y3 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

#             if car_speed[id]['speed'] is not None:
#                 cv2.putText(frame, f'Speed: {int(car_speed[id]["speed"])} km/h', (x3, y3 - 5),
#                             cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)

#         # Draw the middle line
#         cv2.line(frame, (0, middle_line_y), (1020, middle_line_y), (255, 0, 0), 2)
#         cv2.putText(frame, 'Middle Line', (10, middle_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
#         out.write(frame)

#     cap.release()
#     out.release()

#     return output_video_path
import cv2
import os
import pandas as pd
from ultralytics import YOLO
import time
import math

class Tracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0

    def update(self, objects_rect):
        objects_bbs_ids = []
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if dist < 35:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        new_center_points = {object_id: self.center_points[object_id] for _, _, _, _, object_id in objects_bbs_ids}
        self.center_points = new_center_points
        return objects_bbs_ids

# Load the YOLO model
model = YOLO('yolov8s.pt')
class_list = ['car', 'motorcycle', 'truck', 'bus']

middle_line_y = 250
offset = 6
default_speed_range = [80, 100]
speed_range = default_speed_range.copy()
speed_limits = {
    "low": [80, 100],
    "medium": [60, 80],
    "high": [40, 60]
}

def estimate_speed(location1, location2, fps=20, ppm=8.8):
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    d_meters = d_pixels / ppm
    speed = d_meters * fps * 3.6
    return speed

def smooth_speed(old_speed, new_speed, alpha=0.7):
    if old_speed is None:
        return new_speed
    return (alpha * old_speed) + ((1 - alpha) * new_speed)

def update_speed_limit(vehicle_count, vehicles_in_time_frame, last_change_time):
    global speed_range
    time_since_last_change = time.time() - last_change_time

    if vehicle_count <= 10 and time_since_last_change >= 45:
        speed_range = speed_limits["medium"]
        vehicles_in_time_frame = 0
        last_change_time = time.time()
    elif vehicle_count <= 15 and time_since_last_change >= 45:
        speed_range = speed_limits["high"]
        vehicles_in_time_frame = 0
        last_change_time = time.time()
    elif time_since_last_change >= 45:
        speed_range = default_speed_range
        vehicles_in_time_frame = 0
        last_change_time = time.time()

    return vehicles_in_time_frame, last_change_time

def process_video(input_video_path, output_folder):
    tracker = Tracker()

    cap = cv2.VideoCapture(input_video_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_video_path = os.path.join(output_folder, 'output.mp4')

    # Using H264 codec (avc1) to ensure browser compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (1020, 500))

    counter_middle = []
    vehicle_count_middle = 0
    vehicles_in_time_frame = 0
    last_change_time = time.time()
    car_speed = {}

    violations = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1020, 500))
        results = model.predict(frame)
        detections = results[0].boxes.data.detach().cpu().numpy()
        detections_df = pd.DataFrame(detections).astype("float")

        vehicles = []
        for _, row in detections_df.iterrows():
            x1, y1, x2, y2, class_id = int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[5])
            vehicle_class = class_list[class_id] if class_id < len(class_list) else None
            if vehicle_class in class_list:
                vehicles.append([x1, y1, x2, y2])

        bbox_id = tracker.update(vehicles)

        vehicle_count_middle = len(counter_middle)

        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox
            cx, cy = (x3 + x4) // 2, (y3 + y4) // 2

            if middle_line_y - offset < cy < middle_line_y + offset:
                if id not in counter_middle:
                    counter_middle.append(id)
                    vehicle_count_middle += 1
                    vehicles_in_time_frame += 1

            if id in car_speed:
                old_speed = car_speed[id]['speed']
                old_position = car_speed[id]['position']
                new_position = [cx, cy]
                new_speed = estimate_speed(old_position, new_position)
                smoothed_speed = smooth_speed(old_speed, new_speed)
                car_speed[id] = {'speed': smoothed_speed, 'position': new_position}
            else:
                car_speed[id] = {'speed': None, 'position': [cx, cy]}

            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 1)
            cv2.putText(frame, f'ID: {id}', (x3, y3 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            if car_speed[id]['speed'] is not None:
                cv2.putText(frame, f'Speed: {int(car_speed[id]["speed"])} km/h', (x3, y3 - 5),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)

                speed = int(car_speed[id]['speed'])
                if speed > speed_range[1]:
                    current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    violations.append({'ID': id, 'Speed': speed, 'Time': current_time})

        vehicles_in_time_frame, last_change_time = update_speed_limit(vehicles_in_time_frame, vehicles_in_time_frame, last_change_time)

        square_x, square_y = 850, 400
        square_size = 150
        cv2.rectangle(frame, (square_x - square_size // 2, square_y - square_size // 2),
                      (square_x + square_size // 2, square_y + square_size // 2), (255, 255, 255), -1)
        cv2.rectangle(frame, (square_x - square_size // 2, square_y - square_size // 2),
                      (square_x + square_size // 2, square_y + square_size // 2), (0, 0, 0), 3)
        cv2.rectangle(frame, (square_x - square_size // 2 + 5, square_y - square_size // 2 + 5),
                      (square_x + square_size // 2 - 5, square_y + square_size // 2 - 5), (0, 0, 255), 2)

        text_speed_range = f'{speed_range[0]}-{speed_range[1]}'
        cv2.putText(frame, text_speed_range, (square_x - 40, square_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
        cv2.putText(frame, 'km/h', (square_x - 30, square_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        cv2.line(frame, (0, middle_line_y), (1020, middle_line_y), (255, 0, 0), 2)
        cv2.putText(frame, 'Middle Line', (10, middle_line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        cv2.putText(frame, f'Count: {vehicle_count_middle}', (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        out.write(frame)

    cap.release()
    out.release()

    return output_video_path
