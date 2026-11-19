import bpy, math, os
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'closed_house_fbx')
os.makedirs(OUT, exist_ok=True)

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = 0.82
    return m

wall = mat('Warm_Cream_Plaster', (0.91, 0.69, 0.39))
roof = mat('Terracotta_Roof', (0.72, 0.12, 0.075))
roof_hi = mat('Roof_Sunlit_Tiles', (0.94, 0.27, 0.13))
stone = mat('Foundation_Stone', (0.38, 0.43, 0.44))
stone_hi = mat('Stone_Light', (0.56, 0.59, 0.53))
trim = mat('Window_Trim_Cream', (0.97, 0.83, 0.57))
glass = mat('Window_Teal_Glass', (0.08, 0.63, 0.73))
wood = mat('Window_Mullion', (0.44, 0.19, 0.10))

def cube(name, loc, scale, material, bevel=0.0, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rot: o.rotation_euler=rot
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft_Block_Edges','BEVEL'); mod.width=bevel; mod.segments=1
        o.modifiers.new('Weighted_Corner_Normals','WEIGHTED_NORMAL')
    return o

# A fully enclosed pentagonal-prism house shell, with solid front and rear walls.
verts=[(-2,-1.5,0),(2,-1.5,0),(2,1.5,0),(-2,1.5,0),
       (-2,-1.5,2.35),(2,-1.5,2.35),(0,-1.5,3.35),
       (2,1.5,2.35),(-2,1.5,2.35),(0,1.5,3.35)]
faces=[(0,1,2,3), (0,4,5,1), (1,5,7,2), (2,7,8,3), (3,8,4,0),
       (4,6,5), (8,9,6,4), (5,6,9,7), (7,9,8)]
mesh=bpy.data.meshes.new('Enclosed_House_Shell_Mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(wall)
shell=bpy.data.objects.new('Closed_House_Shell_No_Door',mesh); bpy.context.collection.objects.link(shell)

# Roof boards: two solid, low-poly slabs meeting at the ridge.
angle=math.atan2(1.0,2.0)
sloped_len=math.sqrt(2.0**2+1.0**2)+0.28
for side in (-1,1):
    x=side*1.0; z=2.85
    rot=(0, side*angle, 0)
    cube('Roof_Left_Slab' if side<0 else 'Roof_Right_Slab',(x,0,z),(sloped_len,3.35,0.18),roof,0.035,rot)

# Chunky low-poly ridge cap and short chimney.
cube('Roof_Ridge_Cap',(0,0,3.39),(0.26,3.38,0.22),roof_hi,0.035)
cube('Chimney_Brick',(1.08,0.65,3.5),(0.48,0.52,1.0),stone,0.035)
cube('Chimney_Top',(1.08,0.65,4.02),(0.60,0.62,0.14),wall,0.025)

# Foundation ring and chunky corner quoins, leaving the body fully sealed.
cube('Stone_Foundation',(0,0,0.18),(4.18,3.18,0.36),stone,0.055)
for y in (-1.60,1.60):
    for x in (-1.54,0,1.54):
        cube('Foundation_Block',(x,y,0.30),(0.90,0.20,0.25),stone_hi if x==0 else stone,0.035)

# Decorative, sealed windows sit on the outside face; there is no doorway or opening.
for x in (-0.98,0.98):
    cube('Window_Outer_Trim',(x,-1.565,1.38),(0.78,0.14,0.98),trim,0.035)
    cube('Window_Closed_Glass',(x,-1.648,1.40),(0.58,0.07,0.76),glass,0.025)
    cube('Window_Vertical_Mullion',(x,-1.695,1.40),(0.075,0.035,0.76),wood,0.01)
    cube('Window_Horizontal_Mullion',(x,-1.695,1.40),(0.58,0.035,0.075),wood,0.01)

# One compact raised eave trim adds a readable game-asset silhouette.
cube('Front_Eave_Trim',(0,-1.63,2.37),(4.08,0.15,0.16),roof_hi,0.025)

# Set origin-friendly transform and export as one compact FBX with named parts.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'closed_lowpoly_house.fbx'), use_selection=True,
    apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
    object_types={'MESH'}, mesh_smooth_type='OFF', use_mesh_modifiers=True,
    path_mode='COPY', embed_textures=True, bake_space_transform=False)
tris=sum(len(p.vertices)-2 for o in bpy.context.scene.objects if o.type=='MESH' for p in o.data.polygons)
print('Exported Closed House: %d triangles' % tris)
