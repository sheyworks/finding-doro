import bpy
import math
import os

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,"number_bullet_fbx")
os.makedirs(OUT,exist_ok=True)

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj,do_unlink=True)

PALETTE={
    "cyan":(0.035,0.72,0.86,1),
    "glow":(0.26,0.96,1.0,1),
    "yellow":(1.0,0.66,0.045,1),
    "dark":(0.08,0.13,0.17,1),
}
MATS={}

def mat(key):
    if key in MATS: return MATS[key]
    rgba=PALETTE[key]
    m=bpy.data.materials.new("M_Bullet_"+key); m.diffuse_color=rgba; m.use_nodes=True
    bsdf=m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value=rgba
    bsdf.inputs["Roughness"].default_value=0.48
    if key=="glow":
        bsdf.inputs["Emission Color"].default_value=rgba
        bsdf.inputs["Emission Strength"].default_value=0.5
    MATS[key]=m; return m

def cylinder(name,loc,radius,depth,color,sides=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=radius,depth=depth,location=loc)
    o=bpy.context.object; o.name=name; o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.data.materials.append(mat(color)); return o

def cube(name,loc,dims,color,bevel=0.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color))
    if bevel:
        mod=o.modifiers.new("Tiny bevel","BEVEL"); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

# Short energy slug, front tip points down local -Y to match the pistol muzzle.
cylinder("Cyan energy body",(0,-0.135,0),0.048,0.24,"cyan",8)
cylinder("Rear cap",(0,0.003,0),0.052,0.045,"dark",8)
cylinder("Tail ring",(0,-0.045,0),0.059,0.035,"yellow",8)
cylinder("Core stripe",(0,-0.145,0),0.052,0.12,"glow",8)
bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=0.053,radius2=0.0,depth=0.14,location=(0,-0.275,0))
tip=bpy.context.object; tip.name="Pointed energy nose"; tip.rotation_euler[0]=math.pi/2
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
tip.data.materials.append(mat("yellow"))

# Four tiny rear fins make the projectile easy to read in motion.
for i,angle in enumerate((0,math.pi/2,math.pi,3*math.pi/2)):
    x,z=math.cos(angle)*0.052,math.sin(angle)*0.052
    fin=cube("Tail fin %d"%(i+1),(x,0.035,z),(0.052,0.075,0.012),"yellow",0.003)
    fin.rotation_euler[1]=-angle

bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active=bpy.context.selected_objects[0]
bpy.ops.object.join()
bullet=bpy.context.object; bullet.name="Number_Bullet"
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
path=os.path.join(OUT,"number_bullet.fbx")
bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,
    bake_space_transform=True,object_types={"MESH"},add_leaf_bones=False,
    mesh_smooth_type="OFF",path_mode="AUTO",axis_forward="-Z",axis_up="Y")
triangles=sum(len(p.vertices)-2 for p in bullet.data.polygons)
print("Exported Number Bullet",triangles,"triangles",os.path.getsize(path),"bytes")
