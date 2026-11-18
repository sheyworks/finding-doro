import bpy
import math
import os
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "number_blocks_fbx")
os.makedirs(OUT, exist_ok=True)

COLORS = {
    "red": (0.78, 0.045, 0.075, 1), "orange": (1.0, 0.31, 0.035, 1),
    "yellow": (0.88, 0.72, 0.035, 1), "green": (0.09, 0.48, 0.19, 1),
    "blue": (0.015, 0.48, 0.77, 1), "purple": (0.32, 0.19, 0.59, 1),
    "pink": (0.83, 0.055, 0.39, 1), "gray": (0.43, 0.52, 0.59, 1),
    "white": (0.96, 0.96, 0.9, 1), "black": (0.025, 0.025, 0.03, 1),
    "iris": (0.035, 0.27, 0.5, 1), "mouth": (0.12, 0.025, 0.055, 1),
    "tooth": (1.0, 0.95, 0.79, 1), "darkred": (0.37, 0.025, 0.045, 1),
    "darkgreen": (0.035, 0.24, 0.095, 1), "darkblue": (0.015, 0.24, 0.43, 1),
    "darkpink": (0.43, 0.02, 0.19, 1), "gold": (1.0, 0.59, 0.035, 1),
    "evil_red": (0.38,0.018,0.04,1), "evil_orange": (0.44,0.105,0.018,1),
    "evil_yellow": (0.48,0.36,0.012,1), "evil_green": (0.025,0.24,0.065,1),
    "evil_blue": (0.008,0.22,0.39,1), "evil_purple": (0.17,0.08,0.32,1),
    "evil_pink": (0.43,0.018,0.17,1), "evil_gray": (0.20,0.25,0.28,1),
    "crack": (0.018,0.012,0.02,1), "evil_iris": (0.82,0.018,0.025,1),
    "evil_mouth": (0.035,0.008,0.014,1),
    "evil_rainbow_0": (0.20,0.018,0.25,1), "evil_rainbow_1": (0.012,0.095,0.31,1),
    "evil_rainbow_2": (0.015,0.25,0.08,1), "evil_rainbow_3": (0.38,0.28,0.008,1),
    "evil_rainbow_4": (0.42,0.12,0.008,1), "evil_rainbow_5": (0.31,0.012,0.025,1),
}
RAINBOW = [(0.42,0.05,0.5,1),(0.04,0.25,0.78,1),(0.05,0.62,0.28,1),
           (0.96,0.79,0.025,1),(1.0,0.38,0.025,1),(0.78,0.035,0.07,1)]
MATS = {}

def mat(key, rgba=None):
    if key in MATS: return MATS[key]
    c = rgba if rgba else COLORS[key]
    m = bpy.data.materials.new("M_" + key)
    m.diffuse_color = c
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = c
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.78
    MATS[key] = m
    return m

def cube(name, loc, scale, material, bevel=0.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat(material) if isinstance(material, str) else mat(name, material))
    if bevel:
        mod = o.modifiers.new("Tiny edge chamfers", "BEVEL"); mod.width = bevel; mod.segments = 1
        mod.profile = 0.5
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def ico(name, loc, scale, material, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat(material) if isinstance(material, str) else mat(name, material))
    return o

def panel(name, x, z, w, h, color, depth=0.025):
    return cube(name, (x, -0.515, z), (w, depth, h), color, min(0.015, depth/2))

def eye(x, z, size=0.12, iris="iris", side=""):
    ico("Eye white"+side, (x,-0.255,z), (size,size*0.44,size*1.12), "white", 2)
    ico("Iris"+side, (x,-0.292,z), (size*0.53,size*0.26,size*0.62), iris, 1)
    ico("Pupil"+side, (x,-0.313,z), (size*0.25,size*0.13,size*0.33), "black", 1)

def face(cx, cz, eye_gap=0.24, eye_size=0.115, smile=0.23, iris="iris", googly=False, evil=False):
    for s, dx in (("L",-eye_gap/2),("R",eye_gap/2)):
        if googly:
            ico("Eye stalk base", (cx+dx,-0.235,cz+0.02), (0.075,0.07,0.07), "crack" if evil else "darkred", 1)
        eye(cx+dx,cz,eye_size,"evil_iris" if evil else iris,s)
        if evil:
            brow = cube("Angry brow"+s,(cx+dx,-0.275,cz+eye_size*1.35),
                        (eye_size*1.75,0.045,0.055),"crack",0.012)
            brow.rotation_euler[1] = 0.30 if s=="L" else -0.30
    if evil:
        cube("Snarl", (cx,-0.235,cz-0.28), (smile,0.035,0.14), "evil_mouth", 0.012)
        for side in (-1,1):
            fang = cube("Fang",(cx+side*smile*0.30,-0.26,cz-0.24),
                        (0.055,0.025,0.09),"tooth",0.008)
            fang.rotation_euler[1] = side*0.18
    else:
        cube("Open smiling mouth", (cx,-0.235,cz-0.28), (smile,0.03,0.17), "mouth", 0.012)
        cube("Teeth", (cx,-0.258,cz-0.235), (smile*0.55,0.012,0.045), "tooth", 0.006)

def crack_line(x1,z1,x2,z2):
    dx,dz=x2-x1,z2-z1
    o=cube("Jagged body crack",((x1+x2)/2,-0.226,(z1+z2)/2),
           (math.sqrt(dx*dx+dz*dz),0.025,0.026),"crack",0.003)
    o.rotation_euler[1]=-math.atan2(dz,dx)

def arm(x, z, side, color, length=0.38, angle=0.0, radius=0.085):
    # Low-poly, short tapered-looking limb assembled from a single beveled block and hand.
    a = cube("Arm_"+side, (x,-0.02,z), (radius*1.55,0.16,length), color, radius*0.55)
    a.rotation_euler[1] = angle
    ico("Hand_"+side, (x + (0.06 if side=="R" else -0.06),-0.025,z-length*0.45), (radius*1.0,0.11,radius*0.9), color, 1)

def leg(x, z, side, color, length=0.36):
    cube("Leg_"+side, (x,-0.025,z-length/2), (0.11,0.14,length), color, 0.025)
    ico("Foot_"+side, (x,-0.045,z-length), (0.075,0.10,0.06), color, 1)

def leg_spacing(width):
    return min(0.23, max(0.17, width*0.40))

def make_character(n, color, rows, cols, style="normal", evil=False):
    # Body is a rounded voxel assembly; seams read as number-block divisions.
    cell = 0.48
    w, h = cols*cell, rows*cell
    zc = h/2 + 0.28
    base = "evil_"+color if evil else color
    for r in range(rows):
        for c in range(cols):
            if style == "rainbow":
                ri=min(rows-1-r,len(RAINBOW)-1)
                co = "evil_rainbow_%d"%ri if evil else RAINBOW[ri]
            else: co = None
            x = (c-(cols-1)/2)*cell
            z = 0.28 + (r+0.5)*cell
            cube("Block_%d_%d"%(r+1,c+1),(x,0,z),(cell*0.985,0.42,cell*0.985),co or base,0.055)
    # Facial features centered on the front, on the upper part of the body.
    face_z = 0.28 + h*0.67
    if n == 10:
        face_z = 0.28 + h*0.84
    eye_gap = min(0.27, w*0.47)
    eye_size = min(0.12, w*0.2)
    face(0, face_z, eye_gap, eye_size, min(0.26,w*0.52), iris="iris", googly=(n in (1,6,8)), evil=evil)
    if evil:
        # Sharp zig-zag scars along the front edges keep the number silhouette readable.
        crack_line(-w*0.43,0.28+h*0.24,-w*0.25,0.28+h*0.34)
        crack_line(-w*0.25,0.28+h*0.34,-w*0.37,0.28+h*0.44)
        crack_line(w*0.43,0.28+h*0.74,w*0.25,0.28+h*0.65)
        crack_line(w*0.25,0.28+h*0.65,w*0.36,0.28+h*0.55)
    # Limbs and silhouette-specific accents.
    side_z = max(0.42, h*0.46)
    limb_color = base if n not in (7,10) else ("evil_red" if evil else "red")
    if n in (4,6,8,9):
        arm(-w/2-0.09, side_z, "L", limb_color, 0.38, -0.58)
        arm(w/2+0.09, side_z, "R", limb_color, 0.38, 0.58)
    else:
        arm(-w/2-0.10, side_z, "L", limb_color, 0.34, -0.7)
        arm(w/2+0.10, side_z, "R", limb_color, 0.34, 0.7)
    offset = leg_spacing(w)
    leg(-offset,0.29,"L",limb_color,0.30)
    leg(offset,0.29,"R",limb_color,0.30)
    if n == 3:
        # Small three-point crown.
        for i,xx in enumerate((-0.19,0,0.19)):
            ico("Crown jewel", (xx,-0.02,0.28+h+0.10), (0.075,0.07,0.14), ("evil_red" if evil else "red") if i!=1 else ("evil_yellow" if evil else "gold"), 1)
    if n == 7:
        # Tiny antenna tuft.
        ico("Top tuft", (0,-0.015,0.28+h+0.10), (0.10,0.10,0.10), "evil_purple" if evil else "purple", 1)
    if n == 8:
        # Curled side tentacles approximated by short low-poly beads.
        for side in (-1,1):
            for i in range(3):
                zz=0.42+i*0.34
                ico("Curl joint", (side*(w/2+0.21),-0.02,zz), (0.12,0.12,0.13), "evil_pink" if evil else "darkpink", 1)
                ico("Curl tip", (side*(w/2+0.30),-0.02,zz-0.11), (0.09,0.09,0.10), "evil_pink" if evil else "darkpink", 1)
    if n == 9:
        # Square glasses.
        for x in (-0.15,0.15):
            cube("Glasses rim",(x,-0.235,face_z),(0.23,0.04,0.28),"evil_blue" if evil else "darkblue",0.035)
            cube("Glasses lens",(x,-0.263,face_z),(0.16,0.025,0.20),"white",0.025)
            ico("Glasses pupil",(x,-0.283,face_z),(0.043,0.02,0.065),"black",1)
        cube("Glasses bridge",(0,-0.246,face_z),(0.09,0.04,0.05),"evil_blue" if evil else "darkblue",0.015)
    if n == 10:
        # Number Ten's slim red body with visible stacked section bars.
        for i in range(1,10):
            zz=0.28+h*i/10
            cube("Section seam",(0,-0.218,zz),(0.38,0.025,0.018),"crack" if evil else "darkred",0.006)
    # all objects currently in scene will be exported as one character

def clean_scene():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    MATS.clear()
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                       bpy.data.armatures, bpy.data.actions):
        for block in list(datablocks):
            if block.users == 0: datablocks.remove(block)

def add_walk_rig(mesh, number, width, height, shoulder_z):
    arm_data = bpy.data.armatures.new("Number_%02d_Rig" % number)
    rig = bpy.data.objects.new("Number_%02d_Rig" % number, arm_data)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bones = {}
    root = arm_data.edit_bones.new("Root")
    root.head = (0,0,0); root.tail = (0,0,0.28)
    body = arm_data.edit_bones.new("Body")
    body.head = (0,0,0.28); body.tail = (0,0,0.28+height)
    body.parent = root; body.use_connect = True
    for side, sign in (("L",-1),("R",1)):
        arm_b = arm_data.edit_bones.new("Arm."+side)
        arm_b.head = (sign*width/2,0,shoulder_z)
        arm_b.tail = (sign*(width/2+0.34),0,shoulder_z-0.34)
        arm_b.parent = body
        leg_b = arm_data.edit_bones.new("Leg."+side)
        leg_b.head = (sign*leg_spacing(width),0,0.28)
        leg_b.tail = (sign*leg_spacing(width),0,-0.10)
        leg_b.parent = body
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.select_set(False)

    groups = {name: mesh.vertex_groups.new(name=name) for name in
              ("Body","Arm.L","Arm.R","Leg.L","Leg.R")}
    half_w = width/2
    for vert in mesh.data.vertices:
        x, y, z = vert.co
        group = "Body"
        if abs(x) > half_w + 0.005 and z >= 0.25:
            group = "Arm." + ("R" if x > 0 else "L")
        elif z < 0.28 and abs(x) <= half_w + 0.005:
            group = "Leg." + ("R" if x > 0 else "L")
        groups[group].add([vert.index], 1.0, 'REPLACE')
    deform = mesh.modifiers.new("Character Rig", 'ARMATURE')
    deform.object = rig
    mesh.parent = rig

    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    mesh.select_set(False)
    bpy.ops.object.mode_set(mode='POSE')
    for name in ("Arm.L","Arm.R","Leg.L","Leg.R","Root"):
        rig.pose.bones[name].rotation_mode = 'XYZ'
    rig.animation_data_create()
    action = bpy.data.actions.new("Number_%02d_WalkCycle" % number)
    rig.animation_data.action = action
    frames = (1,7,13,19,25)
    phases = (0.42,0.0,-0.42,0.0,0.42)
    for frame, phase in zip(frames, phases):
        rig.pose.bones["Arm.L"].rotation_euler[2] = phase
        rig.pose.bones["Arm.R"].rotation_euler[2] = -phase
        rig.pose.bones["Leg.L"].rotation_euler[2] = -phase * 0.78
        rig.pose.bones["Leg.R"].rotation_euler[2] = phase * 0.78
        rig.pose.bones["Root"].location.z = 0.025 if frame in (7,19) else 0.0
        for bone_name in ("Arm.L","Arm.R","Leg.L","Leg.R"):
            rig.pose.bones[bone_name].keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
        rig.pose.bones["Root"].keyframe_insert(data_path="location", frame=frame, group="Root")
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 25
    bpy.context.scene.render.fps = 24
    return rig

specs = [
    (1,"red",1,1,"normal"),(2,"orange",2,1,"normal"),(3,"yellow",3,1,"normal"),
    (4,"green",2,2,"normal"),(5,"blue",5,1,"normal"),(6,"purple",3,2,"normal"),
    (7,"red",6,1,"rainbow"),(8,"pink",4,2,"normal"),(9,"gray",3,3,"normal"),
    (10,"red",10,1,"normal")
]

for n,color,rows,cols,style in specs:
    clean_scene()
    make_character(n,color,rows,cols,style)
    height, width = rows*0.48, cols*0.48
    shoulder_z = max(0.42, height*0.46)
    # Join the low-poly pieces into one skinned mesh, then bind each limb to its own bone.
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name="Number_%02d"%n
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    rig = add_walk_rig(obj, n, width, height, shoulder_z)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,"number_%02d.fbx"%n),
        use_selection=True, apply_unit_scale=True, bake_space_transform=True,
        object_types={'MESH','ARMATURE'}, add_leaf_bones=False, mesh_smooth_type='OFF',
        bake_anim=True,
        path_mode='AUTO', axis_forward='-Z', axis_up='Y')
    print("Exported",n,"faces",sum(len(p.vertices)-2 for p in obj.data.polygons),
          "size",os.path.getsize(os.path.join(OUT,"number_%02d.fbx"%n)))

# Separate enemy set: same proportions and walk rig, with dark materials and body scars.
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ugly_number_fbx")
os.makedirs(OUT, exist_ok=True)
for n,color,rows,cols,style in specs:
    clean_scene()
    make_character(n,color,rows,cols,style,evil=True)
    height, width = rows*0.48, cols*0.48
    shoulder_z = max(0.42, height*0.46)
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name="Ugly_Number_%02d"%n
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    rig = add_walk_rig(obj, n, width, height, shoulder_z)
    rig.name = "Ugly_Number_%02d_Rig"%n
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    path=os.path.join(OUT,"ugly_number_%02d.fbx"%n)
    bpy.ops.export_scene.fbx(filepath=path,
        use_selection=True, apply_unit_scale=True, bake_space_transform=True,
        object_types={'MESH','ARMATURE'}, add_leaf_bones=False, mesh_smooth_type='OFF',
        bake_anim=True,
        path_mode='AUTO', axis_forward='-Z', axis_up='Y')
    print("Exported enemy",n,"faces",sum(len(p.vertices)-2 for p in obj.data.polygons),
          "size",os.path.getsize(path))
