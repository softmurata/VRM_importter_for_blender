import bpy

def auto_materials(glb_path, target_texture_dir, obj_path):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    # import glb file
    bpy.ops.import_scene.gltf(filepath=glb_path)
    
    # shading viewport(needed?)
    for area in bpy.context.screen.areas: # iterate through areas in current screen
        if area.type == 'VIEW_3D':
            for space in area.spaces: # iterate through spaces in current VIEW_3D area
                if space.type == 'VIEW_3D': # check if space is a 3D view
                    space.viewport_shade = 'RENDERED' # set the viewport shading to rendered


    all_materials = bpy.data.materials[1:-1]

    all_images = bpy.data.images
    for image in all_images:
        all_images.remove(image)
        
    for idx, target_material in enumerate(all_materials):
        active_object = bpy.context.active_object
        material_name = target_material.name
        print('material names:', material_name)
        # get node_tree and nodes
        target_node_tree = target_material.node_tree
        target_nodes = target_node_tree.nodes
        # remove default nodes
        for node in target_nodes:
            target_nodes.remove(node)
        # create new nodes
        texcoord_node = target_nodes.new('ShaderNodeTexCoord')
        texcoord_node.location = (-439.184814453125, 150.6854705810547)
        teximage_node = target_nodes.new('ShaderNodeTexImage')
        teximage_node.location = (-164.83763122558594, 147.45022583007812)
        image_names = material_name.split('_')
        print('image names:', image_names)
        image_name = ''
        if len(image_names[4]) > 2:
            for idx in range(len(image_names)):
                if idx == 4:
                    continue
                image_name += '{}_'.format(image_names[idx])
        else:
            image_names = image_names[:-1]
            for n in image_names:
                image_name += '{}_'.format(n)
            
        image_name = image_name[:-1]
        bpy.data.images.load(target_texture_dir + image_name + '.png')
        teximage_node.image = bpy.data.images[image_name]
        # change projection mode
        teximage_node.projection = 'BOX'
        
        # load image
        pbsdf_node = target_nodes.new('ShaderNodeBsdfPrincipled')
        pbsdf_node.location = (276.5877990722656, 159.6053009033203)
        material_output_node = target_nodes.new('ShaderNodeOutputMaterial')
        material_output_node.location = (633.8919677734375, 126.1744613647461)
        # TexCoords, TexImage, Principled BSDF, Material Output

        # create links
        # Initialize links
        links = target_node_tree.links
        # texcoord attach to tex image
        links.new(texcoord_node.outputs[0], teximage_node.inputs[0])
        
        # tex image attach to Principled BSDF
        links.new(teximage_node.outputs[0], pbsdf_node.inputs[0])
        links.new(teximage_node.outputs[1], pbsdf_node.inputs[18])
        # principled bsdf attach to material output
        links.new(pbsdf_node.outputs[0], material_output_node.inputs[0])
        
        active_object.active_material = target_material
        
    data_name = "Armature"
        
    scene = bpy.context.scene
    for ob in scene.objects:
        if ob.name[:8] == data_name:
            bpy.ops.export_scene.obj(filepath=obj_path)
                
    # delete all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    

"""
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

glb_path = 'C:/Users/TeamVRAN/Downloads/bijin.glb'
texture_path = 'C:/Users/TeamVRAN/Downloads/Textures/tex_0/'
# import glb file
bpy.ops.import_scene.gltf(filepath=glb_path)

# shading viewport(needed?)
for area in bpy.context.screen.areas: # iterate through areas in current screen
    if area.type == 'VIEW_3D':
        for space in area.spaces: # iterate through spaces in current VIEW_3D area
            if space.type == 'VIEW_3D': # check if space is a 3D view
                space.viewport_shade = 'RENDERED' # set the viewport shading to rendered


all_materials = bpy.data.materials[1:-1]

all_images = bpy.data.images
for image in all_images:
    all_images.remove(image)

for idx, target_material in enumerate(all_materials):
    active_object = bpy.context.active_object
    material_name = target_material.name
    # get node_tree and nodes
    target_node_tree = target_material.node_tree
    target_nodes = target_node_tree.nodes
    # remove default nodes
    for node in target_nodes:
        target_nodes.remove(node)
    # create new nodes
    texcoord_node = target_nodes.new('ShaderNodeTexCoord')
    texcoord_node.location = (-439.184814453125, 150.6854705810547)
    teximage_node = target_nodes.new('ShaderNodeTexImage')
    teximage_node.location = (-164.83763122558594, 147.45022583007812)
    mage_names = material_name.split('_')
    image_name = ''
    if len(image_names[4]) > 2:
        for idx in range(len(image_names)):
            if idx == 4:
                continue
            image_name += '{}_'.format(image_names[idx])
    else:
        image_names = image_names[:-1]
        for n in image_names:
            image_name += '{}_'.format(n)
        
    image_name = image_name[:-1]
    bpy.data.images.load(texture_path + image_name + '.png')
    teximage_node.image = bpy.data.images[image_name]
    # change projection mode
    teximage_node.projection = 'BOX'
    
    # load image
    pbsdf_node = target_nodes.new('ShaderNodeBsdfPrincipled')
    pbsdf_node.location = (276.5877990722656, 159.6053009033203)
    material_output_node = target_nodes.new('ShaderNodeOutputMaterial')
    material_output_node.location = (633.8919677734375, 126.1744613647461)
    # TexCoords, TexImage, Principled BSDF, Material Output

    # create links
    # Initialize links
    links = target_node_tree.links
    # texcoord attach to tex image
    links.new(texcoord_node.outputs[0], teximage_node.inputs[0])
    
    # tex image attach to Principled BSDF
    links.new(teximage_node.outputs[0], pbsdf_node.inputs[0])
    links.new(teximage_node.outputs[1], pbsdf_node.inputs[18])
    # principled bsdf attach to material output
    links.new(pbsdf_node.outputs[0], material_output_node.inputs[0])
    
    active_object.active_material = target_material
    
data_name = "Armature"
    
scene = bpy.context.scene
for ob in scene.objects:
    if ob.name[:8] == data_name:
        bpy.ops.export_scene.obj(filepath='C:/Users/TeamVRAN/Downloads/bijin_ver.obj')
            
# delete all
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)
"""