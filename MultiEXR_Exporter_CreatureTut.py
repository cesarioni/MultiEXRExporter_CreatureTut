import bpy
import os
import pathlib
import pprint
C = bpy.context
tree = bpy.context.scene.node_tree
###INSTRUCTIONS:
#1.Create a volume material with the name of volume
#2.Put all the lights and cameras in one separate collection
#(if you click the delete collection button this collection will also be removed)
#The script will create a default view layer to render all the scene

#####################FUNCTIONS
####################Create collections functions
def getFileBaseName():
    fileName = bpy.path.basename(bpy.context.blend_data.filepath)
    fileName = fileName.split(".")
    baseName = fileName[0]
    baseName = baseName.split("_")
    return baseName[0]

def remove_compositor_nodes():
    bpy.context.scene.use_nodes = True
    bpy.context.scene.node_tree.nodes.clear()     

def createOutputs(nameFile, prefix):
    render_output = bpy.context.scene.node_tree.nodes.new(type="CompositorNodeOutputFile")
    filepath = bpy.data.filepath
    ## VERSION WITH THE SAME NAME OF THE FILE
    ## subPath = os.path.join(os.path.dirname(filepath), getFileBaseName(), prefix+"_")
    subPath = os.path.join(os.path.dirname(filepath), "render", prefix+"_")
    render_output.base_path=subPath
    render_output.format.file_format='OPEN_EXR_MULTILAYER'
    render_output.format.color_depth='32'
    render_output.format.color_management = 'OVERRIDE'
    render_output.format.view_settings.view_transform='Standard'
    return render_output    

def createCompositorNode( viewLayername, xPos, yPos):
    # Create Render Layer and File Output nodes
    render_layers_node = tree.nodes.new('CompositorNodeRLayers')
    render_layers_node.label = viewLayername
    render_layers_node.layer = viewLayername
    render_layers_node.location = (xPos,yPos)
    return render_layers_node

def setupMultiEXR(render_layers_node ,path):
    # Create File Output nodes
    name = render_layers_node.layer
    file_output_node = createOutputs(path + "_" + name, name)
    file_output_node.location.x = render_layers_node.location.x + 700
    file_output_node.location.y = render_layers_node.location.y 
    file_output_node.layer_slots.clear()
    for count, socket in enumerate(render_layers_node.outputs):
        #Removing Alpha and noisy image output
        if socket.name=="Alpha":
            socket.enabled = False
        if socket.name=="Noisy Image":
            socket.enabled = False
        # End of Removing Alpha and noisy image output
        if socket.enabled:
            if socket.name!="Image":
                file_output_node.layer_slots.new(socket.name)
            else:
                # Leave the image output empty to get RGB values
                file_output_node.layer_slots.new("")
    file_output_node.layer_slots.new("atmo")
    # Connect the sockets between the two nodes
    for i, socket in enumerate([s for s in render_layers_node.outputs if s.enabled]):
            bpy.context.scene.node_tree.links.new(file_output_node.inputs[i], socket)
    return file_output_node

def copyAlpha(nodeA, nodeB):
    setAlphaNode = bpy.context.scene.node_tree.nodes.new(type="CompositorNodeSetAlpha")
    setAlphaNode.location.x = nodeA.location.x + 350
    setAlphaNode.location.y = nodeA.location.y - 200
    bpy.context.scene.node_tree.links.new(nodeA.outputs["Alpha"], setAlphaNode.inputs[1])
    bpy.context.scene.node_tree.links.new(nodeB.outputs["Image"], setAlphaNode.inputs[0])
    return setAlphaNode

def connectAtmo(nodeA, nodeB):
    bpy.context.scene.node_tree.links.new(nodeA.outputs["Image"], nodeB.inputs["atmo"])
    
scene = bpy.context.scene
scene.use_nodes = True

offset = 1000
fileBaseName = getFileBaseName()
                
CurrentViewLayerName = bpy.context.view_layer.name
     
#remove_compositor_nodes() 

ViewLayer_node = createCompositorNode(CurrentViewLayerName, 0, offset*0) 
EXR_node = setupMultiEXR(ViewLayer_node , fileBaseName)