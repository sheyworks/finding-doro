import bpy
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "battlefield_environment_fbx")
os.makedirs(OUT, exist_ok=True)

COLORS = {
    "concrete": (0.43,0.50,0.52,1), "lightstone": (0.64,0.68,0.64,1),
    "darkstone": (0.22,0.27,0.29,1), "blue": (0.04,0.32,0.66,1),
    "cyan": (0.02,0.68,0.77,1), "red": (0.77,0.045,0.065,1),
    "orange": (0.97,0.31,0.035,1), "yellow": (0.99,0.69,0.035,1),
    "green": (0.20,0.47,0.16,1), "olive": (0.37,0.42,0.15,1),
    "sand": (0.67,0.52,0.29,1), "wood": (0.39,0.20,0.08,1),
    "darkwood": (0.19,0.095,0.035,1), "cream": (0.94,0.86,0.63,1),
    "pink": (0.85,0.09,0.38,1), "purple": (0.34,0.15,0.59,1),
    "grass": (0.25,0.62,0.18,1), "metal": (0.11,0.15,0.17,1),
}
MATS={}

def clear_scene():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    MATS.clear()
    for collection in (bpy.data.meshes,bpy.data.materials):
        for data in list(collection):
            if data.users==0: collection.remove(data)

def mat(key):
    if key in MATS: return MATS[key]
    rgba=COLORS[key]
    m=bpy.data.materials.new("M_Battle_"+key); m.diffuse_color=rgba; m.use_nodes=True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=rgba
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.86
    MATS[key]=m; return m

def cube(name,loc,dims,color,bevel=0.025,rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rotation: o.rotation_euler=rotation
    o.data.materials.append(mat(color))
    if bevel:
        mod=o.modifiers.new("Small edge bevel","BEVEL"); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def beam(name,a,b,width,depth,color,bevel=0.02):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cube_add(size=1,location=(a+b)*0.5)
    o=bpy.context.object; o.name=name; o.dimensions=(width,depth,d.length)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color))
    if bevel:
        mod=o.modifiers.new("Beam bevel","BEVEL"); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    o.rotation_mode="QUATERNION"; o.rotation_quaternion=Vector((0,0,1)).rotation_difference(d.normalized())
    bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def cylinder(name,loc,radius,depth,color,axis="Z",sides=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name
    if axis=="X": o.rotation_euler[1]=math.pi/2
    elif axis=="Y": o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.data.materials.append(mat(color)); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def ico(name,loc,scale,color):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color)); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def prism_flag(name,verts,color):
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],[(0,1,2,3),(3,2,1,0)]); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(mat(color))
    return o

def finish(name,builder):
    clear_scene(); builder()
    objects=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join(); obj=bpy.context.object; obj.name=name
    path=os.path.join(OUT,name.lower()+".fbx")
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,
        bake_space_transform=True,object_types={"MESH"},add_leaf_bones=False,
        mesh_smooth_type="OFF",path_mode="AUTO",axis_forward="-Z",axis_up="Y")
    tris=sum(len(p.vertices)-2 for p in obj.data.polygons)
    print("Exported",name,tris,"triangles",os.path.getsize(path),"bytes")

def large_wall():
    # Long, tall reusable fortification section; end posts align with matching modules.
    cube("Wall core",(0,0,2.25),(9.0,0.60,4.50),"concrete",0.06)
    cube("Wall base course",(0,0,0.36),(9.25,0.78,0.52),"darkstone",0.04)
    cube("Wall top cap",(0,0,4.48),(9.25,0.78,0.22),"lightstone",0.035)
    # Broad colored vertical panels make the wall readable in a toy battlefield.
    for i,x in enumerate((-3.35,-2.0,-0.65,0.7,2.05,3.4)):
        cube("Wall face panel",(x,-0.315,2.43),(1.10,0.055,3.48),"blue" if i%2==0 else "cyan",0.025)
    for x in (-4.15,-2.75,-1.35,0.05,1.45,2.85,4.15):
        cube("Wall top crenellation",(x,0,4.82),(0.55,0.74,0.50),"lightstone",0.035)

def wall_corner():
    # L corner with equal 5-stud runs and a stable, grounded footprint.
    cube("Corner wall X",(-1.20,0,2.1),(5.2,0.58,4.2),"concrete",0.05)
    cube("Corner wall Y",(0,1.20,2.1),(0.58,5.2,4.2),"concrete",0.05)
    cube("Corner base X",(-1.20,0,0.30),(5.35,0.74,0.48),"darkstone",0.035)
    cube("Corner base Y",(0,1.20,0.30),(0.74,5.35,0.48),"darkstone",0.035)
    for x in (-3.2,-1.8,-0.4): cube("Blue corner panel",(x,-0.31,2.15),(1.05,0.055,3.35),"blue",0.02)
    for y in (-0.4,1.0,2.4): cube("Cyan corner panel",(0.31,y,2.15),(0.055,1.05,3.35),"cyan",0.02)
    for x in (-3.4,-2.0,-0.6): cube("Corner crenel X",(x,0,4.4),(0.55,0.72,0.48),"lightstone",0.03)
    for y in (-0.6,0.8,2.2): cube("Corner crenel Y",(0,y,4.4),(0.72,0.55,0.48),"lightstone",0.03)

def breached_wall():
    # Ruined gate module with a broad, walkable breach through the center.
    for x in (-3.2,3.2):
        cube("Broken side pier",(x,0,2.7),(3.4,0.65,5.4),"concrete",0.055)
        cube("Pier foot",(x,0,0.28),(3.55,0.82,0.45),"darkstone",0.035)
    # Broken top fragments stop short of the opening, leaving 4.4m clear width.
    cube("Broken lintel left",(-2.48,0,5.18),(1.5,0.68,0.42),"lightstone",0.045,
         (0,math.radians(-8),math.radians(-4)))
    cube("Broken lintel right",(2.48,0,5.12),(1.5,0.68,0.52),"lightstone",0.045,
         (0,math.radians(9),math.radians(3)))
    # Chunky debris sits beside the opening, not across the path.
    for i,(x,y,z,s) in enumerate(((-1.9,-0.68,0.25,0.45),(-2.25,-0.20,0.34,0.58),
                                  (2.0,-0.48,0.28,0.52),(2.32,0.08,0.38,0.62))):
        cube("Breach rubble",(x,y,z),(s,s*0.8,s*0.65),"darkstone",0.03,
             (math.radians(i*7),math.radians(i*9),math.radians(i*13)))

def open_gazebo():
    # Fully open sides, wide access on all sides, no interior walls or benches.
    cube("Gazebo floor",(0,0,0.18),(6.0,6.0,0.36),"wood",0.045)
    for x in (-2.55,2.55):
        for y in (-2.55,2.55):
            cube("Gazebo column base",(x,y,0.48),(0.48,0.48,0.24),"blue",0.025)
            cube("Gazebo column",(x,y,2.45),(0.28,0.28,3.75),"cream",0.025)
            cube("Gazebo capital",(x,y,4.38),(0.48,0.48,0.18),"red",0.02)
    cube("Gazebo roof ring",(0,0,4.50),(6.0,6.0,0.25),"red",0.035)
    # Low-poly hip roof from four broad sloped beams, open interior beneath.
    beam("Roof slope front",(-3.05,-3.05,4.60),(0,0,5.75),0.16,0.16,"orange",0.02)
    beam("Roof slope back",(-3.05,3.05,4.60),(0,0,5.75),0.16,0.16,"orange",0.02)
    beam("Roof slope left",(-3.05,-3.05,4.60),(0,0,5.75),0.16,0.16,"yellow",0.02)
    beam("Roof slope right",(3.05,-3.05,4.60),(0,0,5.75),0.16,0.16,"yellow",0.02)
    # Roof cover as a chunky square cap and four pitched panels leaves all sides walkable.
    cube("Gazebo roof cap",(0,0,5.42),(1.15,1.15,0.32),"yellow",0.03)
    for side in (-1,1):
        # eave-to-cap strips along each roof face
        beam("Roof face X",(side*2.95,0,4.66),(side*0.42,0,5.42),0.12,5.85,"orange",0.015)
        beam("Roof face Y",(0,side*2.95,4.66),(0,side*0.42,5.42),5.85,0.12,"red",0.015)

def watchtower():
    # Tall observation platform with an open center and an attached ladder.
    for x in (-1.45,1.45):
        for y in (-1.45,1.45):
            beam("Watchtower support",(x*1.30,y*1.30,0),(x,y,4.25),0.22,0.22,"blue",0.025)
    cube("Watchtower platform",(0,0,4.15),(3.35,3.35,0.30),"yellow",0.04)
    for x in (-1.42,1.42):
        cube("Tower rail post",(x,-1.42,4.85),(0.13,0.13,1.25),"red",0.02)
        cube("Tower side rail",(x,0,5.38),(0.13,2.85,0.14),"cyan",0.02)
    cube("Tower rear rail",(0,1.42,5.38),(2.85,0.13,0.14),"cyan",0.02)
    for x in (-0.52,0.52): beam("Watchtower ladder rail",(x,-1.95,0),(x,-1.95,4.0),0.105,0.105,"orange",0.014)
    for i in range(13): cube("Watchtower ladder rung",(0,-1.95,0.22+i*0.29),(1.08,0.10,0.075),"yellow",0.01)

def sandbag_cover():
    # Low three-course serpentine cover that units can see and shoot over.
    colors=("sand","olive","cream")
    for row in range(3):
        z=0.25+row*0.43
        for col in range(5):
            x=-2.0+col*1.0+(0.48 if row%2 else 0)
            if x>2.15: continue
            cube("Sandbag",(x,0,z),(1.02,0.58,0.43),colors[(col+row)%3],0.105,
                 (math.radians((col%2)*3),0,math.radians((-1)**col*2)))

def crate_stack():
    # Reusable stack of chunky supply crates with simple crossed face braces.
    positions=[(-0.82,0.0,0.55),(0.0,0.0,0.55),(0.82,0.0,0.55),
               (-0.41,0.0,1.62),(0.41,0.0,1.62),(0.0,0.0,2.69)]
    for i,(x,y,z) in enumerate(positions):
        c="wood" if i%2==0 else "darkwood"
        cube("Supply crate",(x,y,z),(0.92,0.92,0.92),c,0.045)
        # Front braces as raised slats.
        beam("Crate brace A",(x-0.33,-0.475,z-0.33),(x+0.33,-0.475,z+0.33),0.075,0.05,"cream",0.01)
        beam("Crate brace B",(x-0.33,-0.48,z+0.33),(x+0.33,-0.48,z-0.33),0.075,0.05,"cream",0.01)

def rubble_pile():
    # Loose debris cluster that can be scattered as a small cover/detail prop.
    pieces=[(-0.85,-0.1,0.38,(0.95,0.8,0.72)),(0.0,0.0,0.43,(1.0,0.85,0.82)),
            (0.85,0.05,0.32,(0.75,0.72,0.62)),(-0.35,0.45,0.93,(0.70,0.65,0.68)),
            (0.55,0.42,0.82,(0.82,0.70,0.60)),(0.0,-0.42,1.12,(0.52,0.58,0.62))]
    for i,(x,y,z,s) in enumerate(pieces):
        cube("Concrete rubble",(x,y,z),s,"lightstone" if i%2 else "concrete",0.045,
             (math.radians(i*9),math.radians(i*13),math.radians(i*17)))
    ico("Loose rock left",(-1.15,0.38,0.25),(0.48,0.40,0.32),"darkstone")
    ico("Loose rock right",(1.1,-0.34,0.28),(0.42,0.38,0.30),"darkstone")

def capture_flag():
    # Neutral capture-point marker with a double-sided, triangular team flag.
    cube("Flag base",(0,0,0.16),(1.1,1.1,0.32),"darkstone",0.045)
    cylinder("Flag pole",(0,0,2.0),0.055,3.65,"yellow","Z",8)
    ico("Flag finial",(0,0,3.9),(0.12,0.12,0.16),"red")
    prism_flag("Blue triangular flag",[(0,-0.04,3.72),(1.35,-0.04,3.28),(0,-0.04,2.82),
                                       (0,0.04,3.72),(1.35,0.04,3.28),(0,0.04,2.82)],"blue")

new_assets=[
    ("Battle_Wall_Large",large_wall),
    ("Battle_Wall_Corner",wall_corner),
    ("Battle_Wall_Breach",breached_wall),
    ("Battle_Open_Gazebo",open_gazebo),
    ("Battle_Watchtower",watchtower),
    ("Battle_Sandbag_Cover",sandbag_cover),
    ("Battle_Crate_Stack",crate_stack),
    ("Battle_Rubble_Pile",rubble_pile),
    ("Battle_Capture_Flag",capture_flag),
]
for name,builder in new_assets:
    finish(name,builder)
