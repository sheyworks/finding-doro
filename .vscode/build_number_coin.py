import bpy
import math
import os

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,"number_coin_fbx")
os.makedirs(OUT,exist_ok=True)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj,do_unlink=True)

COLORS={
    "gold":(1.0,0.57,0.035,1),"gold_light":(1.0,0.82,0.16,1),
    "cyan":(0.025,0.58,0.78,1),"navy":(0.025,0.09,0.16,1),
    "cream":(1.0,0.95,0.69,1),
}
MATS={}

def mat(key):
    if key in MATS: return MATS[key]
    rgba=COLORS[key]
    m=bpy.data.materials.new("M_Coin_"+key); m.diffuse_color=rgba; m.use_nodes=True
    bsdf=m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value=rgba
    bsdf.inputs["Metallic"].default_value=0.55 if key.startswith("gold") else 0.18
    bsdf.inputs["Roughness"].default_value=0.4
    MATS[key]=m; return m

def cylinder(name,loc,radius,depth,color,sides=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.data.materials.append(mat(color)); return o

def ico(name,loc,scale,color):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color)); return o

def block(name,loc,dims,color,bevel=0.003):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color))
    if bevel:
        mod=o.modifiers.new("Tiny numeral bevel","BEVEL"); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

# Thick, faceted gold coin with a cyan inlay on both faces.
cylinder("Coin gold body",(0,0,0),0.43,0.11,"gold",12)
cylinder("Front cyan medallion",(0,-0.057,0),0.335,0.018,"cyan",12)
cylinder("Back cyan medallion",(0,0.057,0),0.335,0.018,"cyan",12)
cylinder("Front inset ring",(0,-0.069,0),0.286,0.009,"gold_light",12)
cylinder("Front center inset",(0,-0.075,0),0.266,0.008,"cyan",12)
cylinder("Back inset ring",(0,0.069,0),0.286,0.009,"gold_light",12)
cylinder("Back center inset",(0,0.075,0),0.266,0.008,"cyan",12)

# Twelve low-poly studs around the front rim.
for i in range(12):
    a=2*math.pi*i/12
    ico("Rim stud",(0.375*math.cos(a),-0.081,0.375*math.sin(a)),
        (0.025,0.014,0.025),"gold_light")

# Raised blocky number 3 made from five simple bars for low triangle count.
for z in (0.15,0,-0.15): block("Number 3 horizontal",(0,-0.086,z),(0.23,0.018,0.045),"gold_light")
for z in (0.075,-0.075): block("Number 3 right bar",(0.092,-0.086,z),(0.046,0.018,0.12),"gold_light")

# Three small raised dashes on the reverse face.
for i,x in enumerate((-0.085,0,0.085)):
    o=ico("Back face dot",(x,0.083,0),(0.034,0.009,0.11),"gold_light")
    o.rotation_euler[1]=math.radians((i-1)*22)

bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
bpy.ops.object.join()
coin=bpy.context.object; coin.name="Number_Coin"
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
path=os.path.join(OUT,"number_coin.fbx")
bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,
    bake_space_transform=True,object_types={"MESH"},add_leaf_bones=False,
    mesh_smooth_type="OFF",path_mode="AUTO",axis_forward="-Z",axis_up="Y")
triangles=sum(len(p.vertices)-2 for p in coin.data.polygons)
print("Exported Number Coin",triangles,"triangles",os.path.getsize(path),"bytes")
