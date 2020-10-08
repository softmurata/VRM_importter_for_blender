import sys
import os
import shutil
import json
from collections import OrderedDict
import bpy

# script_filename = os.path.basename(__file__)
# script_filepath = bpy.data.texts[script_filename].filepath
# script_dirpath = os.path.dirname(script_filepath)
script_dirpath = "C:/Users/TeamvRAN/Downloads/VRM_IMPORTER_for_Blender2_8/"
sys.path += [script_dirpath]

import V_Types as VRM_Types
from gl_const import GL_CONSTANS as GLC
sys.path += [os.path.join(script_dirpath, 'importer')]
from importer import binaly_loader
import datetime

def parse_glb(data: bytes):
    reader = binaly_loader.Binaly_Reader(data)
    magic = reader.read_str(4)
    if magic != 'glTF':
        raise Exception('glTF header signature not found: #{}'.format(magic))

    version = reader.read_as_dataType(GLC.UNSIGNED_INT)
    if version != 2:
        raise Exception('version #{} found. This plugin only supports version 2'.format(version))

    size = reader.read_as_dataType(GLC.UNSIGNED_INT)
    size -= 12

    json_str = None
    body = None
    while size > 0:
        # print(size)

        if json_str is not None and body is not None:
            raise Exception('This VRM has multiple chunks, this plugin reads one chunk only.')

        chunk_size = reader.read_as_dataType(GLC.UNSIGNED_INT)
        size -= 4

        chunk_type = reader.read_str(4)
        size -= 4

        chunk_data = reader.read_binaly(chunk_size)
        size -= chunk_size

        if chunk_type == 'BIN\x00':
            body = chunk_data
        elif chunk_type == 'JSON':
            json_str = chunk_data.decode('utf-8')#blenderのpythonverが古く自前decode要す
        else:
            raise Exception('unknown chunk_type: {}'.format(chunk_type))

    return json.loads(json_str,object_pairs_hook=OrderedDict), body


def invalid_chars_remover(filename):
    unsafe_chars = {
            0: '\x00', 1: '\x01', 2: '\x02', 3: '\x03', 4: '\x04', 5: '\x05', 6: '\x06', 7: '\x07', 8: '\x08', 9: '\t', 10: '\n',\
            11: '\x0b', 12: '\x0c', 13: '\r', 14: '\x0e', 15: '\x0f', 16: '\x10', 17: '\x11', 18: '\x12', 19: '\x13', 20: '\x14',\
            21: '\x15', 22: '\x16', 23: '\x17', 24: '\x18', 25: '\x19', 26: '\x1a', 27: '\x1b', 28: '\x1c', 29: '\x1d', 30: '\x1e',\
            31: '\x1f', 34: '"', 42: '*', 47: '/', 58: ':', 60: '<', 62: '>', 63: '?', 92: '\\', 124: '|'
            } #32:space #33:! 
    remove_table = str.maketrans("","","".join([chr(charnum) for charnum in unsafe_chars.keys()]))
    safe_filename = filename.translate(remove_table)
    return safe_filename
    

def get_meta(vrm_pydata, param, defa, cla):
    return vrm_pydata.json["extensions"]["VRM"]["meta"].get(param)[:cla] if vrm_pydata.json["extensions"]["VRM"]["meta"].get(param) is not None else defa


def extract_texture_images(filepath, texture_dir, model_title):
    # filepath is absolute file path
    vrm_pydata = VRM_Types.VRM_pydata(filepath=filepath)
    
    # parser glb file
    with open(filepath, 'rb') as f:
        vrm_pydata.json, body_binary = parse_glb(f.read())
        
    # Initialize binary reader
    binary_reader = binaly_loader.Binaly_Reader(body_binary)
    bufferViews = vrm_pydata.json["bufferViews"]
    
    os.makedirs(texture_dir, exist_ok=True)
    dir_name = invalid_chars_remover(f"{model_title}")
    dir_path = os.path.join(texture_dir, dir_name)

    if dir_name == "no_title":
        dir_name = invalid_chars_remover(datetime.datetime.today().strftime("%M%D%H%I%M%S"))
        for i in range(10):
            dn = f"{dir_name}_{i}"
            if os.path.exists(os.path.join(texture_dir, dn)):
                continue
            elif os.path.exists(os.path.join(texture_dir, dn)):
                dir_path = os.path.join(texture_dir, dn)
                break
            else:
                os.mkdir(os.path.join(texture_dir, dn))
                dir_path = os.path.join(texture_dir, dn)
                break
            
    elif not os.path.exists(os.path.join(texture_dir, dir_name)):
        os.mkdir(dir_path)

    for idx, image_prop in enumerate(vrm_pydata.json["images"]):
        if "extra" in image_prop:
            image_name = image_prop["extra"]["name"]
        else:
            image_name = image_prop["name"]
            
        binary_reader.set_pos(bufferViews[image_prop["bufferView"]]["byteOffset"])
        image_binary = binary_reader.read_binaly(bufferViews[image_prop["bufferView"]]["byteLength"])
        image_type = image_prop["mimeType"].split("/")[-1]
        
        if image_name == "":
            image_name = "texture_" + str(idx)
            print(" no name image is named ".format(image_name))
        elif len(image_name) >= 50:
            print(" too long ")
            image_name = "tex_2longname_" + str(idx)
            
        
        image_name = invalid_chars_remover(image_name)
        image_path = os.path.join(dir_path, image_name + "." + image_type)
        
        if not os.path.exists(image_path):
            with open(image_path, "wb") as imageWriter:
                imageWriter.write(image_binary)
                
        elif image_name in [img.name for img in vrm_pydata.image_propaties]:
            written_flag = False
            for i in range(5):
                second_image_name = image_name + "_" + str(i)
                image_path = os.path.join(dir_path, second_image_name + "." + image_type)
                if not os.path.exists(image_path):
                    with open(image_path, "wb") as imageWriter:
                        imageWriter.write(image_binary)
                    image_name = second_image_name
                    written_flag = True
                    break
                
            if not written_flag:
                print("There are more than 5 images")
                
        else:
            print(image_name + 'already exists')
            
        image_propaty = VRM_Types.Image_props(image_name, image_path, image_type)
        vrm_pydata.image_propaties.append(image_propaty)
        

def get_model_title(filepath):
    regist_data_path = 'C:/Users/TeamVRAN/Documents/VRFactory/data_regist.json'
    f = open(regist_data_path)
    database = json.load(f)
    f.close()
    vrm_number = filepath.split('/')[-1].split('.')[0]
    
    return database[vrm_number]


# main function for creating base glb file + texture dir
vrm_files = os.listdir('C:/Users/TeamVRAN/Downloads/VRModel/')
vrm_files = ['C:/Users/TeamVRAN/Downloads/VRModel/' + v for v in vrm_files]

for filepath in vrm_files:
    model_title = get_model_title(filepath)
    texture_path = 'C:/Users/TeamVRAN/Documents/VRFactory/Textures/'
    print()
    print('----model_title {}----'.format(model_title))
    glbpath = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/{}.glb'.format(model_title)
    os.makedirs(texture_path, exist_ok=True)

        
    extract_texture_images(filepath, texture_path, model_title)

    shutil.copy(filepath, glbpath)

"""
# main function 
filepath = 'C:/Users/TeamVRAN/Downloads/VRModel/5382062288.vrm'
model_title = get_model_title(filepath)
texture_path = 'C:/Users/TeamVRAN/Documents/VRFactory/Textures/'
print()
print('----model_title {}----'.format(model_title))
glbpath = 'C:/Users/TeamVRAN/Documents/VRFactory/VRDatasetGLB/{}.glb'.format(model_title)
os.makedirs(texture_path, exist_ok=True)

    
extract_texture_images(filepath, texture_path, model_title)

shutil.copy(filepath, glbpath)
"""
    
