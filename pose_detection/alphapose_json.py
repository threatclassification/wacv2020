import sys
import numpy as np
import cv2
from os import walk # for listing contents of a directory
from os import isdir # for testing paths
from os import exists # for testing paths
from shutil import copyfile # for copying duplicates to folder (for now)
from shutil import move # for moving duplicates to folder (eventually)
import random
import yaml
import json
import pickle

def json_load_byteified(file_handle):
	return _byteify(
		json.load(file_handle, object_hook=_byteify),
		ignore_dicts=True
	)

def json_loads_byteified(json_text):
	return _byteify(
		json.loads(json_text, object_hook=_byteify),
		ignore_dicts=True
	)

def _byteify(data, ignore_dicts = False):
	# if this is a unicode string, return its string representation
	if isinstance(data, unicode):
		return data.encode('utf-8')
	# if this is a list of values, return list of byteified values
	if isinstance(data, list):
		return [ _byteify(item, ignore_dicts=True) for item in data ]
	# if this is a dictionary, return dictionary of byteified keys and values
	# but only if we haven't already byteified it
	if isinstance(data, dict) and not ignore_dicts:
		return {
			_byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
			for key, value in data.iteritems()
		}
	# if it's anything else, return it in its original form
	return data

def poll_skeleton(joints):
	joint_list = [\
	"   Right Ankle" ,
	"    Right Knee" ,
	"     Right Hip" ,
	"      Left Hip" ,
	"     Left Knee" ,
	"    Left Ankle" ,
	"        Pelvis" ,
	"         Chest" ,
	"          Neck" ,
	"          Pate" ,
	"   Right Wrist" ,
	"   Right Elbow" ,
	"Right Shoulder" ,
	" Left Shoulder" ,
	"    Left Elbow" ,
	"    Left Wrist"]


	print("    Joint     :  x ,  y , confidence")
	for x in range(0,16):
		print("{0}: {1:3d}, {2:3d}, {3}").format(joint_list[x], int(joints[x][0]), int(joints[x][1]),joints[x][2])

def draw_skeleton(image, joints):
	pairs = [\
	(0,1), # right shin
	(1,2), # right thigh
	(2,6), # right hip
	(6,3), # left hip
	(3,4), # left thigh
	(4,5), # left shin
	(6,7), # spine
	(7,8), # neck
	(8,9), # head
	(8,12), #right shoulder
	(12,11), #right bicep
	(11,10), #right forearm
	(10,16), #right gun
	(8,13), #left shoulder
	(13,14), #left bicep
	(14,15)] #left forearm

	for pair in pairs:
		cv2.line(image, (int(joints[pair[0]][0]), int(joints[pair[0]][1])), (int(joints[pair[1]][0]), int(joints[pair[1]][1])), (0,255,0), thickness=1, lineType=8, shift=0) 
	return image

def show_keypoints_on_image(image, joints):
	joint_image = image.copy()
	joint_image = draw_skeleton(image, joints)
	poll_skeleton(joints)
	for joint in joints:
		if joint.all():
			# print("joint (x,y): ({}, {})").format(joint[0], joint[1])
			# random joint color
			# cv2.circle(joint_image, (int(joint[0]),int(joint[1])), 4, (random.randint(0,255),random.randint(0,255),random.randint(0,255)), thickness=-1, lineType=8, shift=0) 
			# black joint color with white center
			cv2.circle(joint_image, (int(joint[0]),int(joint[1])), 5, (0,0,0), thickness=-1, lineType=8, shift=0) 
			cv2.circle(joint_image, (int(joint[0]),int(joint[1])), 2, (255,255,255), thickness=-1, lineType=8, shift=0) 

	cv2.circle(joint_image, (int(joints[-1][0]),int(joints[-1][1])), 8, (0,0,255), thickness=-1, lineType=8, shift=0) 
	cv2.circle(joint_image, (int(joints[-1][0]),int(joints[-1][1])), 6, (255,0,0), thickness=-1, lineType=8, shift=0) 
	cv2.circle(joint_image, (int(joints[-1][0]),int(joints[-1][1])), 4, (0,0,255), thickness=-1, lineType=8, shift=0) 
	cv2.circle(joint_image, (int(joints[-1][0]),int(joints[-1][1])), 2, (255,0,0), thickness=-1, lineType=8, shift=0) 

	
	# 1: 49 # 3: 51 # 5: 53 # 7: 55 # 0: 48
	cv2.namedWindow('joints',cv2.WINDOW_NORMAL)
	while(1):
		print("classify image as either (1)high, (3)medium, (5)mild, (7)low, or (0)zero")
		print("  (1)high:   brandished pistol, aimed position, discharge imminent")
		print("  (3)medium: weapon drawn from holster, but not held in firing position")
		print("  (5)mild:   pistol is holstered, but hand is near or touching the weapon (quickdraw)")
		print("  (7)low:    pistol is present in the frame, but the hands of the individual is not near a drawing position")
		print("  (0)zero:   pistol is erroneously associated with skeleton, or skeleton is poorly formed such that the association is bad")
		cv2.imshow('joints',joint_image)
		cv2.resizeWindow('joints', joint_image.shape[0]*4,joint_image.shape[0]*4)
		
		k = cv2.waitKey(0)
		if k==122: # Esc key to stop
			threat = 0
			break
		if k==49: # 1 = high
			threat = 1
			break
		if k==51: # 3 = medium
			threat = 3
			break
		if k==53: # 5 = mild
			threat = 5
			break
		if k==55: # 7 = low
			threat = 7
			break
		if k==48: # 0 = zero
			threat = 0
			break
		else:
			print k
	cv2.destroyWindow("joints")
	return threat, joint_image

def check_pistol_cropped_location(potential_threat, cv_image, crop_image_offset):
	# potential_threat = {
	# 'xmin':person_box['xmin'],
	# 'ymin':person_box['ymin'],
	# 'xmax':person_box['xmax'],
	# 'ymax':person_box['ymax'], 
	# 'pistol_x':pistol_box['center_x']-person_box['xmin'], 
	# 'pistol_y':pistol_box['center_y']-person_box['ymin']
	# }

	if potential_threat['xmin'] < crop_image_offset: 
		x = potential_threat['pistol_x'] + potential_threat['xmin']
	else:
		x = potential_threat['pistol_x'] + crop_image_offset

	if potential_threat['ymin'] < crop_image_offset: 
		y = potential_threat['pistol_y'] + potential_threat['ymin']
	else:
		y = potential_threat['pistol_y'] + crop_image_offset
	return x,y 

def img_crop(image, x_min, x_max, y_min, y_max):
	if (x_min <= 0):
		x_min = 0
	if (y_min <=0 ):
		y_min = 0
	if (x_max >= image.shape[1]):
		x_max = image.shape[1]
	if (y_max >= image.shape[0]):
		y_max = image.shape[0]

	cropped_image = image[y_min:y_max, x_min:x_max]
	return cropped_image

def box_overlap(human_box, gun_box):
	# Overlapping rectangles overlap both horizontally & vertically
	x_bool = range_overlap(human_box["xmin"], human_box["xmax"], gun_box["xmin"], gun_box["xmax"])
	y_bool = range_overlap(human_box["ymin"], human_box["ymax"], gun_box["ymin"], gun_box["ymax"])
	return x_bool and y_bool

def joint_overlap(human_box, jointmin, jointmax):
	# Overlapping rectangles overlap both horizontally & vertically
	x_bool = range_overlap(human_box["xmin"], human_box["xmax"], jointmin[0], jointmax[0])
	y_bool = range_overlap(human_box["ymin"], human_box["ymax"], jointmin[1], jointmax[1])
	return x_bool and y_bool

def range_overlap(a_min, a_max, b_min, b_max):
	# Neither range is completely greater than the other
	return (a_min <= b_max) and (b_min <= a_max)


def main():
	print("\n\n\n\n\n\n\n")

	# Setup config
	with open("alphapose.yaml", 'r') as ymlfile:
		if sys.version_info[0] > 2:
			cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
		else:
			cfg = yaml.load(ymlfile)


	jsondata = json_load_byteified(open(cfg['json_file']))

	if (cfg['model_pose'] == "BODY_25"):
		subimage_folder = cfg['subimage_body25']
	elif (cfg['model_pose'] == "MPI"):
		subimage_folder = cfg['subimage_mpii']
	else:
		print("Incorrect setting for skeletons")
		return

	print("subimage_folder:   {}").format(subimage_folder)

	if (cfg['model_pose'] == "BODY_25"):
		x = np.empty((1,9,2))
		rele_dexes = [1,2,3,4,5,6,7,8,9,12]		
		right_elbow = 3
		right_wrist = 4
	elif (cfg['model_pose'] == "MPI"):
		x = np.empty((1,10,2))
		rele_dexes = [1,2,3,4,5,6,7,8,11,14]		
		right_elbow = 3
		right_wrist = 4
	else:
		print("ERROR: MUST CHOSE EITHER 'BODY_25' OR 'MPI' FOR 'model_pose'")
		return

	number_highs = 0
	number_meds = 0
	number_milds = 0
	number_lows = 0
	number_zeros = 0

	# check overlapping boxes & associate pistols with people
	for (dirpath, dirnames, filenames) in walk(subimage_folder+'high/images/'):
		number_highs = len(filenames)
		break
	for (dirpath, dirnames, filenames) in walk(subimage_folder+'medium/images/'):
		number_meds = len(filenames)
		break
	for (dirpath, dirnames, filenames) in walk(subimage_folder+'mild/images/'):
		number_milds = len(filenames)
		break
	for (dirpath, dirnames, filenames) in walk(subimage_folder+'low/images/'):
		number_lows = len(filenames)
		break
	for (dirpath, dirnames, filenames) in walk(subimage_folder+'zero/images/'):
		number_zeros = len(filenames)
		break

	print("number_meds: {}").format(number_meds)


	print("\n\n")

	print(len(jsondata)/25)


 
	# n = 0
	# blockn = []

	# for entry in range(n*25, n*25+25):
	# 	blockn.append(jsondata[entry])
	# 	print("\n jsondata[{}]: {}").format(entry, jsondata[entry])
		
	# print("\n\n\n")
	# n = 1
	# blockn = []
	# for entry in range(n*25, n*25+25):
	# 	blockn.append(jsondata[entry])
	# 	print("\n jsondata[{}]: {}").format(entry, jsondata[entry])



	# for entry in range(0, len(jsondata))
	# for entry in jsondata:
	# 	# entry = jsondata[201]
	# 	# print(entry)
	# 	# load image and labels relating to this json entry
	# 	image_filename = entry['image_id']
	# 	current_image = cfg['src_images'] + image_filename
	# 	print("current_image:  {}").format(current_image)
	# 	cv_image = cv2.imread(current_image,cv2.IMREAD_COLOR) #load image in cv2
	# 	cv_img_height = cv_image.shape[0]
	# 	cv_img_width = cv_image.shape[1]

	# 	label_file = cfg['label_folder']+image_filename[:-4]+".txt"
	# 	print("label file:     {}").format(label_file)
	# 	person_boxes = []
	# 	pistol_boxes = []

	# 	try:
	# 		with open(label_file) as file:
	# 			for line in file: 
	# 				line = line.strip().split() #or some other preprocessing
	# 				# print("line: {}").format(line)
	# 				box_center_x = float(line[1])*cv_img_width
	# 				box_center_y = float(line[2])*cv_img_height
	# 				box_width = float(line[3])*cv_img_width
	# 				box_height = float(line[4])*cv_img_height
	# 				x_min = int(round(box_center_x - (box_width/2)))
	# 				x_max = int(round(box_center_x + (box_width/2)))
	# 				y_min = int(round(box_center_y - (box_height/2)))
	# 				y_max = int(round(box_center_y + (box_height/2)))
	# 				if line[0] == "0": # then it is a pistol
	# 					# pistol_boxes.append({'xmin':x_min,'ymin':y_min,'xmax':x_max,'ymax':y_max})
	# 					pistol_boxes.append({
	# 						'xmin':x_min,'ymin':y_min, 'xmax':x_max,'ymax':y_max, 
	# 						'center_x':box_center_x, 'center_y':box_center_y})
	# 				if line[0] == "1": # then it is a person
	# 					person_boxes.append({'xmin':x_min,'ymin':y_min,'xmax':x_max,'ymax':y_max})
	# 	except:
	# 		print("Could not open label file: {}").format(label_file)
	# 		continue

	# 	joints = np.asarray(entry['keypoints'])
	# 	joints = np.reshape(joints, (16, 3))

	# 	jointmax = np.amax(joints, axis=0)
	# 	jointmin = np.amin(joints, axis=0)

	# 	print("jointmax: {}").format(jointmax)
	# 	print("jointmin: {}").format(jointmin)

	# 	for person_box in person_boxes:
	# 		for pistol_box in pistol_boxes:
	# 			cv_image = cv2.imread(current_image,cv2.IMREAD_COLOR) #load image in cv2
	# 			if box_overlap(person_box, pistol_box) and joint_overlap(person_box, jointmin, jointmax):
	# 				# add "joint" for gun
	# 				pistol_location = ([pistol_box['center_x'], pistol_box['center_y'], 0])
	# 				# print("pistol_location: {}").format(pistol_location)
	# 				pistol_joints = np.vstack((joints,pistol_location))
	# 				# draw joints on person and ask for input on classification
	# 				threat_class, joint_image = show_keypoints_on_image(cv_image, pistol_joints)
	# 				# print("pistol pixel center: {}, {}").format(pistol_box['center_x'], pistol_box['center_y'])
	# 				# print("joints 16x3: {}").format(joints)
	# 				print("threat_class: {}").format(threat_class)

	# 				if threat_class == 1: # high threat
	# 					print("    threat_class: {}").format("high")
	# 					if cfg['save_skeltons']:
	# 						image_file = ("{0}{1}high_threat_{2:06d}").format(subimage_folder, 'high/images/',number_highs)
	# 						skeleton_file = ("{0}{1}high_threat_{2:06d}").format(subimage_folder, 'high/skeletons/',number_highs)
	# 						cv2.imwrite(image_file+".jpg", joint_image) # save skeleton image
	# 						np.save(skeleton_file+".npy", pistol_joints) # Save numpy arrays
	# 						np.savetxt(skeleton_file+".txt", pistol_joints, delimiter=',', fmt='%4.2f')   # X is an array
	# 						print("      {}").format(skeleton_file)
	# 					number_highs += 1
	# 				elif threat_class == 3: # medium threat
	# 					print("    threat_class: {}").format("medium")
	# 					if cfg['save_skeltons']:
	# 						image_file = ("{0}{1}medium_threat_{2:06d}").format(subimage_folder, 'medium/images/',number_meds)
	# 						skeleton_file = ("{0}{1}medium_threat_{2:06d}").format(subimage_folder, 'medium/skeletons/',number_meds)
	# 						cv2.imwrite(image_file+".jpg", joint_image) # save skeleton image
	# 						np.save(skeleton_file+".npy", pistol_joints) # Save numpy arrays
	# 						np.savetxt(skeleton_file+".txt", pistol_joints, delimiter=',', fmt='%4.2f')   # X is an array
	# 						print("      {}").format(skeleton_file)
	# 					number_meds += 1
	# 				elif threat_class == 5: # mild threat
	# 					print("    threat_class: {}").format("mild")
	# 					if cfg['save_skeltons']:
	# 						image_file = ("{0}{1}mild_threat_{2:06d}").format(subimage_folder, 'mild/images/',number_milds)
	# 						skeleton_file = ("{0}{1}mild_threat_{2:06d}").format(subimage_folder, 'mild/skeletons/',number_milds)
	# 						cv2.imwrite(image_file+".jpg", joint_image) # save skeleton image
	# 						np.save(skeleton_file+".npy", pistol_joints) # Save numpy arrays
	# 						np.savetxt(skeleton_file+".txt", pistol_joints, delimiter=',', fmt='%4.2f')   # X is an array
	# 						print("      {}").format(skeleton_file)
	# 					number_milds += 1
	# 				elif threat_class == 7: # low threat
	# 					print("    threat_class: {}").format("low")
	# 					if cfg['save_skeltons']:
	# 						image_file = ("{0}{1}low_threat_{2:06d}").format(subimage_folder, 'low/images/',number_lows)
	# 						skeleton_file = ("{0}{1}low_threat_{2:06d}").format(subimage_folder, 'low/skeletons/',number_lows)
	# 						cv2.imwrite(image_file+".jpg", joint_image) # save skeleton image
	# 						np.save(skeleton_file+".npy", pistol_joints) # Save numpy arrays
	# 						np.savetxt(skeleton_file+".txt", pistol_joints, delimiter=',', fmt='%4.2f')   # X is an array
	# 						print("      {}").format(skeleton_file)
	# 					number_lows += 1
	# 				elif threat_class == 0: # zero threat
	# 					print("    threat_class: {}").format("zero")
	# 					if cfg['save_skeltons']:
	# 						image_file = ("{0}{1}zero_threat_{2:06d}").format(subimage_folder, 'zero/images/',number_zeros)
	# 						skeleton_file = ("{0}{1}zero_threat_{2:06d}").format(subimage_folder, 'zero/skeletons/',number_zeros)
	# 						cv2.imwrite(image_file+".jpg", joint_image) # save skeleton image
	# 						np.save(skeleton_file+".npy", pistol_joints) # Save numpy arrays
	# 						np.savetxt(skeleton_file+".txt", pistol_joints, delimiter=',', fmt='%4.2f')   # X is an array
	# 						print("      {}").format(skeleton_file)
	# 					number_zeros += 1
	# 				else:
	# 					print("should never get here, something weird happened")
	# 				#move original image to sorted folder





if __name__ == "__main__":
	main()



# with open('person.json') as f:
#   data = json.load(f)

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}

