import bpy
import math
import os

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,"battle_ground_fbx")
os.makedirs(OUT,exist_ok=True)

COLORS={
    "soil":(0.30,0.18,0.09,1),"grass":(0.24,0.67,0.20,1),"grass_light":(0.39,0.79,0.25,1),
    "dirt":(0.48,0.29,0.13,1),"dirt_light":(0.61,0.39,0.19,1),"concrete":(0.48,0.54,0.55,1),
    "concrete_light":(0.65,0.69,0.68,1),"crack":(0.19,0.23,0.24,1),"stone":(0.38,0.43,0.43,1),
    "stone_dark":(0.25,0.29,0.30,1),"sand":(0.68,0.49,0.24,1),"yellow":(0.91,0.65,0.12,1),
}
MATS={}

def clear():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    MATS.clear()
    for coll in (bpy.data.meshes,bpy.data.materials):
        for data in list(coll):
            if data.users==0: coll.remove(data)

def mat(key):
    if key in MATS: return MATS[key]
    c=COLORS[key]; m=bpy.data.materials.new("M_Ground_"+key); m.diffuse_color=c; m.use_nodes=True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=c
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=0.9
    MATS[key]=m; return m

def cube(name,loc,dims,color,bevel=0,rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rotation: o.rotation_euler=rotation
    o.data.materials.append(mat(color))
    if bevel:
        mod=o.modifiers.new("Ground detail bevel","BEVEL"); mod.width=bevel; mod.segments=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def ico(name,loc,scale,color):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color)); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def tiled_box(name,size,side_color,top_color,thickness=0.4):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,thickness/2))
    o=bpy.context.object; o.name=name; o.dimensions=(size,size,thickness)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(side_color)); o.data.materials.append(mat(top_color))
    for poly in o.data.polygons:
        if poly.normal.z>0.5: poly.material_index=1
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o

def mesh_object(name,verts,faces,materials,face_mats=None):
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj)
    for m in materials: mesh.materials.append(mat(m))
    if face_mats:
        for poly,index in zip(mesh.polygons,face_mats): poly.material_index=index
    return obj

def base_arena():
    tiled_box("Battle grass arena base",32,"soil","grass",0.6)
    # Subtle dry patches at opposite corners break up the large green surface.
    for x,y in ((-11,-10),(10,10)):
        cube("Dry grass patch",(x,y,0.605),(5.0,3.0,0.015),"grass_light",0.02,
             (0,0,math.radians(18)))

def grass_tile():
    tiled_box("Grass ground tile",8,"soil","grass")
    # Small, flat clover patches stay away from the tile edges for seamless placement.
    for x,y in ((-2.1,-1.8),(1.6,2.0),(-0.4,2.6),(2.4,-2.3)):
        cube("Grass color patch",(x,y,0.405),(0.75,0.55,0.012),"grass_light",0.008,
             (0,0,math.radians((x-y)*9)))

def dirt_tile():
    tiled_box("Dirt path tile",8,"soil","dirt")
    for x,y,s in ((-2.8,-1.5,0.25),(-1.4,2.4,0.18),(1.1,-2.5,0.22),(2.5,1.3,0.28),
                  (0.2,0.5,0.15)):
        ico("Path pebble",(x,y,0.415),(s,s*0.72,0.035),"dirt_light")

def concrete_tile():
    tiled_box("Concrete ground tile",8,"stone_dark","concrete")
    # Four broad plates with thin recessed-looking seams.
    for x in (-2.0,2.0): cube("Concrete seam X",(x,0,0.407),(0.045,8,0.014),"crack",0)
    for y in (-2.0,2.0): cube("Concrete seam Y",(0,y,0.407),(8,0.045,0.014),"crack",0)
    # A couple of short angular cracks, not a noisy all-over texture.
    cube("Concrete crack 1",(-1.0,-0.5,0.412),(1.25,0.035,0.018),"crack",0,
         (0,0,math.radians(28)))
    cube("Concrete crack 2",(-0.54,0.0,0.412),(0.82,0.03,0.018),"crack",0,
         (0,0,math.radians(-54)))

def rubble_tile():
    tiled_box("Rubble ground tile",8,"stone_dark","stone")
    pieces=[(-3.0,-2.8,0.18,(0.72,0.54,0.28)),(-2.7,2.5,0.18,(0.8,0.55,0.32)),
            (3.05,2.3,0.18,(0.62,0.64,0.26)),(2.8,-2.6,0.18,(0.75,0.58,0.30)),
            (-3.1,0.2,0.16,(0.55,0.42,0.22)),(3.0,-0.1,0.15,(0.48,0.5,0.24))]
    for i,(x,y,z,s) in enumerate(pieces):
        cube("Rubble ground chunk",(x,y,z),(s[0],s[1],s[2]),"concrete_light" if i%2 else "concrete",0.035,
             (math.radians(i*7),math.radians(i*11),math.radians(i*19)))
    # Keep center open so characters can cross the tile.
    for x,y in ((-1.4,2.8),(1.8,-2.6),(2.6,1.1)):
        ico("Loose ground rock",(x,y,0.46),(0.20,0.17,0.12),"stone_dark")

def crater_tile():
    tiled_box("Crater ground tile",8,"soil","dirt")
    # Low polygon earthen impact rim around a flat, walkable center.
    sides=12; center=(0,0); verts=[]
    rings=[(1.20,0.415),(1.52,0.46),(1.92,0.82),(2.28,0.70),(2.62,0.415)]
    for radius,z in rings:
        for i in range(sides):
            angle=2*math.pi*i/sides
            jitter=1.0+0.045*math.sin(i*4+1)
            verts.append((radius*jitter*math.cos(angle),radius*jitter*math.sin(angle),z))
    faces=[]; mats=[]
    for r in range(len(rings)-1):
        for i in range(sides):
            a=r*sides+i; b=r*sides+(i+1)%sides
            c=(r+1)*sides+(i+1)%sides; d=(r+1)*sides+i
            faces.append((a,b,c,d)); mats.append(0 if r<2 else 1)
    mesh_object("Crater raised rim",verts,faces,["dirt","sand"],mats)
    # A few chips sit on the rim, leaving the center clear and walkable.
    for i in (1,4,8,10):
        angle=2*math.pi*i/sides
        x,y=2.0*math.cos(angle),2.0*math.sin(angle)
        ico("Crater rim chip",(x,y,0.82),(0.28,0.20,0.13),"stone_dark")

def export(name,builder):
    clear(); builder()
    objs=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join(); obj=bpy.context.object; obj.name=name
    path=os.path.join(OUT,name.lower()+".fbx")
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,
        bake_space_transform=True,object_types={"MESH"},add_leaf_bones=False,
        mesh_smooth_type="OFF",path_mode="AUTO",axis_forward="-Z",axis_up="Y")
    tris=sum(len(p.vertices)-2 for p in obj.data.polygons)
    print("Exported",name,tris,"triangles",os.path.getsize(path),"bytes")

for name,builder in [
    ("Ground_Battle_Base",base_arena),
    ("Ground_Grass_Tile",grass_tile),
    ("Ground_Dirt_Tile",dirt_tile),
    ("Ground_Concrete_Tile",concrete_tile),
    ("Ground_Rubble_Tile",rubble_tile),
    ("Ground_Crater_Tile",crater_tile),
]: export(name,builder)
