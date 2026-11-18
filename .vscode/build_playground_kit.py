import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "playground_environment_fbx")
os.makedirs(OUT, exist_ok=True)

PALETTE = {
    "grass": (0.22,0.70,0.25,1), "green": (0.10,0.55,0.20,1),
    "lime": (0.50,0.82,0.12,1), "red": (0.86,0.08,0.09,1),
    "orange": (1.0,0.34,0.035,1), "yellow": (1.0,0.77,0.035,1),
    "blue": (0.03,0.42,0.85,1), "cyan": (0.015,0.72,0.82,1),
    "purple": (0.38,0.20,0.69,1), "pink": (0.94,0.12,0.46,1),
    "cream": (0.96,0.88,0.64,1), "wood": (0.38,0.19,0.075,1),
    "dark": (0.07,0.09,0.13,1), "white": (0.93,0.97,0.96,1),
}
MATS = {}

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    MATS.clear()
    for datablocks in (bpy.data.meshes, bpy.data.materials):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

def material(key):
    if key in MATS:
        return MATS[key]
    rgba = PALETTE[key]
    mat = bpy.data.materials.new("M_Play_" + key)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.82
    MATS[key] = mat
    return mat

def cube(name, loc, dims, color, bevel=0.025, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        obj.rotation_euler = rotation
    obj.data.materials.append(material(color))
    if bevel:
        mod = obj.modifiers.new("Small safe edge bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj

def beam(name, a, b, width, depth, color, bevel=0.02):
    start, end = Vector(a), Vector(b)
    direction = end - start
    bpy.ops.mesh.primitive_cube_add(size=1, location=(start+end)*0.5)
    obj=bpy.context.object; obj.name=name
    obj.dimensions=(width,depth,direction.length)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(material(color))
    if bevel:
        mod=obj.modifiers.new("Small beam bevel","BEVEL"); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=obj; bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0,0,1)).rotation_difference(direction.normalized())
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj

def cylinder(name, loc, radius, depth, color, axis="Z", sides=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    if axis == "X": obj.rotation_euler[1] = math.pi/2
    elif axis == "Y": obj.rotation_euler[0] = math.pi/2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(material(color))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj

def ico(name, loc, scale, color):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc)
    obj=bpy.context.object; obj.name=name; obj.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material(color))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj

def pyramid_roof(name, half, z0, peak_z, color):
    verts=[(-half,-half,z0),(half,-half,z0),(half,half,z0),(-half,half,z0),(0,0,peak_z)]
    faces=[(0,3,2,1),(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    return obj

def export_asset(name, builder):
    clear_scene()
    builder()
    bpy.ops.object.select_all(action="SELECT")
    meshes=[o for o in bpy.context.selected_objects if o.type=="MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes: obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    bpy.ops.object.join()
    obj=bpy.context.object; obj.name=name
    path=os.path.join(OUT,name.lower()+".fbx")
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,
        bake_space_transform=True,object_types={"MESH"},add_leaf_bones=False,
        mesh_smooth_type="OFF",path_mode="AUTO",axis_forward="-Z",axis_up="Y")
    triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
    print("Exported",name,triangles,"triangles",os.path.getsize(path),"bytes")

def tower():
    # Raised square lookout with three open sides, four legs, ladder and a simple roof.
    for x in (-1.15,1.15):
        for y in (-1.15,1.15):
            cube("Tower post",(x,y,1.18),(0.20,0.20,2.36),"blue",0.025)
    cube("Tower platform",(0,0,2.38),(2.75,2.75,0.25),"yellow",0.035)
    # Back and side safety rails leave the front clear for the slide.
    for x in (-1.15,1.15):
        cube("Safety rail post",(x,0.95,2.95),(0.13,0.13,0.92),"red",0.018)
    cube("Back rail",(0,0.95,3.30),(2.45,0.13,0.14),"red",0.02)
    for side in (-1,1):
        cube("Side rail upper",(side*1.17,-0.05,3.30),(0.13,1.95,0.14),"cyan",0.02)
        cube("Side rail lower",(side*1.17,-0.05,2.90),(0.13,1.95,0.10),"cyan",0.015)
    # Bright pyramid roof.
    pyramid_roof("Red pyramid roof",1.55,3.65,4.55,"red")
    cube("Roof trim",(0,0,3.66),(3.15,3.15,0.10),"orange",0.02)
    # Simple front ladder centered at y=-1.55.
    for x in (-0.52,0.52):
        beam("Ladder side",(x,-1.54,0.0),(x,-1.54,2.28),0.11,0.11,"orange",0.015)
    for i in range(7):
        z=0.30+i*0.31
        cube("Ladder rung",(0,-1.54,z),(1.10,0.105,0.09),"yellow",0.012)

def slide():
    # Standalone slide module: raised landing, inclined chute, side lips and side ladder.
    top=(-1.0,2.20); bottom=(2.05,0.36)
    angle=-math.atan2(top[1]-bottom[1],bottom[0]-top[0])
    mid_y=(top[0]+bottom[0])/2; mid_z=(top[1]+bottom[1])/2
    length=math.sqrt((bottom[0]-top[0])**2+(bottom[1]-top[1])**2)
    cube("Slide chute",(0,mid_y,mid_z),(0.78,length,0.14),"cyan",0.045)
    for x in (-0.43,0.43):
        cube("Slide raised lip",(x,mid_y,mid_z+0.12),(0.09,length,0.28),"blue",0.025,
             (angle,0,0))
    # landing step/platform at the tall end
    cube("Slide platform",(0,-1.20,2.28),(1.25,0.65,0.22),"yellow",0.025)
    for x in (-0.52,0.52):
        beam("Slide ladder rail",(x,-1.28,0),(x,-1.28,2.17),0.09,0.09,"red",0.015)
    for i in range(7):
        z=0.25+i*0.30
        cube("Slide ladder rung",(0,-1.28,z),(1.08,0.09,0.075),"orange",0.01)

def swing_set():
    # Freestanding A-frame with two fixed seats and simple low-poly hanging rods.
    for x in (-1.75,1.75):
        for y,sign in ((-0.82,-1),(0.82,1)):
            beam("Swing frame leg",(x+sign*0.70,y,0),(x,0,3.15),0.15,0.15,"blue",0.02)
        cube("A frame foot",(x,0,0.09),(1.70,1.95,0.18),"yellow",0.025)
    beam("Swing top beam",(-1.82,0,3.15),(1.82,0,3.15),0.20,0.20,"red",0.025)
    for sx in (-0.78,0.78):
        for xoff in (-0.18,0.18):
            cylinder("Swing hanger",(sx+xoff,0,1.80),0.035,2.50,"dark","Z",6)
        cube("Swing seat",(sx,0,0.52),(0.62,0.42,0.16),"green" if sx<0 else "orange",0.04)

def seesaw():
    # Static seesaw prop; the broad beam is level and ready to be animated in-game.
    beam("Seesaw beam",(-2.0,0,1.05),(2.0,0,1.05),0.22,0.22,"red",0.035)
    cylinder("Pivot axle",(0,0,1.05),0.23,0.48,"dark","X",8)
    # Triangular support body.
    verts=[(-0.48,-0.28,0.16),(0.48,-0.28,0.16),(0, -0.28,1.02),
           (-0.48,0.28,0.16),(0.48,0.28,0.16),(0,0.28,1.02)]
    faces=[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
    mesh=bpy.data.meshes.new("SeesawSupportMesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new("Seesaw triangular support",mesh); bpy.context.collection.objects.link(ob); ob.data.materials.append(material("yellow"))
    cube("Pivot base",(0,0,0.12),(1.25,0.90,0.24),"blue",0.035)
    for x in (-1.72,1.72):
        cube("Seesaw seat",(x,0,1.22),(0.62,0.72,0.18),"cyan" if x<0 else "pink",0.035)
        for side in (-1,1):
            cube("Seat handle",(x,side*0.27,1.47),(0.10,0.10,0.45),"orange",0.018)

def fence():
    # Modular three-stud fence section; end posts line up when placed side by side.
    length=3.0
    for x in (-length/2,length/2):
        cube("Fence end post",(x,0,0.66),(0.22,0.24,1.32),"blue",0.025)
    cube("Fence bottom rail",(0,0,0.28),(length,0.18,0.16),"orange",0.02)
    cube("Fence top rail",(0,0,1.14),(length,0.20,0.18),"red",0.025)
    colors=("yellow","green","cyan","pink","purple","orange")
    for i,x in enumerate((-1.22,-0.73,-0.24,0.24,0.73,1.22)):
        h=0.62 if i%2==0 else 0.78
        cube("Color block picket",(x,0,0.67),(0.35,0.22,h),colors[i],0.025)

def tree():
    # Small cubic tree for repeated placement around paths and play areas.
    cube("Tree trunk",(0,0,0.95),(0.42,0.42,1.90),"wood",0.035)
    cube("Trunk root base",(0,0,0.18),(0.85,0.78,0.36),"wood",0.045)
    ico("Lower foliage",(0,0,2.15),(0.90,0.80,0.80),"green")
    ico("Upper foliage L",(-0.48,0,2.72),(0.62,0.61,0.62),"lime")
    ico("Upper foliage R",(0.48,0.03,2.72),(0.62,0.61,0.62),"grass")
    ico("Top foliage",(0,0.02,3.18),(0.60,0.58,0.58),"green")

assets=[
    ("Play_Tower",tower),
    ("Play_Slide",slide),
    ("Play_Swing_Set",swing_set),
    ("Play_Seesaw",seesaw),
    ("Play_Block_Fence",fence),
    ("Play_Block_Tree",tree),
]
for asset_name,builder in assets:
    export_asset(asset_name,builder)
